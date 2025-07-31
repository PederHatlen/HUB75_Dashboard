import functions, requests, json
from PIL import Image
from datetime import datetime, timezone, timedelta

small05 = functions.font["small05"]

LATITUDE  = 63.4224
LONGITUDE = 10.4320

# Static variables
UTC = timezone.utc

# Weather icons from YR
with open("./weatherIcons_simple.json", "r") as fi: weatherIcons = json.load(fi)
iconsLarge  = {e:Image.open(f"./weatherIcons/{weatherIcons[e]['code']}.png").resize((25,25), Image.Resampling.HAMMING) for e in weatherIcons.keys()}
iconsMedium = {e:Image.open(f"./weatherIcons/{weatherIcons[e]['code']}.png").resize((20,20), Image.Resampling.HAMMING) for e in weatherIcons.keys()}
iconsSmall  = {e:Image.open(f"./weatherIcons/{weatherIcons[e]['code']}.png").resize((15,15), Image.Resampling.HAMMING) for e in weatherIcons.keys()}

# # With a pink background for distinguishing
# bg = Image.new("RGBA", (100,100), "#ff0088")
# iconsLarge  = {e:Image.alpha_composite(bg, Image.open(f"./weatherIcons/{weatherIcons[e]['code']}.png")).resize((25,25), Image.Resampling.HAMMING) for e in weatherIcons.keys()}
# iconsMedium = {e:Image.alpha_composite(bg, Image.open(f"./weatherIcons/{weatherIcons[e]['code']}.png")).resize((20,20), Image.Resampling.HAMMING) for e in weatherIcons.keys()}
# iconsSmall  = {e:Image.alpha_composite(bg, Image.open(f"./weatherIcons/{weatherIcons[e]['code']}.png")).resize((15,15), Image.Resampling.HAMMING) for e in weatherIcons.keys()}

# Icons for current events
LR = [*functions.hex2rgb(functions.color["lightred"]), 255]
LB = [*functions.hex2rgb(functions.color["lightblue"]), 255]
WC, GC, BC = (255,255,255,255), (100,100,100,255), (0,0,0,0)

tempIconR = functions.imFromArr([[LR,LR,BC,BC,BC],[LR,LR,BC,LR,LR],[BC,BC,LR,BC,BC],[BC,BC,LR,BC,BC],[BC,BC,BC,LR,LR]], "RGBA")
tempIconB = functions.imFromArr([[LB,LB,BC,BC,BC],[LB,LB,BC,LB,LB],[BC,BC,LB,BC,BC],[BC,BC,LB,BC,BC],[BC,BC,BC,LB,LB]], "RGBA")

rainIcon = functions.imFromArr([[LB,BC,BC,BC,LB],[LB,BC,LB,BC,LB],[BC,BC,LB,BC,LB],[LB,BC,BC,BC,BC],[LB,BC,BC,LB,BC]], "RGBA")
windIcon = functions.imFromArr([[BC,BC,WC,GC,BC],[GC,GC,WC,GC,BC],[WC,WC,WC,WC,WC],[BC,GC,WC,GC,GC],[BC,GC,WC,BC,BC]], "RGBA")
covrIcon = functions.imFromArr([[BC,BC,WC,WC,BC],[GC,WC,WC,WC,WC],[WC,WC,WC,WC,WC],[GC,WC,WC,WC,GC]], "RGBA")

# Global Variables
expires, dataCuttof = datetime.now(tz=UTC), datetime.now(tz=UTC)
offsetH, dn = 0, 0
data = {}

# Functions
def get_data_cuttof(data):
    for d in data["properties"]["timeseries"]:
        if not set({"next_12_hours", "next_6_hours", "next_1_hours"}).issubset(set(d["data"].keys())):
            return datetime.fromisoformat(d["time"])

def get_cached_data():
    try:
        with open("./tempWeather.json") as fi: return json.load(fi)
    except: return {}

