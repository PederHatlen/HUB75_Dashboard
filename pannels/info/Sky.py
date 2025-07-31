import functions, datetime, random
import numpy as np
import astral.sun, astral.moon # Cheating
from PIL import Image, ImageDraw
from math import radians, sin, cos, atan2, asin, degrees, pi

small05 = functions.font["small05"]

DATE_COLOR    = "#7BD3EA"
SUNRISE_COLOR = (255, 168, 92)
SUNSET_COLOR  = (255, 107, 107)
SUN_COLOR     = (255, 241, 117)
MOON_COLOR    = (21, 56, 99)
BACKGROUND    = "#7BD3EA"

BC = (0, 0, 0)
GC = MOON_COLOR
WC = (255, 255, 255)

# Moon phase images
moonPhases = {
    0:functions.imFromArr([[BC,GC,GC,GC,GC,BC],[GC,GC,GC,GC,GC,GC],[GC,GC,GC,GC,GC,GC],[GC,GC,GC,GC,GC,GC],[GC,GC,GC,GC,GC,GC],[BC,GC,GC,GC,GC,BC]]),
    1:functions.imFromArr([[BC,GC,GC,WC,WC,BC],[GC,GC,GC,GC,WC,WC],[GC,GC,GC,GC,GC,WC],[GC,GC,GC,GC,GC,WC],[GC,GC,GC,GC,WC,WC],[BC,GC,GC,WC,WC,BC]]),
    2:functions.imFromArr([[BC,GC,GC,WC,WC,BC],[GC,GC,GC,WC,WC,WC],[GC,GC,GC,WC,WC,WC],[GC,GC,GC,WC,WC,WC],[GC,GC,GC,WC,WC,WC],[BC,GC,GC,WC,WC,BC]]),
    3:functions.imFromArr([[BC,GC,GC,WC,WC,BC],[GC,GC,WC,WC,WC,WC],[GC,WC,WC,WC,WC,WC],[GC,WC,WC,WC,WC,WC],[GC,GC,WC,WC,WC,WC],[BC,GC,GC,WC,WC,BC]]),
    4:functions.imFromArr([[BC,WC,WC,WC,WC,BC],[WC,WC,WC,WC,WC,WC],[WC,WC,WC,WC,WC,WC],[WC,WC,WC,WC,WC,WC],[WC,WC,WC,WC,WC,WC],[BC,WC,WC,WC,WC,BC]]),
    5:functions.imFromArr([[BC,WC,WC,GC,GC,BC],[WC,WC,WC,WC,GC,GC],[WC,WC,WC,WC,WC,GC],[WC,WC,WC,WC,WC,GC],[WC,WC,WC,WC,GC,GC],[BC,WC,WC,GC,GC,BC]]),
    6:functions.imFromArr([[BC,WC,WC,GC,GC,BC],[WC,WC,WC,GC,GC,GC],[WC,WC,WC,GC,GC,GC],[WC,WC,WC,GC,GC,GC],[WC,WC,WC,GC,GC,GC],[BC,WC,WC,GC,GC,BC]]),
    7:functions.imFromArr([[BC,WC,WC,GC,GC,BC],[WC,WC,GC,GC,GC,GC],[WC,GC,GC,GC,GC,GC],[WC,GC,GC,GC,GC,GC],[WC,WC,GC,GC,GC,GC],[BC,WC,WC,GC,GC,BC]])
}

# LC = SUN_COLOR
# RAY = (102, 96, 47)
# HC = (68, 68, 68)
# sunrise_icon = functions.imFromArr([
#     [BC,BC,LC,BC,BC],
#     [BC,LC,BC,LC,BC],
#     [BC,BC,BC,BC,BC],
#     [LC,BC,LC,BC,LC],
#     [BC,LC,LC,LC,BC],
#     [HC,HC,HC,HC,HC],
# ])

LC  = SUN_COLOR
RAY = LC
# RAY = (102, 96, 47)
HC  = (68, 68, 68)
BC  = (0, 0, 0)
sunrise_icon = functions.imFromArr([
    # [BC,BC,BC,BC,BC,BC,BC],
    [BC,BC,BC,RAY,BC,BC,BC],
    [BC,BC,RAY,BC,RAY,BC,BC],
    [BC,BC,BC,BC,BC,BC,BC],
    [BC,BC,LC,LC,LC,BC,BC],
    [BC,LC,LC,LC,LC,LC,BC],
    [HC,HC,HC,HC,HC,HC,HC],
])


# LC  = SUNSET_COLOR
# RAY = LC
sunset_icon = functions.imFromArr([
    [BC,BC,RAY,BC,RAY,BC,BC],
    [BC,BC,BC,RAY,BC,BC,BC],
    [BC,BC,BC,BC,BC,BC,BC],
    [BC,BC,LC,LC,LC,BC,BC],
    [BC,LC,LC,LC,LC,LC,BC],
    [HC,HC,HC,HC,HC,HC,HC],
])

# arrow2 = functions.imFromArr([
#     [BC,BC,LC,BC,BC],
#     [BC,LC,LC,LC,BC],
#     [LC,LC,LC,LC,LC],
#     [BC,BC,LC,BC,BC],
#     [BC,BC,LC,BC,BC],
# ])

