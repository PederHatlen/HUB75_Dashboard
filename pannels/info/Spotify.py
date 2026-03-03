import properties, requests, time, json, traceback
from PIL import Image, ImageDraw, ImageEnhance
from threading import Thread
from datetime import datetime as dt, timedelta as td
from websockets.sync.client import connect
from math import ceil

import numpy as np
from sklearn.cluster import KMeans
from skimage.color import rgb2lab, lab2rgb

"""
TO USE THIS INTEGRATION:

You need a Spotify developer app (https://developer.spotify.com/dashboard)
Get a refresh token, client id, and client secret
    The two last can be retrieved from the spotify app you have made
    You can get a refresh token by completing the Oauth2 initiation ritual

All these needs to be added to the json file "secrets.json" in the root of the project (where the main.py file is)
    i.e.: {"refresh_token":"TOKEN", "client_id":"ID", "client_secret":"SECRET"}
Placed in the root of this project (same folder as main.py)
To add custom names for the devices (other than generic "iPhone" or [hostname])
    add:  "device_mapping": {[deviceid]: [name]}

USING THE WS:

There is three different posibilities for using the socket.
They are chosen by setting the SPOTIFY_SOCKET variable to either of these
    host:[PORT] - Hosts a WS, accessible for other programs as well
    [ADDRESS]   - Address to socket
    local       - Runs the SpotifyWS locally without exposing a WS

If it is unset or set to False, the pannel will not be loaded.

DATA FROM SpotifyWS:

    playing:    bool
    title:      str
    artists:    str
    album:      str
    progress:   int ms
    duration:   int ms
    time:       timestamp
    cover_url:  str url
    device:     {id: str, name: str, etc... }

"""

SPOTIFY_SOCKET = "host:1338"
SWATCH = (3, 3, 3) # X, Y, Padding

prev_dial_turn, ws = 0, ""
data, covers, albumColors = {}, {}, []
HAIsUpdated = False

def rgb2lum(rgb): return (0.2126*rgb[0] + 0.7152*rgb[1] + 0.0722*rgb[2])/255
def rgb_to_hsv(rgb):
    rgb = np.array(rgb) / 255.0
    return np.array(Image.fromarray((rgb[np.newaxis, np.newaxis, :] * 255).astype('uint8')).convert('HSV'))[0, 0] / 255.0

# Using K-Means to group into n- clusters of similar colors (default 3)
# Filtering out too dark/light and low saturated colors, if possible
# Using LAB colors for more even distribution
def get_palette(im, n_colors=5, sorting="none"):
    if n_colors < 1: n_colors = 5
    
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
    return palette

def setHaColors(colors, transition = 1):
    complete = ["has" in properties.secrets,"access_token" in properties.secrets["has"],"ip" in properties.secrets["has"],"spotify_lights" in properties.ha]
    if not all(complete): return False
    try:
        success = True
        headers = {"Authorization": f"Bearer {properties.secrets['has']['access_token']}","content-type": "application/json",}
        for i in range(len(properties.ha["spotify_lights"])):
            # print(properties.ha["spotify_lights"][i])
            data = {"entity_id":properties.ha["spotify_lights"][i], "rgb_color":colors[i%len(colors)], "transition": transition, "effect":"Solid"}
            resp = requests.post(f"http://{properties.secrets['has']['ip']}/api/services/light/turn_on", headers=headers, json=data)
            if resp.status_code != 200:
                print(f"HAColor: Error {resp.status_code}")
                success = False
        if success: print(f"HAColor: Successfully set HA colors")
    except Exception as E: print(f"HAColor: Couldn't set colors with HAS: {E}")

def process_data(new_data):
    global covers, data, HAIsUpdated, albumColors
    if new_data["title"] == "" and new_data["artists"] == [] and new_data["cover_url"] == "": return # print("Nothing playing")
    if SpotifyWS == "": print(f"Spotify: playing: {new_data['title']} by {', '.join(new_data['artists'])}")

    # get the cover url, and download it if not allready
    if new_data["cover_url"] not in covers:
        temp_im = ImageEnhance.Contrast(Image.open(requests.get(new_data["cover_url"], stream=True).raw)).enhance(1.5)
        covers[new_data["cover_url"]] = ImageEnhance.Brightness(temp_im.resize((32,32), Image.Resampling.HAMMING)).enhance(0.9)
        if len(covers) > 20: del covers[list(covers.keys())[0]]

    if "cover_url" not in data or new_data["cover_url"] != data["cover_url"]:
        albumColors = get_palette(covers[new_data["cover_url"]], 5 if "spotify_lights" not in properties.ha else len(properties.ha["spotify_lights"]), "lightness")
        HAIsUpdated = False

    new_data["time"] = dt.fromtimestamp(new_data["time"])
    data = new_data
    properties.data["spotify_data"] = data

