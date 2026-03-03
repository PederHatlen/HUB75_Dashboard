"""
Requires a spotify developer app
You need to get a client_id, client_secret and a refresh_token

This is put into a json format file called spotify.secret
in the folder you run the program from. (./ from this file)

TO USE THIS PROGRAMM:
You need a Spotify developer app (https://developer.spotify.com/dashboard)
Get a refresh token, client id, and client secret
    The two last can be retrieved from the spotify app you have made
    You can get a refresh token by completing the Oauth2 initiation ritual
all these needs to be added to the json formated file "spotify.secret" in the root of the project (where the main.py file is)
    i.e. {"refresh_token":"TOKEN", "client_id":"ID", "client_secret":"SECRET"}
"""

import time, base64, json, requests, threading
from websockets.sync import server
from datetime import datetime as dt, timedelta as td

MS = td(milliseconds=1)
INTERVAL = td(seconds=2)

data = {"playing": False, "title": "", "artists": [], "album": "", "progress": 0, "duration": 10000, "cover_url": ""}
next_data = dt.now()
clients = set()

with open("./secrets.json", "r") as fi: spotifySecrets = json.load(fi)["spotify"]
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
        # print(f"Code retrieval: {raw}")
        token_runout = (dt.now() + td(seconds=raw["expires_in"] - 10))

        access_token = raw["access_token"]
    return access_token

def player_action(action):
    global next_data
    print(f"Spotify: Sending request {action}")
    method = "put" if action in ["play", "pause"] else "post"
    response = requests.request(method, f"https://api.spotify.com/v1/me/player/{action}", headers={'Authorization':f'Bearer {get_refresh_token()}'})
    if response.status_code == 200: next_data = dt.now()
    else: print(f"Spotify: Error sending to Spotify: {response.status_code} {response.reason}")

## SpotifyWS returns data: ##
# playing:    bool
# title:      str
# artists:    str
# album:      str
# progress:   int ms
# duration:   int ms
# time:       timestamp
# cover_url:  str url
# device:     {name: str, id: str, **etc.}

def digest(raw):
    global data
    try:
        if "device_mapping" in spotifySecrets and raw["device"]["id"] in spotifySecrets["device_mapping"]:
            raw["device"]["name"] = spotifySecrets["device_mapping"][raw["device"]["id"]]
        return {
            "playing": raw["is_playing"],
            "title": raw["item"]["name"],
            "artists": [a["name"] for a in raw["item"]["artists"] if a["type"] == "artist"],
            "album": raw["item"]["album"]["name"],
            "progress": raw["progress_ms"],
            "duration": raw["item"]["duration_ms"],
            "time": dt.now().timestamp(),
            "cover_url": raw["item"]["album"]["images"][0]["url"],
            "device": raw["device"]
        }
    except Exception as e:
        print(f"Spotify: It didn't want to be digested: {e}")
        data["playing"] = False
        return data

def get_data():
    global data
    try:
        response = requests.get("https://api.spotify.com/v1/me/player", headers={'Authorization':f'Bearer {get_refresh_token()}'})
        if response.status_code == 200: return digest(response.json())
    except Exception as e: print(f"Spotify: Error: {e}")
    data["playing"] = False
    return data

# Get new data from spotify
# every 2 seconds or if song ended
def threadedData(callback = ""):
    global data, next_data
    while True:
        try:
            if next_data < dt.now():
                old = {"playing": data["playing"], "title": data["title"], "artists": data["artists"]}
                data = get_data()

                change = data["playing"] != old["playing"] or data["title"] != old["title"] or data["artists"] != old["artists"]
                if change:
                    print(f"Spotify: NEW song: {data['title']} by {', '.join(data['artists'])} [{'playing' if data['playing'] else 'paused'} on {data['device']['name']} ({data['device']['id']})]")
                    for c in clients: c.send(json.dumps(data))
                    if callback != "": callback(data)
                next_data = dt.now() + min(INTERVAL, td(hours=data["playing"], milliseconds=100 + data["duration"] - data["progress"]))                    
        except Exception as E: print(f"Spotify: Error: {E}")
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
    print("Spotify: Starting Spotify runner")
    threading.Thread(name="SpotifyRunner", target=threadedData, daemon=True).start()
    print(f"Spotify: Starting WebSocket on port :{port}")
    threading.Thread(name="SpotifyWS", target=start_ws, args=(host, port), daemon=True).start()

if __name__ == "__main__":
    run(1338)
    try:input("Startup complete! Enter to quit...\n")
    except KeyboardInterrupt as E: print("Keyboard interrupt")
    print("Quitting!")