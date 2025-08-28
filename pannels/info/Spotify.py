import functions, requests, time, base64, datetime
from PIL import Image, ImageDraw, ImageEnhance
from threading import Thread

import numpy as np
from sklearn.cluster import KMeans
from skimage.color import rgb2lab, lab2rgb

"""
TO USE THIS INTEGRATION:
You need a Spotify developer app (https://developer.spotify.com/dashboard)
Get a refresh token, client id, and client secret
    The two last can be retrieved from the spotify app you have made
    You can get a refresh token by completing the Oauth2 initiation ritual
all these needs to be added to the json file "secrets.json" in the root of the project (where the main.py file is)

"""

LOG_NEWDATA = False
GET_DATA_THREADED = True

small05 = functions.font["small05"]
icons07 = functions.font["icons07"]

spotifyColor = functions.color["spotify"]
scrollSpeed = 0.5 # (pixel/50ms)

prev_dial_turn = 0
fn = 0

covers = {}
coverURL = ""

data = {"playing":False, "time":datetime.datetime.fromtimestamp(0), "data":{}}
oldTS = datetime.datetime.fromtimestamp(0)
oldCover = ""
HAIsUpdated = False
needNewDataPLZ = False
albumColors = []
SWATCHSIZE = 3
PALETTESIZE = 5

MS = datetime.timedelta(milliseconds=1)

fullscreen = False

spotySecrets = functions.secrets["spotify"]
spotySecrets["Authorization"] = base64.b64encode("".join([spotySecrets["client_id"], ":", spotySecrets["client_secret"]]).encode("ascii")).decode("ascii")

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

def rgb2lum(rgb): return (0.2126*rgb[0] + 0.7152*rgb[1] + 0.0722*rgb[2])/255

def rgb_to_hsv(rgb):
    rgb = np.array(rgb) / 255.0
    return np.array(Image.fromarray((rgb[np.newaxis, np.newaxis, :] * 255).astype('uint8')).convert('HSV'))[0, 0] / 255.0

# Using K-Means to group into n- clusters of similar colors (default 3)
# Filtering out too dark/light and low saturated colors, if possible
# Using LAB colors for more even distribution
def get_palette(im, n_colors=4, sorting="none"):
    img = np.array(im.convert("RGB"))
    pixels = img.reshape((-1, 3))

    brightness_threshold=(0.2, 1)
    saturation_threshold=0.3

    filtered = np.array([color.tolist() for color in pixels 
                         if brightness_threshold[0] < rgb_to_hsv(color)[2] < brightness_threshold[1] 
                         and rgb_to_hsv(color)[1] > saturation_threshold])

    finalColorArr = filtered if (len(filtered) >= n_colors) else pixels
    pixels_lab = rgb2lab(finalColorArr.astype(np.float64) / 255.0)

    # Run KMeans
    kmeans = KMeans(n_clusters=n_colors, random_state=42)
    labels = kmeans.fit_predict(pixels_lab)

    centers_reshaped = kmeans.cluster_centers_[np.newaxis, :, :]
    palette = (lab2rgb(centers_reshaped)[0] * 255).astype(int)

    if sorting == "frequency": palette = palette[np.argsort(-np.bincount(labels))]                          # Sorting by cluster size
    elif sorting == "saturation": palette = palette[np.argsort([rgb_to_hsv(c)[1] for c in palette])]        # Sorting by saturation
    elif sorting == "lightness": palette = palette[np.argsort([-rgb2lum(c) for c in palette])]              # Sorting by luminance

    palette = palette.tolist()

    if len(filtered) < n_colors:
        print(f"Pixel count unchanged, Final palette: {palette}")
    else: print(f"Reduced pixel count by {((len(pixels)-len(filtered))/len(pixels))*100:.2f}% to {len(filtered)}, Final palette: {palette}")

    return palette

def get_data():
    global data, oldTS, albumColors, covers, coverURL, HAIsUpdated, oldCover
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
    
    # get the cover url, and download it if not allready
    tempCoverURL = currentlyPlaying["item"]["album"]["images"][0]["url"]
    if tempCoverURL not in covers:
        tempCover = Image.open(requests.get(currentlyPlaying["item"]["album"]["images"][1]["url"], stream=True).raw)
        covers[tempCoverURL] = {
            "small": ImageEnhance.Contrast(tempCover.resize((32,32), Image.Resampling.HAMMING)).enhance(1.25),
            "large": ImageEnhance.Contrast(tempCover.resize((64,64), Image.Resampling.HAMMING)).enhance(1.25)
        }
        if len(covers) > 20: del covers[list(covers.keys())[0]]
        print(f"There is now {len(covers)} saved covers.")

    if tempCoverURL != oldCover or (not data["playing"] and currentlyPlaying["is_playing"]):
        oldCover = tempCoverURL
        HAIsUpdated = False
        albumColors = get_palette(covers[tempCoverURL]["large"], PALETTESIZE, "lightness")
        Thread(target=(lambda: functions.sendImageToESP(covers[tempCoverURL]["large"]))).start()
        
    if not HAIsUpdated and functions.HASGetHelperStatus("do_follow_spotify"):
        HAIsUpdated = True
        Thread(target=functions.setHaColors, args=[get_palette(covers[tempCoverURL]["large"])]).start()
    
    # Making avaleable only when completely loaded
    coverURL = tempCoverURL
    
    if not currentlyPlaying["is_playing"]: Thread(target=functions.ESPScreen, args=["clear"]).start()
    
    # print(currentlyPlaying)
    data["playing"] = currentlyPlaying["is_playing"]
    data["data"] = currentlyPlaying
    data["time"] = datetime.datetime.now()
    if LOG_NEWDATA: print(f"Got new Spotify data [{'playing' if data['playing'] else 'paused'}]")

