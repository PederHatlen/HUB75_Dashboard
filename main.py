import sys, datetime
old_f = sys.stdout
class F:
    lastbyteHasNL = True
    def flush(self): old_f.flush()
    def write(self, x):
        old_f.write(f"{datetime.datetime.now().isoformat(sep='[', timespec='milliseconds')}] {x:s}"[10:] if self.lastbyteHasNL else x)
        self.lastbyteHasNL = "\n" in x
sys.stdout = F()

import functions
import Display, virtual_display, menu, pannels, error
import time, gpiozero, traceback, threading
from flask import request

Display.setup(functions.WIDTH, functions.HEIGHT)
menu.setup(pannels)

# Initialize the webserver/running screen emulator
virtual_display.setup(pannels)
socketio = virtual_display.run(1337, allow_cors=True)

lastSentFrame = functions.getBlankIM()[0]

do_display = True

spotifyWasPlaying = False
autoSelected = False
oldSelected = ""
lastRenderEvent = datetime.datetime.now()

def getHASDisplayStatus():
    global do_display
    while True:
        do_display = functions.HASGetHelperStatus("enable_dashboard_screen")
        time.sleep(2)

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

def render(im):
    global lastSentFrame, lastRenderEvent
    lastRenderEvent = datetime.datetime.now()
    if lastSentFrame != im:
        lastSentFrame = im
        if do_display: Display.render(im)
        else: Display.render(functions.getBlankIM()[0])
        return socketio.emit("refresh", functions.PIL2Socket(im))

def autoSelector():
    global spotifyWasPlaying, menu, oldSelected, autoSelected

    spotifyIsPlaying = pannels.packages["Spotify"].data["playing"]

    if not spotifyWasPlaying and spotifyIsPlaying:
        oldSelected = menu.selected
        menu.selected = "Spotify"
        autoSelected = True

    if spotifyWasPlaying and spotifyIsPlaying and menu.selected != "Spotify":
        autoSelected = False

    elif spotifyWasPlaying and not spotifyIsPlaying and autoSelected:
        menu.selected = oldSelected
    
    spotifyWasPlaying = spotifyIsPlaying

if __name__ == "__main__":
    # Dials and buttons
    dial0 = dial(0, 26, 20, 21, True)
    dial1 = dial(1, 16, 19, 13)

    # Get the status of the display from HAS (Ask if display should be off)
    displayRunner = threading.Thread(target=getHASDisplayStatus, name="HASDisplayRunner", daemon=True)
    displayRunner.start()

    @socketio.on("connect")
    def onConnect(data=""):
        socketio.emit("refresh", functions.PIL2Socket(lastSentFrame), to=request.sid)

    @socketio.on('inp')
    def on_connection(data):
        print(f"Input from virtual display: {data}") #type:ignore
        if "dir" in data: 
            if data["dir"][0] == "0": dial0.dial(data["dir"][1])
            elif data["dir"][0] == "1": dial1.dial(data["dir"][1])
        elif "btn" in data:
            if data["btn"] == 0: dial0.btn()
            elif data["btn"] == 1: dial1.btn()

    # Render loop
    while True:
        start = time.time()
        autoSelector()

        if menu.active: render(menu.get())
        else:
            try: render(pannels.packages[menu.selected].get())
            except KeyboardInterrupt as E:
                print("Keyboard interrupt!")
                break
            except Exception as e:
                print(f"Error: {e}", traceback.format_exc())
                render(error.get())

        # print(f"Computation time: {round(time.time() - start, 3)}s") 
        # compTime = round(time.time() - start, 3)
        # if compTime >= 0.1: print(f"over: {compTime}")
        try:
            time.sleep(0.1 - min(0.05, round(time.time() - start, 3)))
        except KeyboardInterrupt as E:
            print("Keyboard interrupt!")
            break

    dial0.BTN.close()
    dial0.DIAL.close()
    dial1.BTN.close()
    dial1.DIAL.close()

    print("Stopping...")