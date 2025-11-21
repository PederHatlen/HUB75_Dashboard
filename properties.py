import pathlib, json
import numpy as np
from PIL import ImageFont, Image, ImageDraw, ImageColor

TARGET_FPS = 15
WIDTH, HEIGHT = 64, 32

ha = {"display_status":True, "spotify_lighting":False}

path = str(pathlib.Path(__file__).parent.resolve())

with open(f"{path}/secrets.json", "r") as fi: secrets = json.load(fi)

font = {
    5: ImageFont.truetype(f"{path}/fonts/small05.ttf", 5),
    10: ImageFont.truetype(f"{path}/fonts/small05.ttf", 10),
    15: ImageFont.truetype(f"{path}/fonts/small05.ttf", 15),
}
color = {
    "red":      "#FF0000",
    "lightred": "#FF4040",
    "orange":   "#FF8000",
    "yellow":   "#FFFF00",
    "green":    "#00FF00",
    "mint":     "#00FF80",
    "teal":     "#00FFFF",
    "lightblue":"#0080FF",
    "blue":     "#0000FF",
    "purple":   "#8000FF",
    "pink":     "#FF00FF",
    "magenta":  "#FF0080",
    "white":    "#FFFFFF",
    "spotify":  "#1ED760"
}
color_rgb = {}
for c in color: color_rgb[c] = ImageColor.getrgb(color[c])

def getBlankIM(color = None):
    im = Image.new(mode="RGB", size=(WIDTH, HEIGHT), color=color)
    return im, ImageDraw.Draw(im)

def imFromArr(arr, mode = "RGB"): return Image.fromarray(np.array(arr, dtype=np.uint8), mode=mode)