def next():
    global needNewDataPLZ
    response = requests.post("https://api.spotify.com/v1/me/player/next", headers={'Authorization':f'Bearer {getDaToken()}'})
    if response.status_code == 200: needNewDataPLZ = True
    else: print(f"Error sending to Spotify (next): {response.status_code}")
def previous():
    global needNewDataPLZ
    response = requests.post("https://api.spotify.com/v1/me/player/previous", headers={'Authorization':f'Bearer {getDaToken()}'})
    if response.status_code == 200: needNewDataPLZ = True
    else: print(f"Error sending to Spotify (previous): {response.status_code}")
def play():
    response = requests.put("https://api.spotify.com/v1/me/player/play", headers={'Authorization':f'Bearer {getDaToken()}'})
    if response.status_code == 200: data["playing"] = True
    else: print(f"Error sending to Spotify (play): {response.status_code}")
def pause():
    response = requests.put("https://api.spotify.com/v1/me/player/pause", headers={'Authorization':f'Bearer {getDaToken()}'})
    if response.status_code == 200: data["playing"] = False
    else: print(f"Error sending to Spotify (pause): {response.status_code}")

def btn(): (pause() if data["playing"] else play())

def dial(e):
    global prev_dial_turn, fullscreen
    if prev_dial_turn > datetime.datetime.now().timestamp() - 1: return
    prev_dial_turn = datetime.datetime.now().timestamp()

    if e == "1R": next()
    elif e == "1L": previous()
    # elif e[0] == "0": fullscreen = not fullscreen

def threadedData():
    global data, oldTS, needNewDataPLZ
    while True:
        try:
            if not GET_DATA_THREADED and not needNewDataPLZ:
                time.sleep(2)
                continue
            # Get new data from spotify (every 2 seconds) or (system sendt skip request) or (song just ended)
            delta = (datetime.datetime.now() - oldTS)
            # print(delta.seconds, oldTS)
            if delta.seconds > 2 or needNewDataPLZ or (data["playing"] and (data["data"]["progress_ms"]+(delta/MS)-100 >= data["data"]["item"]["duration_ms"])):
                get_data()
                needNewDataPLZ = False
        except Exception as E:
            print(f"Error while trying to get Spotify Status: {E}\n...Retrying after 2 seconds")
            time.sleep(1.5)
        time.sleep(0.5)

spotifyRunner = Thread(target=threadedData, name="SpotifyRunner", daemon=True)
spotifyRunner.start()

def get():
    global data, fn, oldTS, needNewDataPLZ, albumColors, coverURL
    fn +=1

    im = Image.new(mode="RGB", size=(functions.WIDTH, functions.HEIGHT))

    # If you are not playing annything on spotify return black screen
    if data["data"] == {}: return im

    if not GET_DATA_THREADED and (datetime.datetime.now() - oldTS).seconds > 2:
        needNewDataPLZ = True

    delta = (datetime.datetime.now() - data["time"])

    # Set localdata to stored data
    currentlyPlaying = data["data"]

    infoArea = Image.new(mode="RGB", size=(30,30))
    info = ImageDraw.Draw(infoArea)
    info.fontmode = "1"

    titlelength = small05.getlength(f'{currentlyPlaying["item"]["name"]}    ')
    artists = "  -  ".join([e["name"] for e in currentlyPlaying["item"]["artists"]])
    artistlength = small05.getlength(f"{artists}    ")

    scrolLen = (fn//2)

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

    for i in range(len(albumColors)): info.rectangle(((i*SWATCHSIZE+i, 15), (i*SWATCHSIZE+i+SWATCHSIZE-1,15+SWATCHSIZE-1)), fill=functions.rgb2hex(albumColors[i]))

    im.paste(covers[coverURL]["small"], (0,0))
    im.paste(infoArea, (33,1))
    # im.paste(corrected.enhance(1.25),(32,0))

    return im