def data_thread(host):
    global ws
    while True:
        try:
            ws = connect(f"ws://{host}")
            print("Spotify: Connected to WebSocket")
            while True: process_data(json.loads(ws.recv()))
        except Exception as e: print(f"Spotify: Disconnected from spotify WS... trying to reconnect in 5s {traceback.format_exc()}")
        time.sleep(5)

SpotifyWS = ""
if SPOTIFY_SOCKET == False or SPOTIFY_SOCKET == "":
    raise Exception("socket is not set-up (See config in ./pannels/info/Spotify.py)")
elif SPOTIFY_SOCKET.lower() == "local":
    import SpotifyWS
    Thread(target=SpotifyWS.threadedData, name="SpotifyRunner", args=[process_data], daemon=True).start()
else:
    host = SPOTIFY_SOCKET
    if SPOTIFY_SOCKET.split(":")[0].lower() == "host":
        import SpotifyWS
        SpotifyWS.run(int(SPOTIFY_SOCKET.split(":")[-1]))
        host = f"localhost:{SPOTIFY_SOCKET.split(':')[-1]}"
    Thread(target=data_thread, name="SpotifyRunner", args=[host], daemon=True).start()

def btn():
    global SpotifyWS
    if SpotifyWS != "": SpotifyWS.player_action("pause" if data["playing"] else "play")

def dial(e):
    global prev_dial_turn, fullscreen, ws, SpotifyWS
    if prev_dial_turn > dt.now().timestamp() - 1 or (ws == "" and SpotifyWS == "") or e[0] != "1": return

    prev_dial_turn = dt.now().timestamp()

    action = "next" if e[1] == "R" else "previous"
    if SpotifyWS != "": SpotifyWS.player_action(action)
    else: ws.send(action)

class scrollingText():
    def __init__(self, d, x, y, color = "#FFF", center = False):
        self.d, self.pos, self.y, self.color, self.center, self.drawframe = d, x, y, color, center, True
    def draw(self, text):
        self.drawframe = not self.drawframe
        textlen = ceil(self.d.font.getlength(text))
        if textlen <= self.d.im.size[0]: self.pos = 0 if not self.center else int((self.d.im.size[0]-textlen)/2) +1
        elif self.pos < 1-textlen - 6:   self.pos = 0
        else:
            if self.drawframe: self.pos -= 1
            self.d.text((self.pos + textlen + 6, self.y), text, fill=self.color)
        self.d.text((self.pos, self.y), text, fill=self.color)

im, _ = properties.getBlankIM()

infoArea = Image.new(mode="RGB", size=(30,30))
info = ImageDraw.Draw(infoArea)
info.font = properties.font[5]

title_text  = scrollingText(info, 0,  0, "#FFF")
artist_text = scrollingText(info, 0,  7, "#888")
device_text = scrollingText(info, 0, 21, properties.color["spotify"], True)

def get():
    global data, albumColors, HAIsUpdated #, artist_pos, title_pos, device_pos
    info.rectangle((0,0,30,30), "#000") # Clear screen
    
    if data == {}: return im # Return blank screen if no data

    # Set HA light, if that is required
    if not HAIsUpdated and data["playing"] and ("spotify_lighting" in properties.ha and properties.ha["spotify_lighting"]):
        HAIsUpdated = True
        Thread(target=setHaColors, args=[albumColors]).start()

    # Scrolling Title/Artists/Device
    title_text.draw(data['title'])
    artist_text.draw(" - ".join(data['artists']))
    device_text.draw(data['device']['name'])

    # The albom cover colors
    for i in range(len(albumColors)):
        x, y = i*(SWATCH[0] + SWATCH[2]) + 0, 15
        info.rectangle(((x, y), (x+SWATCH[0]-1, y+SWATCH[1]-1)), fill=tuple(albumColors[i]))

    # Progressbar
    progress = data["progress"] + (dt.now() - data["time"])/td(milliseconds=1) if data["playing"] else 0
    info.line([(0,29),(29,29)], fill="#fff", width=1)
    info.line([(0,29),(round((progress/data["duration"])*30),29)], fill=properties.color["spotify"], width=1)

    # Final assembly
    im.paste(covers[data["cover_url"]], (0,0))
    im.paste(infoArea, (33,1))

    return im
