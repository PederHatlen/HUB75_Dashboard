import pathlib, json
import numpy as np
from PIL import ImageFont, Image, ImageDraw, ImageColor

### Settings ###
TARGET_FPS = 15
WIDTH, HEIGHT = 64, 32
DISPLAY_DEBUG_MENU = True

# Globally available properties
ha, data, pannels = {}, {}, ""


PATH = str(pathlib.Path(__file__).parent.resolve())
with open(f"{PATH}/secrets.json", "r") as fi: secrets = json.load(fi)

font = {
    5: ImageFont.truetype(f"{PATH}/fonts/small05.ttf", 5, layout_engine=ImageFont.Layout.BASIC),
    10: ImageFont.truetype(f"{PATH}/fonts/small05.ttf", 10, layout_engine=ImageFont.Layout.BASIC),
    15: ImageFont.truetype(f"{PATH}/fonts/small05.ttf", 15, layout_engine=ImageFont.Layout.BASIC),
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

menuColor = {
    "sys":color_rgb["lightred"],
    "dev":color_rgb["yellow"],
    "fun":color_rgb["purple"],
    "info":color_rgb["green"],
    "DEFAULT": (68, 68, 68)
}

### Functions ###
def getBlankIM(color = None) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new(mode="RGB", size=(WIDTH, HEIGHT), color=color)
    return im, ImageDraw.Draw(im)

def imFromArr(arr, mode = "RGB") -> Image.Image: return Image.fromarray(np.array(arr, dtype=np.uint8), mode=mode)