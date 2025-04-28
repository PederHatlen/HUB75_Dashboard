import datetime, random, sys , os
from PIL import Image, ImageDraw
import functions

small05 = functions.font["small05"]

#      1
#    -----
#   |     |
# 2 |     | 6
#   |  7  |
#    -----
#   |     |
# 3 |     | 5
#   |     |
#    -----
#      4

font = {1:[5,6], 2:[1,3,4,6,7], 3:[1,4,5,6,7], 4:[2,5,6,7], 5:[1,2,4,5,7], 6:[1,2,3,4,5,7], 7:[1,5,6], 8:[1,2,3,4,5,6,7,8], 9:[1,2,4,5,6,7], 0:[1,2,3,4,5,6]}
def character(n, fill = "#fff", size = 8):
    char = Image.new(mode="RGBA", size=(size, size*2+1))
    d = ImageDraw.Draw(char)
    
    if 1 in font[n]: d.line((0, 0, size, 0), fill=fill)                 # 1 - TopLine
    if 2 in font[n]: d.line((0, 0, 0, size), fill=fill)                 # 2 - TopLeft
    if 3 in font[n]: d.line((0, size, 0, 2*size), fill=fill)            # 3 - BottomLeft
    if 4 in font[n]: d.line((0, 2*size, size, 2*size), fill=fill)       # 4 - BottomLine
    if 5 in font[n]: d.line((size-1, size, size-1, 2*size), fill=fill)  # 5 - BottomRight
    if 6 in font[n]: d.line((size-1, 0, size-1, size), fill=fill)       # 6 - TopRight
    if 7 in font[n]: d.line((0, size, size, size), fill=fill)           # 7 - MidLine

    return char

size, depth = 6, 20

width = size+4
height = width+size

x, y = 2, 8

BColor = (0, 255, 212)   # Teal
FColor = (164, 10, 255)  # Purple

class stardust:
    def __init__(self, y = ""):
        self.dir = (1,1)
        self.len = random.randint(2,10)

        self.x = random.randint(-32, 64)

        if self.x < 0 and (y == ""):
            self.y = abs(self.x)
            self.x = 0
        else: self.y = y if y != "" else 0
    
    def render(self, d, color = (255,255,255)):
        self.x += self.dir[0]
        self.y += self.dir[1]
        for n in range(self.len):
            c = tuple(round(((self.len-n)/self.len)*x) for x in color)
            d.point((self.x-self.dir[0]*n, self.y-self.dir[1]*n), c)
    
    def isBound(self): return self.x < 64 or self.y < 32

dustemikkel = [stardust(random.randint(0,32)) for i in range(100)]

def holo(n, size, depth, color):
    d = depth+1
    char = Image.new(mode="RGBA", size=(size+depth, size*2+d))
    mask = character(n, size=size)
    for i in range(0,d)[::-1]:
        c = tuple(round(x/(i+1)) for x in color)
        char.paste(character(n, c, size), (i,i), mask=mask)
    return char


def get():
    im, d = functions.getBlankIM()

    for s in dustemikkel:
        s.render(d, color=BColor)
        if not s.isBound():
            dustemikkel.remove(s)
            dustemikkel.append(stardust())

    color = FColor

    n = datetime.datetime.now()
    # h0 = holo(8, size, depth, color)
    h0 = holo(n.hour//10, size, depth, color)
    h1 = holo(n.hour%10, size, depth, color)
    m0 = holo(n.minute//10, size, depth, color)
    m1 = holo(n.minute%10, size, depth, color)
    s0 = holo(n.second//10, size, depth, color)
    s1 = holo(n.second%10, size, depth, color)

    im.paste(h0,(width*0 +x,y), mask=h0)
    im.paste(h1,(width*1 +x,y), mask=h1)
    im.paste(m0,(width*2 +x,y), mask=m0)
    im.paste(m1,(width*3 +x,y), mask=m1)
    im.paste(s0,(width*4 +x,y), mask=s0)
    im.paste(s1,(width*5 +x,y), mask=s1)


    # mask = character(n.second%10, "#fff", 9)

    # for i in range(1,5)[::-1]:
    #     c = round(255//i)
    #     im.paste(character(n.second%10, (c,c,c), 9), (i,i), mask=mask)


    
    # im.paste(character(n.second%10, "#444"), (4,4))
    # im.paste(character(n.second%10, "#AAA"), (3,3))
    # im.paste(character(n.second%10, "#CCC"), (2,2))
    # im.paste(character(n.second%10, "#FFF"), (1,1))

    return im