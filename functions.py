import pathlib, requests, json, threading, time
import numpy as np
from PIL import ImageFont, Image, ImageDraw
PATH = str(pathlib.Path(__file__).parent.resolve())

from sklearn.cluster import KMeans

asciiTable = "`.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"

with open("./secrets.json", "r") as fi:
    secrets = json.load(fi)

try:
    with open("./settings.json", "r") as fi: settings = json.load(fi)
except:
    open("./settings.json", "w").close()
    settings = {}

HAColors = []

def threadedHAColors():
    global HAColors
    while True:
        try:
            tempColors = []
            headers = {"Authorization": f"Bearer {secrets['homeassistant']['access_token']}","content-type": "application/json",}
            for state in ["light.bordlampe", "light.led_strip_light", "light.taklampe"]:
                resp = requests.get(f"http://127.0.0.1:8123/api/states/{state}", headers=headers)
                # print(f"Homeassistant {state}: {resp.status_code}")
                if resp.status_code == 200: tempColors.append(resp.json()["attributes"]["rgb_color"])
                else: tempColors.append([255,255,255])
            HAColors = tempColors
        except Exception as e: print(f"Error while trying to get colors from HAS: {e}")
        time.sleep(10)

# threading.Thread(target=threadedHAColors, daemon=True).start()

font = {
    "small05": ImageFont.truetype(f"{PATH}/fonts/small05.ttf", 5),
    "large10": ImageFont.truetype(f"{PATH}/fonts/small05.ttf", 10),
    "icons07": ImageFont.truetype(f"{PATH}/fonts/icons.ttf", 7)
}

color = {
    "red":"#FF0000",
    "lightred":"#FF4040",
    "orange":"#FF8000",
    "yellow":"#FFFF00",
    "green":"#00FF00",
    "mint":"#00FF80",
    "teal":"#00FFFF",
    "lightblue":"#0080FF",
    "blue":"#0000FF",
    "purple":"#8000FF",
    "pink":"#FF00FF",
    "magenta":"#FF0080",
    "white":"#FFFFFF",
    "spotify":"#1ED760"
}

def getBlankIM():
    im = Image.new(mode="RGB", size=(64, 32))
    d = ImageDraw.Draw(im)  
    d.fontmode = "1"
    return im, d

def imFromArr(arr): return Image.fromarray(np.array(arr, dtype=np.uint8), mode="RGB")

def clamp8(x): return min(255, max(0, int(x)))

def rgb2hex(rgb): return '#%02x%02x%02x' % (clamp8(rgb[0]), clamp8(rgb[1]), clamp8(rgb[2]))

def hex2rgb(hex):
    if type(hex) == list and len(hex) == 3: return hex
    if hex[0] == "#": hex = hex[1:]
    if len(hex) == 3: return tuple(int(hex[i]*2, 16) for i in (0, 1, 2))
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def rgb2lum(rgb): return (0.2126*rgb[0] + 0.7152*rgb[1] + 0.0722*rgb[2])/255

def hex2lum(hex): return rgb2lum(hex2rgb(hex))

def rgb_to_hsv(rgb):
    rgb = np.array(rgb) / 255.0
    return np.array(Image.fromarray((rgb[np.newaxis, np.newaxis, :] * 255).astype('uint8')).convert('HSV'))[0, 0] / 255.0

def renderConsole(frame): print("\n".join([" ".join([asciiTable[int(hex2lum(y)*len(asciiTable))] for y in x]) for x in frame]))

def PIL2frame(im): return im
def PIL2Socket(im): return [[rgb2hex(y) for y in x] for x in np.array(im).tolist()]

def haWantsChanging():
    headers = {"Authorization": f"Bearer {secrets['homeassistant']['access_token']}","content-type": "application/json",}
    resp = requests.get(f"http://127.0.0.1:8123/api/states/input_boolean.do_follow_spotify", headers=headers)
    return resp.json()["state"] == "on"

def setHaColors(desk, strip, roof, transition = 1):
    headers = {"Authorization": f"Bearer {secrets['homeassistant']['access_token']}","content-type": "application/json",}
    for data in [{"entity_id":"light.bordlampe", "rgb_color":desk, "transition": transition}, {"entity_id":"light.led_strip_light", "rgb_color":strip, "transition": transition}, {"entity_id":"light.taklampe", "rgb_color":roof, "transition": transition}]:
        resp = requests.post("http://127.0.0.1:8123/api/services/light/turn_on", headers=headers, json=data)
        if resp.status_code == 200: print("Sucess")
        else: print(f"Error {resp.status_code}")

def filter_colors(colors, brightness_threshold=(0.2, 0.9), saturation_threshold=0.2):
    return [color for color in colors if brightness_threshold[0] < rgb_to_hsv(color)[2] < brightness_threshold[1] and rgb_to_hsv(color)[1] > saturation_threshold]

def get_palette(im, n_colors=5):
    img = np.array(im.convert("RGB"))
    img_data = img.reshape((-1, 3))

    # Run KMeans
    kmeans = KMeans(n_clusters=n_colors)
    labels = kmeans.fit_predict(img_data)
    centers = kmeans.cluster_centers_.astype(int)

    # Count labels to find most common
    label_counts = np.bincount(labels)
    sorted_idx = np.argsort(-label_counts)  # Descending order
    sorted_colors = centers[sorted_idx]

    # Filter colors
    filtered_colors = filter_colors(sorted_colors)
    # filtered_colors = sorted_colors

    # Pick colors
    dominant_color = filtered_colors[0] if len(filtered_colors) > 0 else sorted_colors[0]
    accent_color = filtered_colors[1] if len(filtered_colors) > 1 else sorted_colors[1]
    third_color = filtered_colors[2] if len(filtered_colors) > 2 else sorted_colors[2]

    return {
        'dominant': [int(i) for i in tuple(dominant_color)],
        'accent': [int(i) for i in tuple(accent_color)],
        'third': [int(i) for i in tuple(third_color)]
    }