import properties, requests, time, json, traceback
from PIL import Image, ImageDraw, ImageEnhance
from threading import Thread
from datetime import datetime as dt, timedelta as td
from websockets.sync.client import connect

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

G = properties.color_rgb["spotify"]
B, F, H = (0,0,0,0), [*G, 255], [*G, 127]
pauseIcon = properties.imFromArr([[F,F,B,F,F],[F,F,B,F,F],[F,F,B,F,F],[F,F,B,F,F],[F,F,B,F,F]], "RGBA")
playIcon  = properties.imFromArr([[F,H,B,B,B],[F,F,F,H,B],[F,F,F,F,F],[F,F,F,H,B],[F,H,B,B,B]], "RGBA")

prev_dial_turn = 0
fn = 0
ws = ""
data = {}

covers = {}
albumColors = []
HAIsUpdated = False

SWATCH_X, SWATCH_Y, SWATCH_PAD = 3, 3, 3
PALETTESIZE = len(properties.secrets["has"]["light_ids"])

ha_data = {}
def ha_data_interface(interface):
    global ha_data
    ha_data = interface

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

    bright_max, sat_max = (0.2, 1), 0.3
    filtered = [color.tolist() for color in pixels if bright_max[0] < rgb_to_hsv(color)[2] < bright_max[1] and rgb_to_hsv(color)[1] > sat_max]

    finalColorArr = np.array(filtered) if (len(filtered) >= n_colors) else pixels
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

    if len(filtered) < n_colors: print(f"Pixel count unchanged, Final palette: {palette}")
    else: print(f"Reduced pixel count by {((len(pixels)-len(filtered))/len(pixels))*100:.2f}% to {len(filtered)}, Final palette: {palette}")

    return palette

## SpotifyWS data: ##
# playing:    bool
# title:      str
# artists:    str
# album:      str
# progress:   int ms
# duration:   int ms
# time:  timestamp
# cover_url:  str url

def setHaColors(colors, transition = 1):
    complete = ["has" in properties.secrets, "access_token" in properties.secrets["has"], "light_ids" in properties.secrets["has"], "ip" in properties.secrets["has"]]
    if not all(complete): return False
    try:
        headers = {"Authorization": f"Bearer {properties.secrets['has']['access_token']}","content-type": "application/json",}
        for i in range(len(properties.secrets['has']['light_ids'])):
            data = {"entity_id":properties.secrets['has']['light_ids'][i], "rgb_color":colors[i%len(colors)], "transition": transition}
            resp = requests.post(f"http://{properties.secrets['has']['ip']}/api/services/light/turn_on", headers=headers, json=data)
            print(f"Setting {data['entity_id']} to {data['rgb_color']}")
            if resp.status_code != 200: print(f"Error {resp.status_code}")
    except Exception as E: print(f"Couldn't set colors with HAS: {E}")

def process_data(new_data):
    global covers, data, HAIsUpdated, albumColors
    if new_data["title"] == "" and new_data["artists"] == [] and new_data["cover_url"] == "": return print("Nothing playing")

    # get the cover url, and download it if not allready
    if new_data["cover_url"] not in covers:
        tempCover = Image.open(requests.get(new_data["cover_url"], stream=True).raw)
        covers[new_data["cover_url"]] = ImageEnhance.Contrast(tempCover.resize((32,32), Image.Resampling.HAMMING)).enhance(1.25)
        if len(covers) > 20: del covers[list(covers.keys())[0]]
        print(f"There is now {len(covers)} saved covers.")

    if "cover_url" not in data or new_data["cover_url"] != data["cover_url"]:
        albumColors = get_palette(covers[new_data["cover_url"]], PALETTESIZE, "lightness")
        HAIsUpdated = False

    new_data["time"] = dt.fromtimestamp(new_data["time"])
    data = new_data

def data_thread():
    global data, ws
    while True:
        try:
            ws = connect("ws://localhost:1338")
            print("Connected to WebSocket")
            while True: process_data(json.loads(ws.recv()))
        except Exception as e: print(f"Disconnected from spotify WS... trying to reconnect in 5s {traceback.format_exc()}")
        time.sleep(5)

def btn(): (ws.send("pause" if data["playing"] else "play"))

def dial(e):
    global prev_dial_turn, fullscreen
    if prev_dial_turn > dt.now().timestamp() - 1: return
    prev_dial_turn = dt.now().timestamp()

    if e == "1R": ws.send("next")
    elif e == "1L": ws.send("previous")

SpotifyRunner = Thread(target=data_thread, name="SpotifyRunner", daemon=True)
SpotifyRunner.start()

def get():
    global data, fn, albumColors, coverURL, HAIsUpdated
    fn +=1

    im, _ = properties.getBlankIM()

    # If you are not playing annything on spotify return black screen
    if data == {}: return im
    
    if not HAIsUpdated and data["playing"] and ha_data["spotify_lighting"]:
        HAIsUpdated = True
        Thread(target=setHaColors, args=[albumColors]).start()

    infoArea = Image.new(mode="RGB", size=(30,30))
    info = ImageDraw.Draw(infoArea)
    info.font = properties.font[5]

    titlelength = info.font.getlength(f'{data["title"]}    ')
    artists = "  -  ".join(data["artists"])
    artistlength = info.font.getlength(f"{artists}    ")

    scrolLen = (fn//2)

    if titlelength > 32:
        textPos = (-int(scrolLen%(max(titlelength, 32))),0)
        info.text(textPos, "    ".join([data["title"]]*3), fill=(255,255,255))
    else: info.text((0,0), data["title"], fill="#fff")

    if artistlength > 32:
        textPos = (-int(scrolLen%(max(artistlength, 32))),8)
        info.text(textPos, f"{artists}    {artists}", fill="#888")
    else: info.text((0,8), artists, fill="#888")

    progress = data["progress"] + (dt.now() - data["time"])/td(milliseconds=1) if data["playing"] else 0
    info.line([(0,29),(29,29)], fill="#fff", width=1)
    info.line([(0,29),(round((progress/data["duration"])*30),29)], fill=properties.color["spotify"], width=1)

    icon = pauseIcon if data["playing"] else playIcon
    infoArea.paste(icon, (12, 21), mask=icon)

    for i in range(len(albumColors)):
        x, y = i*(SWATCH_X + SWATCH_PAD) + 1, 15
        info.rectangle(((x, y), (x+SWATCH_X-1, y+SWATCH_Y-1)), fill=tuple(albumColors[i]))

    im.paste(covers[data["cover_url"]], (0,0))
    im.paste(infoArea, (33,1))

    return im
