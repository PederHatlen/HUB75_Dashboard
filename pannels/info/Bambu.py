import functions, datetime
import bambulabs_api as bl

small05 = functions.font["small05"]

BambulabColor = (0, 255, 0)

LC, DC = (255,255,255), (0,0,0)
bambuIcon = functions.imFromArr([
    [LC,LC,DC,LC,LC],
    [LC,LC,DC,LC,LC],
    [LC,LC,DC,DC,LC],
    [LC,DC,DC,LC,DC],
    [DC,LC,DC,LC,LC],
    [LC,LC,DC,LC,LC],
    [LC,LC,DC,LC,LC],
])

s = functions.secrets["bambulab"]

try: printer = bl.Printer(s["ip"], s["access_code"], s["serial"])
except: printer = False

data = False
dataTS = (datetime.datetime.now() + datetime.timedelta(seconds=2))

def getData():
    global data, dataTS, printer
    try:
        printer.connect()
        data = {
            "state":printer.mqtt_client.get_current_state().name.replace("_", " "),
            "percent":printer.mqtt_client.get_last_print_percentage(),
            "end_time":(datetime.datetime.now().replace(second=0) + datetime.timedelta(minutes=printer.mqtt_client.get_remaining_time())),
            "cur_layers":printer.mqtt_client.current_layer_num(),
            "tot_layers":printer.mqtt_client.total_layer_num(),
        }
    except Exception as E:
        print(f"Could not get new data: {E}")
        data = False
    dataTS = datetime.datetime.now()

def get():
    im, d = functions.getBlankIM()

    if dataTS < (datetime.datetime.now() - datetime.timedelta(seconds=2)): getData()

    if not data:
        d.multiline_text((32, 16), "Printer\noffline", spacing=2, anchor="mm", fill=BambulabColor, font=functions.font["small05"])
        return im

    # im.paste(bambuIcon, (1,0))
    d.text((1,1), data["state"], font=small05, fill=BambulabColor)

    if data["end_time"]:
        td = (data["end_time"] - datetime.datetime.now()).total_seconds()
        d.text((1,7), f'{data["end_time"].strftime("%H:%M")} - {int((td/(60*60))%60)}H {int((td/60)%60):0>2}M', font=small05)

    if data["cur_layers"] != None and data["tot_layers"] != None:
        d.text(((1,19)), f'{data["cur_layers"]}/{data["tot_layers"]}', font=small05, fill="#fff")

    if type(data["percent"]) == int:
        d.text((1,26), f'{data["percent"]}%', font=small05, fill="#fff")

        statusBarIM = functions.Image.new(mode="RGB", size=(int(64*(data["percent"]/100)), 7), color=BambulabColor)
        statusBarD = functions.ImageDraw.Draw(statusBarIM)

        statusBarD.text((1,1), f'{data["percent"]}%', font=small05, fill="#000")
        im.paste(statusBarIM, (0,25))

    return im