stars = [[(random.randint(0,64), random.randint(0,64)), random.random() * 2*pi] for i in range(128)]

fn_last = 0
oldim = Image.new("RGB", size=(64,32))

lat, long = 63.4224, 10.4320 # Trondheim
# lat, long = 69.0645, 18.5152 # Bardufoss
# lat, long = 90, 10.4320 # North pole
# lat, long = 0, 10.4320 # Equator

def getSunAltitude(t:datetime.datetime, lat = lat, long = long):  # Tyholttårnet, Trondheim Norway
    # Souces: 
    # https://en.wikipedia.org/wiki/Position_of_the_Sun
    # https://sceweb.sce.uhcl.edu/helm/WEB-Positional%20Astronomy/Tutorial/Conversion/Conversion.html
    # https://aa.usno.navy.mil/faq/GAST

    D = (t.timestamp() / 86400.0) - 10957.5                                                         # Days since 1st of January 2000 with julian calendar
    L = (280.46646 + 0.98564736 * D)                                                                # Mean longitude of sun (corrected for aberration of light)
    g = radians(357.528 + 0.9856003 * D)                                                            # Mean anomaly of the earth, angle from periapsis in an orbit (from the earths perspective)
    eclipticLong = radians(L + 1.9148 * sin(g) + 0.02 * sin(2 * g))                                 # Ecliptic Longitude of sun
    eclipticTilt = radians(23.439 - 0.0000004 * D)                                                  # Obliquity of the ecliptic, The tilt of the axis the sun and earth lies on

    RA = atan2(cos(eclipticTilt) * sin(eclipticLong), cos(eclipticLong))                            # Right Ascension, angle between longitude 0 on the equator to the suns longitude on the equator
    DEC = asin(sin(eclipticTilt) * sin(eclipticLong))                                               # declination

    GMST = 280.46061837 + 360.98564736629 * D                                                       # Greenwich Mean Sidereal Time (suntime at Greenwich) in hours
    LHA = radians(GMST + long - degrees(RA))                                                        # Local Hour Angle (LST - Right Ascention)
    
    return degrees(asin(sin(DEC) * sin(radians(lat)) + cos(DEC) * cos(radians(lat)) * cos(LHA)))    # Altitude of the sun on the sky from given coordinates

dayoffset = 0
def dial(e):
    global dayoffset
    if e == "1R": dayoffset+=1
    elif e == "1L": dayoffset-=1
    
def btn():
    global dayoffset
    dayoffset = 0

def get():
    global oldim, fn_last, dayoffset
    
    im = Image.new(mode="RGB", size=(64, 32))
    d = ImageDraw.Draw(im, mode="RGBA")
    now = datetime.datetime.now() + datetime.timedelta(days=dayoffset) # Scrub through the year
    modified = now.replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=datetime.timezone.utc)

    xyValues = [(t, 15-(int((getSunAltitude(modified + datetime.timedelta(hours=t/2))/90)*15.5))) for t in range(0,64)]

    try:
        s = astral.sun.sun(astral.Observer(latitude=lat, longitude=long), modified, tzinfo=modified.tzinfo)
        sunriseDT = s["sunrise"].astimezone().strftime("%H:%M")
        sunsetDT = s["sunset"].astimezone().strftime("%H:%M")
    except: sunriseDT, sunsetDT = "None", "None"

    for s in stars:
        s[1] += 0.1
        c = round((sin(s[1])+1)*10)
        d.point(s[0], fill=(c,c,c))

    d.line(((0,16), (64,16)), "#444")                                                   # Horizonline
    d.line(xyValues, "#FFEECF")                                                            # Graph of sun possitions
    sunPos = xyValues[round((now.hour + now.minute/60)*2)]

    d.circle(sunPos, 4, (*SUN_COLOR, 10))
    d.circle(sunPos, 3, (*SUN_COLOR, 25))
    d.circle(sunPos, 2, (*SUN_COLOR, 75))
    d.rectangle(((sunPos[0]-1, sunPos[1]-1), (sunPos[0]+1, sunPos[1]+1)), fill=functions.color["yellow"])
    d.point(sunPos, "#FFF")

    moonPos = (54, 1)
    im.paste(moonPhases[((astral.moon.phase(modified)/27.99)*8)//1], moonPos)
    d.ellipse(((moonPos[0]-1, moonPos[1]-1), (moonPos[0]+6, moonPos[1]+6)), (*MOON_COLOR, 19))
    d.ellipse(((moonPos[0]-2, moonPos[1]-2), (moonPos[0]+7, moonPos[1]+7)), (*MOON_COLOR, 5))

    d.text((1,1), str(now.strftime("%b %d")), MOON_COLOR, small05)
    d.text((1, 26), str(sunriseDT), SUN_COLOR, small05)
    d.text((46, 26), str(sunsetDT), SUN_COLOR, small05)

    im.paste(sunrise_icon, (20, 26))
    im.paste(sunset_icon, (37, 26))
    oldim = im

    return im