import adafruit_blinka_raspberry_pi5_piomatter as piomatter
import PIL.Image as Image
import numpy as np

isSetup = False

pWidth, pHeight = 64, 32
framebuffer = np.asarray(Image.new(mode="RGB", size=(pWidth, pHeight))) + 0
matrix = ""


def setup(width, height):
    global matrix, pWidth, pHeight, framebuffer, isSetup
    pWidth, pHeight = width, height 
    geometry = piomatter.Geometry(width=pWidth, height=pHeight, n_addr_lines=(5 if pHeight > 32 else 4), rotation=piomatter.Orientation.Normal)
    framebuffer = np.asarray(Image.new(mode="RGB", size=(pWidth, pHeight))) + 0

    matrix = piomatter.PioMatter(colorspace=piomatter.Colorspace.RGB888Packed,
        pinout=piomatter.Pinout.AdafruitMatrixBonnet,
        framebuffer=framebuffer,
        geometry=geometry)
    
    isSetup = True

def render(f):
    if not isSetup: return

    if f.size != (pWidth,pHeight): f = f.crop((0,0,pWidth,pHeight))
    framebuffer[:] = np.asarray(f)
    matrix.show()
