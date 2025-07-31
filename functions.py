import pathlib, requests, json, base64
import numpy as np
from PIL import ImageFont, Image, ImageDraw
PATH = str(pathlib.Path(__file__).parent.resolve())

WIDTH = 64
HEIGHT = 32

HA_LIGHT_IDS = ["light.bordlampe", "light.wled1", "light.led_strip_light", "light.taklampe"]

asciiTable = "`.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"

with open("./secrets.json", "r") as fi:
    secrets = json.load(fi)

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

def getBlankIM(color = None):
    im = Image.new(mode="RGB", size=(WIDTH, HEIGHT), color=color)
    d = ImageDraw.Draw(im)  
    d.fontmode = "1"
    return im, d

def imFromArr(arr, mode = "RGB"): return Image.fromarray(np.array(arr, dtype=np.uint8), mode=mode)

def clamp8(x): return min(255, max(0, int(x)))
def rgb2hex(rgb): return '#%02x%02x%02x' % (clamp8(rgb[0]), clamp8(rgb[1]), clamp8(rgb[2]))

def hex2rgb(hex):
    if type(hex) == list and len(hex) == 3: return hex
    if hex[0] == "#": hex = hex[1:]
    if len(hex) == 3: return tuple(int(hex[i]*2, 16) for i in (0, 1, 2))
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def PIL2Socket(im): return [[rgb2hex(y) for y in x] for x in np.array(im).tolist()]

def HASGetHelperStatus(helperID):
    # print("Getting status from HA")
    try:
        headers = {"Authorization": f"Bearer {secrets['homeassistant']['access_token']}","content-type": "application/json",}
        return requests.get(f"http://127.0.0.1:8123/api/states/input_boolean.{helperID}", headers=headers).json()["state"] == "on"
    except Exception as E:
        print("Couldn't contact HAS")
        return False

def setHaColors(colors, transition = 1):
    try:
        headers = {"Authorization": f"Bearer {secrets['homeassistant']['access_token']}","content-type": "application/json",}
        for i in range(len(HA_LIGHT_IDS)):
            data = {"entity_id":HA_LIGHT_IDS[i], "rgb_color":colors[i%len(colors)], "transition": transition}
            print(f"Setting {data['entity_id']} to {data['rgb_color']}")
            resp = requests.post("http://127.0.0.1:8123/api/services/light/turn_on", headers=headers, json=data)
            if resp.status_code != 200: print(f"Error {resp.status_code}")
    except Exception as E:
        print("Couldn't set colors with HAS")

def sendImageToESP(im, host):
    try: 
        b64 = base64.b64encode(np.array(im.convert('RGB'), dtype=np.uint8).tobytes()).decode("utf-8")
        # print(b64, len(b64))
        r = requests.post(host,headers={"Content-Type": "text/plain"},data=b64)
        if r.status_code == 200: print(f"Image sent to ESP sucessfully!")
        else: print(f"Got response while sending image to ESP: {r.status_code}, {r.text}")
    except Exception as E: print(f"Could not send image to ESP")