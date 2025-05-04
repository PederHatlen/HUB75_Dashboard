import functions, datetime, math, locale, random
from contextlib import contextmanager
from PIL import Image, ImageDraw

LOCALE_STRING = 'nb_NO.utf8' # Change to your own (trust me it's the easiest way)

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

dust = [stardust(random.randint(0,32)) for i in range(100)]


@contextmanager
def setlocale(name):
    saved = locale.setlocale(locale.LC_ALL)
    try: yield locale.setlocale(locale.LC_ALL, name)
    finally: locale.setlocale(locale.LC_ALL, saved)

small05 = functions.font["small05"]


def hexFun():
    now = datetime.datetime.now()
    hexTime = f"#{round((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()*100):0>6X}".upper() # Milliseconds -> Hex

    im, d = functions.getBlankIM()
    d.rectangle((0,0,64,32), fill=hexTime)
    d.text((5,5), hexTime, font=small05, fill=(255,255,255))

    return im


def hexBoring():
    now = datetime.datetime.now()

    hexTime = f"#{str(now.hour).rjust(2,'0')}{str(now.minute).rjust(2,'0')}{str(now.second).rjust(2,'0')}"  # Clock as color

    im, d = functions.getBlankIM()
    d.rectangle((0,0,64,32), fill=hexTime)
    d.text((5,5), hexTime, font=small05, fill=(255,255,255))

    return im

ps, gap = 4, 2 # Pixel size, pixel gap
def binary():
    im, d = functions.getBlankIM()

    now = datetime.datetime.now()
    time = list(f"{str(now.hour).rjust(2,'0')}{str(now.minute).rjust(2,'0')}{str(now.second).rjust(2,'0')}")
    for x, n in enumerate(time):
        for y in range(0,4):
            xc = x*(gap+ps) + (32-(ps*6+gap*5)/2)           # pixel and gap size offsetting + centering on the screen
            yc = (3-y)*(gap+ps) + (16-(ps*4 + gap*3)/2)     # reversing, pixel and gap size offsetting + centering on the screen

            if int(n) | (2**y) == int(n): d.rectangle(((xc,yc), (xc+ps-1,yc+ps-1)), "#fff")     # if number is the same when you turn on bit at n position bit is in number
            elif y<3 or x%2: d.rectangle(((xc,yc), (xc+ps-1,yc+ps-1)), "#222")                  # The times 10 spot should be 1 lower (hour has no need for 3, but it looks bad without)

    return im

def analog():
    im, d = functions.getBlankIM()

    now = datetime.datetime.now()

    o = 15  # Origo
    r = 15  # Radius
    w = 4   # Width

    hLen = 8    # Hour dial length
    mLen = 10   # Minute dial length
    sLen = 14   # Second dial length

    for deg in range(0, 360, 30):
        x, y = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        d.line((round(x*(r-w+1)) + o, round(y*(r-w+2)) + o, round(x*r)+o, round(y*r)+o), functions.color["orange"], 1)
    for deg in range(0, 360, 90):
        x, y = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        d.line((round(x*(r-w+1)) + o, round(y*(r-w+2)) + o, round(x*r)+o, round(y*r)+o), "#fff", 1)

    hour = (now.hour/12) * 2*math.pi - math.pi/2
    minute = (now.minute/60) * 2*math.pi - math.pi/2
    second = (now.second/60) * 2*math.pi - math.pi/2

    d.line((o, o, round(math.cos(hour)*hLen)+o, round(math.sin(hour)*hLen)+o), functions.color["white"], 1)
    d.line((o, o, round(math.cos(minute)*mLen)+o, round(math.sin(minute)*mLen)+o), functions.color["white"], 1)
    d.line((o, o, round(math.cos(second)*sLen)+o, round(math.sin(second)*sLen)+o), functions.color["orange"], 1)

    with setlocale(LOCALE_STRING):
        d.text((34, 0), now.strftime("%A"), functions.color["orange"], small05)
        d.text((34, 8), now.strftime("%-d %b")[:-1], functions.color["white"], small05)
        d.text((34, 16), f"Uke {str(now.isocalendar()[1]).rjust(2, '0')}", functions.color["white"], small05)

    # d.point((15, 15), functions.color["orange"])

    # d.point((*[(x*2, 0) for x in range(32)], *[(0, y*2) for y in range(16)]))

    return im


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

def holo(n, size, depth, color):
    d = depth+1
    char = Image.new(mode="RGBA", size=(size+depth, size*2+d))
    mask = character(n, size=size)
    for i in range(0,d)[::-1]:
        c = tuple(round(x/(i+1)) for x in color)
        char.paste(character(n, c, size), (i,i), mask=mask)
    return char


def segment():
    im, d = functions.getBlankIM()

    size, depth = 6, 20
    width = size+4

    x, y = 2, 8

    BColor = (0, 255, 212)   # Teal
    FColor = (164, 10, 255)  # Purple


    for s in dust:
        s.render(d, color=BColor)
        if not s.isBound():
            dust.remove(s)
            dust.append(stardust())

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

    return im


selector = 0
total = 4

def dial(e):
    global selector, total
    if e == "1R": selector = (selector+1 if selector < total else 0)
    elif e == "1L": selector = (selector-1 if selector > 0 else total)

def get():
    if selector == 0: return analog()
    if selector == 1: return binary()
    if selector == 2: return hexBoring()
    if selector == 3: return hexFun()
    if selector == 4: return segment()

    return analog()