import functions, datetime, math, locale
from contextlib import contextmanager

LOCALE_STRING = 'nb_NO.utf8' # Change to your own (trust me it's the easiest way)

@contextmanager
def setlocale(name):
    saved = locale.setlocale(locale.LC_ALL)
    try: yield locale.setlocale(locale.LC_ALL, name)
    finally: locale.setlocale(locale.LC_ALL, saved)

small05 = functions.font["small05"]

def get():
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