import functions, datetime, requests, json, textwrap
from PIL import Image, ImageDraw, ImageEnhance
from functions import color

small05 = functions.font["small05"]

lfn = 0
expires = datetime.datetime.now(tz=datetime.timezone.utc)
dataCuttof = datetime.datetime.now(tz=datetime.timezone.utc)

# lat, long = 63.4224, 10.4320 # Trondheim Norway

settings = {
    "lat":63.4224,
    "long":10.4320
}

# def contrast(img, level=0.7): return ImageEnhance.Contrast(img).enhance(level)
def contrast(img, level=1.2):
    def cont(c): return 128 + level * (c - 128)
    return img.point(cont)

# Weather icons from YR
with open("./weatherIcons.json", "r") as fi: weatherIcons = json.load(fi)
icons      = {e:contrast(Image.open(f"./weatherIcons/{weatherIcons[e]['code']}.png")).resize((18,18), Image.Resampling.BOX) for e in weatherIcons.keys()}
iconsSmall = {e:contrast(Image.open(f"./weatherIcons/{weatherIcons[e]['code']}.png")).resize((10,10), Image.Resampling.BILINEAR) for e in weatherIcons.keys()}

# Icons for current events
LB = functions.hex2rgb(functions.color["lightblue"])
WC, GC, BC = (255,255,255), (100,100,100), (0,0,0)
rainIcon = functions.imFromArr([[LB,BC,BC,BC,LB],[LB,BC,LB,BC,BC],[BC,BC,LB,BC,LB],[LB,BC,BC,BC,LB],[LB,BC,LB,BC,BC],[BC,BC,LB,BC,BC]])
cloudIcon = functions.imFromArr([[BC,WC,WC,BC,BC,BC],[WC,WC,WC,WC,WC,BC],[WC,WC,WC,WC,WC,WC],[WC,WC,WC,WC,WC,WC]])
windIcon = functions.imFromArr([[BC,BC,WC,GC,BC],[GC,GC,WC,GC,BC],[WC,WC,WC,WC,WC],[BC,GC,WC,GC,GC],[BC,GC,WC,BC,BC]])

def get_cached_data():
    global expires
    with open("./tempWeather.json") as fi:
        try:
            cach = json.load(fi)
            expires = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=2)
            return cach
        except:
            print("Coud not get cache, persuming expired")
            return {"expires":(datetime.datetime.now(tz=datetime.timezone.utc)-datetime.timedelta(hours=2)).isoformat()}

def get_data():
    global expires
    # return get_cached_data()
    cach = get_cached_data()
    if "expires" in cach and datetime.datetime.fromisoformat(cach["expires"]) > datetime.datetime.now(tz=datetime.timezone.utc):
        print(f"Using cached data, expires {cach['expires']}")
        return cach

    headers = {'User-Agent':'https://github.com/PederHatlen/MatrixDashboard email:pederhatlen@gmail.com',}
    response = requests.get(f"https://api.met.no/weatherapi/locationforecast/2.0/complete?lat={round(settings['lat'],4)}&lon={round(settings['long'],4)}",headers=headers)
    try: expires = datetime.datetime.strptime(response.headers["Expires"][:-4], "%a, %d %b %Y %H:%M:%S", ).replace(tzinfo=datetime.timezone.utc)
    except Exception as E:
        print(E)
        expires = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=4)
        print("Could not parse expiration time (using +4 hours) Error: {E}")
    print(f"Got new weatherdata, expiration: {expires}")
    data = response.json()
    data["expires"] = expires.isoformat()

    with open("./tempWeather.json", "w") as fi:
        fi.write(json.dumps(data))
    return data
    
def get_current_hour(t):
    global data
    for d in data["properties"]["timeseries"]:
        if d["time"][:13] == t.isoformat()[:13]:
            return d["data"]
        
def get_cuttof(data):
    for d in data["properties"]["timeseries"]:
        if not set({"next_12_hours", "next_6_hours", "next_1_hours"}).issubset(set(d["data"].keys())):
            return datetime.datetime.fromisoformat(d["time"])

# dn = 0
# def dial(e):
#     global dn
#     print(dn)
#     if e == "1R": dn+=1
#     elif e == "1L": dn-=1

