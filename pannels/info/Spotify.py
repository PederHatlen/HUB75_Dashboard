import requests, time, json, base64, datetime
from PIL import Image, ImageDraw, ImageEnhance
from functions import *


"""
TO USE THIS INTEGRATION:
You need a Spotify developer app (https://developer.spotify.com/dashboard)
Get a refresh token, client id, and client secret
    The two last can be retrieved from the spotify app you have made
    You can get a refresh token by completing the Oauth2 initiation ritual
all these needs to be added to the json file "spotifysecrets.json" in the root of the project (where the main.py file is)

"""

LOG_NEWDATA = False

small05 = font["small05"]
icons07 = font["icons07"]

spotifyColor = color["spotify"]
scrollSpeed = 0.5 # (pixel/50ms)

prev_dial_turn = 0

covers = {}
data = {"playing":False, "time":datetime.datetime.fromtimestamp(0), "data":{}}
oldTS = datetime.datetime.fromtimestamp(0)
needNewDataPLZ = False

MS = datetime.timedelta(milliseconds=1)

spotySecrets = {}

with open(f"{PATH}/spotifysecrets.json", "r") as fi:
    file = json.load(fi)
    spotySecrets["refresh_token"] = file["refresh_token"]
    spotySecrets["Authorization"] = base64.b64encode("".join([file["client_id"], ":", file["client_secret"]]).encode("ascii")).decode("ascii")

def getDaToken():
    if "runout" not in spotySecrets or spotySecrets["runout"] < datetime.datetime.now():
        body = {
            'grant_type':'refresh_token',
            'refresh_token':spotySecrets["refresh_token"]
        }
        headers = {
            'Authorization':f'Basic {spotySecrets["Authorization"]}',
            'Content-Type':'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", "https://accounts.spotify.com/api/token", data=body, headers=headers)
        spotySecrets["access_token"] = response.json()["access_token"]

        spotySecrets["runout"] = (datetime.datetime.now() + datetime.timedelta(seconds=response.json()["expires_in"] - 10))
    return spotySecrets["access_token"]

def get_data():
    global data, oldTS
    oldTS = datetime.datetime.now()
    try: response = requests.get("https://api.spotify.com/v1/me/player", headers={'Authorization':f'Bearer {getDaToken()}'})
    except requests.exceptions.ConnectionError:
        print("Couldnt connect to internet")
        data["playing"] = False
        return
    if response.status_code != 200:
        if LOG_NEWDATA: print("Not playing annything")
        data["playing"] = False
        return
    currentlyPlaying = response.json()
    # print(currentlyPlaying)
    data["playing"] = currentlyPlaying["is_playing"]
    data["data"] = currentlyPlaying
    data["time"] = datetime.datetime.now()
    if LOG_NEWDATA: print(f"Got new Spotify data [{'playing' if data['playing'] else 'paused'}]")

def next():
    global needNewDataPLZ
    response = requests.post("https://api.spotify.com/v1/me/player/next", headers={'Authorization':f'Bearer {getDaToken()}'})
    if response.status_code == 200: needNewDataPLZ = True
    else: print(f"Error: {response.status_code}")
def previous():
    global needNewDataPLZ
    response = requests.post("https://api.spotify.com/v1/me/player/previous", headers={'Authorization':f'Bearer {getDaToken()}'})
    if response.status_code == 200: needNewDataPLZ = True
    else: print(f"Error: {response.status_code}")
def play():
    response = requests.put("https://api.spotify.com/v1/me/player/play", headers={'Authorization':f'Bearer {getDaToken()}'})
    if response.status_code == 200: data["playing"] = True
    else: print(f"Error: {response.status_code}")
def pause():
    response = requests.put("https://api.spotify.com/v1/me/player/pause", headers={'Authorization':f'Bearer {getDaToken()}'})
    if response.status_code == 200: data["playing"] = False
    else: print(f"Error: {response.status_code}")

def btn(): (pause() if data["playing"] else play())

def dial(e):
    global prev_dial_turn
    if prev_dial_turn > datetime.datetime.now().timestamp() - 1: return
    prev_dial_turn = datetime.datetime.now().timestamp()
    
    if e == "1R": next()
    elif e == "1L": previous()

def threadedData():
    global data, oldTS, needNewDataPLZ
    while True:
        # Get new data from spotify (every 10 seconds) or (system sendt skip request) or (song just ended)
        delta = (datetime.datetime.now() - oldTS)
        # print(delta.seconds, oldTS)
        if delta.seconds > 2 or needNewDataPLZ or (data["playing"] and (data["data"]["progress_ms"]+(delta/MS)-100 >= data["data"]["item"]["duration_ms"])):
            get_data()
            needNewDataPLZ = False

        time.sleep(0.5)

def get(fn = 0):
    global data, covers

    im = Image.new(mode="RGB", size=(64, 32))

    # If you are not playing annything on spotify return black screen
    if data["data"] == {}:
        return PIL2frame(im)
    
    delta = (datetime.datetime.now() - data["time"])

    # Set localdata to stored data
    currentlyPlaying = data["data"]

    # get the cover url, and download it if not allready
    coverURL = currentlyPlaying["item"]["album"]["images"][0]["url"]
    if coverURL not in covers:
        covers[coverURL] = Image.open(requests.get(currentlyPlaying["item"]["album"]["images"][-1]["url"], stream=True).raw).resize((32,32), Image.Resampling.HAMMING)
        covers[coverURL] = ImageEnhance.Contrast(covers[coverURL]).enhance(1.25)
        if len(covers) > 20: del covers[list(covers.keys())[0]]
        print(f"There is now {len(covers)} saved covers.")

    infoArea = Image.new(mode="RGB", size=(30,30))
    info = ImageDraw.Draw(infoArea)
    info.fontmode = "1"

    titlelength = small05.getlength(f'{currentlyPlaying["item"]["name"]}    ')
    artists = "  -  ".join([e["name"] for e in currentlyPlaying["item"]["artists"]])
    artistlength = small05.getlength(f"{artists}    ")

    scrolLen = int(fn*scrollSpeed)

    if titlelength > 32: 
        textPos = (-int(scrolLen%(max(titlelength, 32))),0)
        info.text(textPos, "    ".join([currentlyPlaying["item"]["name"]]*3), font=small05, fill=(255,255,255))
    else:
        info.text((0,0), currentlyPlaying["item"]["name"], font=small05, fill="#fff")

    if artistlength > 32:
        textPos = (-int(scrolLen%(max(artistlength, 32))),8)
        info.text(textPos, f"{artists}    {artists}", font=small05, fill="#888")
    else:
        info.text((0,8), artists, font=small05, fill="#888")

    progress = ((currentlyPlaying["progress_ms"]+(delta/MS if data["playing"] else 0))/currentlyPlaying["item"]["duration_ms"])
    info.line([(0,29),(29,29)], fill="#fff", width=1)
    info.line([(0,29),(round(progress*30),29)], fill=spotifyColor, width=1)

    info.text((12, 20), text=("1" if data["playing"] else "0"), font=icons07, fill=spotifyColor)

    im.paste(covers[coverURL], (0,0))
    im.paste(infoArea, (33,1))
    # im.paste(corrected.enhance(1.25),(32,0))

    return im