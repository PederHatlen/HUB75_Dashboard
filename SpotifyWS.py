import time, base64, json, requests, threading
from websockets.sync import server
from datetime import datetime as dt, timedelta as td

MS = td(milliseconds=1)
INTERVAL = td(seconds=2)

data = {"playing": False, "title": "", "artists": [], "album": "", "progress": 0, "duration": 10000, "cover_url": ""}
next_data = dt.now()
clients = set()

with open("./spotify.secret", "r") as fi: spotifySecrets = json.load(fi)
authorization = base64.b64encode("".join([spotifySecrets["client_id"], ":", spotifySecrets["client_secret"]]).encode("ascii")).decode("ascii")
token_runout = dt.now()
access_token = ""

def get_refresh_token():
    global access_token, token_runout
    if token_runout < dt.now():
        body = {'grant_type':'refresh_token','refresh_token':spotifySecrets["refresh_token"]}
        headers = {'Authorization':f'Basic {authorization}','Content-Type':'application/x-www-form-urlencoded'}
        response = requests.request("POST", "https://accounts.spotify.com/api/token", data=body, headers=headers)
        raw = response.json()
        if response.status_code != 200: raise Exception("Didn't get an auth code")
        print(f"Code retrieval: {raw}")
        token_runout = (dt.now() + td(seconds=raw["expires_in"] - 10))

        access_token = raw["access_token"]
    return access_token

def player_action(action):
    global next_data
    print(f"Sending request {action}")
    method = "put" if action in ["play", "pause"] else "post"
    response = requests.request(method, f"https://api.spotify.com/v1/me/player/{action}", headers={'Authorization':f'Bearer {get_refresh_token()}'})
    if response.status_code == 200: next_data = dt.now()
    else: print(f"Error sending to Spotify: {response.status_code} {response.reason}")

## SpotifyWS data: ##
# playing:    bool
# title:      str
# artists:    str
# album:      str
# progress:   int ms
# duration:   int ms
# time:       timestamp
# cover_url:  str url

def digest(raw):
    global data
    try:
        return {
            "playing": raw["is_playing"],
            "title": raw["item"]["name"],
            "artists": [a["name"] for a in raw["item"]["artists"] if a["type"] == "artist"],
            "album": raw["item"]["album"]["name"],
            "progress": raw["progress_ms"],
            "duration": raw["item"]["duration_ms"],
            "time": dt.now().timestamp(),
            "cover_url": raw["item"]["album"]["images"][0]["url"]
        }
    except Exception as e:
        print(f"It didn't want to be digested: {e}")
        data["playing"] = False
        return data

def get_data():
    global data
    try:
        response = requests.get("https://api.spotify.com/v1/me/player", headers={'Authorization':f'Bearer {get_refresh_token()}'})
        if response.status_code == 200: return digest(response.json())
    except Exception as e: print(f"Error: {e}")
    data["playing"] = False
    return data

# Get new data from spotify
# every 2 seconds or if song ended
def threadedData():
    global data, next_data
    while True:
        try:
            if next_data < dt.now():
                old, data = data, get_data()

                state_change = data["playing"] != old["playing"]
                song_change  = (data["title"] != old["title"] or data["artists"] != old["artists"])

                if state_change or song_change:
                    print(f"NEW song: {data['title']}, {'[playing]' if data['playing'] else '[paused]'}")
                    for c in clients: c.send(json.dumps(data))
                next_data = dt.now() + min(INTERVAL, td(hours=data["playing"], milliseconds=100 + data["duration"] - data["progress"]))                    
        except Exception as E: print(f"Error: {E}")
        time.sleep(0.25)

def handler(ws):
    global clients, data
    clients.add(ws)
    ws.send(json.dumps(data))
    try:
        for m in ws:
            print(m)
            if m in ["next", "previous", "play", "pause"] and not ((data["playing"] and m=="play") or (not data["playing"] and m=="pause")):
                player_action(m)
    finally: clients.remove(ws)

def start_ws(host, port):
    with server.serve(handler, host, port) as s: s.serve_forever()
    
def run(port, host="0.0.0.0"):
    print("Starting Spotify runner")
    threading.Thread(name="SpotifyRunner", target=threadedData, daemon=True).start()
    print("Starting web server")
    threading.Thread(name="SpotifyWS", target=start_ws, args=(host, port), daemon=True).start()

if __name__ == "__main__":
    run(1338)
    input("Startup complete! Enter to quit...\n")