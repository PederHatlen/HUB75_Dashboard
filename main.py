import properties, display, virtual_display, menu, pannels, error
import time, gpiozero, traceback, threading, json, re
from websockets.sync.client import connect

class dial:
    def __init__(self, dialNumber, BTNpin, D1, D2, isMenu = False):
        self.BTN = gpiozero.Button(BTNpin,bounce_time=0.1)
        self.DIAL = gpiozero.RotaryEncoder(D1,D2, wrap=True, max_steps=0)
        self.dialNumber = dialNumber

        self.isMenu = isMenu

        self.BTN.when_activated = self.btn
        self.DIAL.when_rotated_clockwise = (lambda: self.dial("R"))
        self.DIAL.when_rotated_counter_clockwise = (lambda: self.dial("L"))

    def dial(self, dir):
        if menu.active:
            menu.dial(f"{self.dialNumber}{dir}")
            return render(menu.get())

        try: pannels.packages[menu.selected].dial(f"{self.dialNumber}{dir}")
        except AttributeError: return print(f"{menu.selected} doesn't support dial")
        return render(pannels.packages[menu.selected].get())

    def btn(self):
        if self.isMenu:
            menu.active = not menu.active
            if menu.active: render(menu.get())
            return

        try: pannels.packages[menu.selected].btn()
        except AttributeError: return print(f"{menu.selected} doesn't support buttons")
        return render(pannels.packages[menu.selected].get())

    def close(self):
        self.BTN.close()
        self.DIAL.close()

ws, ha_data = "", {"display_status":True, "spotify_lighting": False}
def ha_data_thread():
    global ws, prop
    while True:
        try:
            ws = connect("ws://peder-rpi:8123/api/websocket")
            print("Connected to WebSocket")
            while True:
                time.sleep(0.25)
                raw_message = ws.recv(timeout=None)
                message = json.loads(raw_message)
                if "type" not in message: continue
                if message["type"] == "auth_required": ws.send(json.dumps({"type": "auth", "access_token": properties.secrets["has"]["access_token"]}))
                # if message["type"] == "result": print(raw_message)
                if message["type"] == "auth_ok":
                    print("Successfully authorized with HA")
                    ws.send("""{"id": 1, "type": "subscribe_entities", "entity_ids": ["input_boolean.enable_dashboard_screen"]}""")
                    ws.send("""{"id": 2, "type": "subscribe_entities", "entity_ids": ["input_boolean.do_follow_spotify"]}""")
                if message["type"] == "event" and "event" in message:
                    s = re.search(r'(?<=\"s\":\")(?:on|off)(?=\",\")', raw_message)
                    if s and message["id"] == 1: ha_data["display_status"] = (s[0] == "on")
                    elif s and message["id"] == 2: ha_data["spotify_lighting"] = (s[0] == "on")
        except Exception as e: print(f"Disconnected from HA, trying to reconnect in 5s {e}")
        if ws != "": ws.close(code=1000, reason="Something messed up here sry")
        time.sleep(5)

def render(im):
    global ha_data
    if ha_data["display_status"]: display.render(im)
    else: display.render(properties.getBlankIM()[0])
    virtual_display.render(im)

spotifyWasPlaying = False
oldSelected = ""
def autoSelector():
    global spotifyWasPlaying, menu, oldSelected
    if pannels.packages["Spotify"].data == {}: return

    spotifyIsPlaying = pannels.packages["Spotify"].data["playing"]

    if not spotifyWasPlaying and spotifyIsPlaying:
        oldSelected = menu.selected
        menu.selected = "Spotify"

    elif spotifyWasPlaying and not spotifyIsPlaying and menu.selected == "Spotify":
        menu.selected = oldSelected

    spotifyWasPlaying = spotifyIsPlaying

if __name__ == "__main__":   
    frameTime = 1/properties.TARGET_FPS
    
    # Dials and buttons
    dials = [dial(0, 26, 20, 21, True), dial(1, 16, 19, 13)]

    threading.Thread(target=ha_data_thread, name="HAS Websocket", daemon=True).start()

    display.setup(properties.WIDTH, properties.HEIGHT)
    menu.setup(pannels)
    virtual_display.setup(1337, dials=dials, allow_cors=True)
    
    for p in pannels.packages:
        try: pannels.packages[p].ha_data_interface(ha_data)
        except AttributeError: continue

    # Render loop
    while True:
        start = time.time()
        autoSelector()

        try: render(menu.get() if menu.active else pannels.packages[menu.selected].get())
        except KeyboardInterrupt as E: break
        except Exception as e:
            print(f"Error: {e}", traceback.format_exc())
            render(error.get())
            time.sleep(2)

        compTime = time.time() - start
        # print(compTime)
        time.sleep(frameTime - min(frameTime-0.01, compTime))

    for d in dials: d.close()
    print("Stopping...")