def get_data():
    global expires, dataCuttof
    print("Getting new data")
    cach = get_cached_data()
    if "expires" in cach and datetime.fromisoformat(cach["expires"]) > datetime.now(tz=UTC):
        print(f"Using cached data, expires {cach['expires']}")
        expires = datetime.fromisoformat(cach["expires"])
        dataCuttof = get_data_cuttof(cach)
        return cach

    headers = {'User-Agent':'https://github.com/PederHatlen/MatrixDashboard email:pederhatlen@gmail.com',}
    response = requests.get(f"https://api.met.no/weatherapi/locationforecast/2.0/complete?lat={round(LATITUDE,4)}&lon={round(LONGITUDE,4)}",headers=headers)

    try: expires = datetime.strptime(response.headers["Expires"][:-4], "%a, %d %b %Y %H:%M:%S").replace(tzinfo=UTC)
    except Exception as E:
        print(f"Could not parse expiration time (using +4 hours) Error: {E}")
        expires = datetime.now(tz=UTC) + timedelta(hours=4)
    print(f"Got new weatherdata, expiration: {expires}")

    data = {"expires":expires.isoformat(), **response.json()}
    dataCuttof = get_data_cuttof(data)

    with open("./tempWeather.json", "w") as fi: fi.write(json.dumps(data))
    return data
    
def get_current_hour(t):
    global data
    for d in data["properties"]["timeseries"]:
        if d["time"][:13] == t.isoformat()[:13]: return d["data"]

def dial(e):
    global dataCuttof, offsetH, dn
    dn += (1 if e == "1R" else -1)
    if e == "1R" and dataCuttof > datetime.now(tz=UTC) + timedelta(hours=offsetH+1): offsetH += 1
    elif e == "1L" and offsetH > 0: offsetH -= 1

def btn():
    global offsetH
    offsetH = 0

def get():
    global data, expires

    im, d = functions.getBlankIM()

    if datetime.now(tz=UTC) > expires: data = get_data()
    
    if data == {}: 
        d.text((32, 16), "No data", font=small05, anchor="mm")
        return im

    now = datetime.now(tz=UTC) + timedelta(hours=offsetH)
    currentHour = get_current_hour(now)

    description = weatherIcons[currentHour['next_1_hours']['summary']['symbol_code']]["description"]
    iconLarge = iconsLarge[currentHour['next_1_hours']['summary']['symbol_code']]
    iconMedium = iconsMedium[currentHour['next_1_hours']['summary']['symbol_code']]
    iconNext = iconsSmall[currentHour['next_6_hours']['summary']['symbol_code']]

    # description = weatherIcons[list(weatherIcons.keys())[dn//1 % len(weatherIcons.keys())]]["description"]
    # iconLarge = iconsLarge[list(weatherIcons.keys())[dn//1 % len(weatherIcons.keys())]]
    # iconMedium = iconsMedium[list(weatherIcons.keys())[dn//1 % len(weatherIcons.keys())]]
    # iconNext = iconsSmall[list(weatherIcons.keys())[dn//1 % len(weatherIcons.keys())]]

    # Drawing icons and extra text, Changed sizes/positions, if showing other times
    if offsetH == 0:
        im.paste(iconLarge, (0, 0), mask=iconLarge)
        im.paste(iconNext, (26, 7), mask=iconNext)
        d.text((28, 1), "+6H", font=small05, fill=functions.color["orange"])
    else:
        im.paste(iconMedium, (1, 5), mask=iconMedium)
        im.paste(iconNext, (25, 9), mask=iconNext)
        d.text((27, 3), "+6H", font=small05, fill=functions.color["orange"])
        d.text((1, 0), now.astimezone(datetime.now(timezone.utc).astimezone().tzinfo).strftime("%H:00"), font=small05, fill=functions.color["orange"])

    d.text((1 if len(description) > 5 else 3, 26), description, font=small05)

    # Get current conditions from data
    temp = currentHour["instant"]["details"]["air_temperature"]
    perc = currentHour["next_1_hours"]["details"]["precipitation_amount"]
    wind = currentHour["instant"]["details"]["wind_speed"]
    covr = round(currentHour["instant"]["details"]["cloud_area_fraction"])

    temp = temp if -10 < temp < 10  else round(temp)
    perc = perc if       perc < 100 else round(perc)
    wind = wind if       wind < 100 else round(wind)

    # # Maximum values (The longest suported lengths)
    # temp = -9.9
    # wind = 99.9
    # percipation = 99.9
    # clouds = 100

    # Current concitions values
    d.text((57,  1), str(temp), font=small05, anchor="rt")
    d.text((57,  9), str(perc), font=small05, anchor="rt")
    d.text((57, 17), str(wind), font=small05, anchor="rt")
    d.text((57, 25), str(covr), font=small05, anchor="rt")

    # Current concitions icons
    im.paste(tempIconB if temp < 0 else tempIconR, (58, 1), mask=tempIconB)
    im.paste(rainIcon, (58, 9), mask=rainIcon)
    im.paste(windIcon, (58, 17), mask=windIcon)
    im.paste(covrIcon, (58, 25), mask=covrIcon)
    
    return im