offsetH = 0
def dial(e):
    global data, dataCuttof, offsetH
    if e == "1R" and dataCuttof > datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=offsetH+1):
        offsetH+=1 
    elif e == "1L" and offsetH > 0:
        offsetH-=1

def btn():
    global offsetH
    offsetH = 0

data = {}
def get():
    global data, lfn, weatherIcons, expires, dataCuttof

    if datetime.datetime.now(tz=datetime.timezone.utc) > expires: 
        data = get_data()
        dataCuttof = get_cuttof(data)
    
    im, d = functions.getBlankIM()

    if data == {}: return im

    now = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=offsetH)
    currentHour = get_current_hour(now)

    # im.paste(icons[list(weatherIcons.keys())[dn//1 % len(weatherIcons.keys())]], (1, 1))
    # im.paste(icons1[list(weatherIcons.keys())[dn//1 % len(weatherIcons.keys())]], (18, 1))

    # im.paste(iconsSmall[list(weatherIcons.keys())[dn//1 % len(weatherIcons.keys())]], (20, 7))
    # im.paste(iconsSmall[list(weatherIcons.keys())[dn//1 % len(weatherIcons.keys())]], (32, 7))

    # im.paste(icons[list(weatherIcons.keys())[dn//1 % len(weatherIcons.keys())]], (1, 1))
    
    if offsetH == 0:
        im.paste(icons[currentHour['next_1_hours']['summary']['symbol_code']], (1, 1))
        im.paste(iconsSmall[currentHour['next_6_hours']['summary']['symbol_code']], (20, 6))
        im.paste(iconsSmall[currentHour['next_12_hours']['summary']['symbol_code']], (32, 6))
        d.text((21, 0), "06", font=small05, fill=color["orange"])
        d.text((33, 0), "12", font=small05, fill=color["orange"])
    else:
        im.paste(iconsSmall[currentHour['next_1_hours']['summary']['symbol_code']], (3, 7))
        im.paste(iconsSmall[currentHour['next_6_hours']['summary']['symbol_code']], (15, 7))
        im.paste(iconsSmall[currentHour['next_12_hours']['summary']['symbol_code']], (27, 7))
        d.text((1, 1), f"+{offsetH}", font=small05, fill=color["lightred"])
        d.text((16, 1), "06", font=small05, fill=color["orange"])
        d.text((28, 1), "12", font=small05, fill=color["orange"])

    # im.paste(iconsSmall[currentHour['next_6_hours']['summary']['symbol_code']], (20, 7))
    # im.paste(iconsSmall[currentHour['next_12_hours']['summary']['symbol_code']], (32, 7))
    # d.text((21, 1), "06", font=small05, fill=color["orange"])
    # d.text((33, 1), "12", font=small05, fill=color["orange"])

    description = "\n".join(textwrap.wrap(weatherIcons[currentHour['next_1_hours']['summary']['symbol_code']]["description"], int(40//small05.getlength("A")), break_long_words=False))
    #description = "\n".join(textwrap.wrap(weatherIcons[list(weatherIcons.keys())[dn//1 % len(weatherIcons.keys())]]["description"], width=int(40//small05.getlength("A")), break_long_words=False))

    temp = currentHour["instant"]["details"]["air_temperature"]
    temp = temp if (-10 < int(temp) < 10) else round(temp)

    percipation = currentHour["next_1_hours"]["details"]["precipitation_amount"]
    percipation = percipation if (percipation < 10) else round(percipation)

    clouds = str(round(currentHour["instant"]["details"]["cloud_area_fraction"]))
    wind = str(currentHour["instant"]["details"]["wind_speed"])

    d.text((56 - small05.getlength(str(temp)), 1), str(temp), font=small05)
    d.text((56 - small05.getlength(str(percipation)), 9), str(percipation), font=small05)
    d.text((56 - small05.getlength(str(clouds)), 17), str(clouds), font=small05)
    d.text((56 - small05.getlength(str(wind)), 25), str(wind), font=small05)

    d.text((56, 1), "°C", font=small05, fill=(color["lightblue"] if temp < 0 else color["lightred"]))
    im.paste(rainIcon, (57, 9))
    im.paste(cloudIcon, (57, 17))
    im.paste(windIcon, (57, 25))

    d.multiline_text((1, (20 if "\n" in description else 25)), description, font=small05, spacing=1)
    
    return im
