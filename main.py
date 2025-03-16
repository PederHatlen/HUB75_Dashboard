import Display, virtual_display, menu, pannels, functions, error
import time, gpiozero, datetime, traceback
from threading import Thread

from flask import request

DO_AUTOSELECTING = True

# Initialize the webserver/running screen emulator
socketio = virtual_display.run(1337, allow_cors=True)

oldoutTS = 0
oldimage = pannels.packages["Blank"].get()

consolerender = False

spotifyWasPlaying = False
autoSelected = False
oldSelected = ""
lastRenderEvent = datetime.datetime.now()

IsMenuActive= False

spotifyRunner = Thread(target=pannels.packages["Spotify"].threadedData, name="SpotifyRunner", daemon=True)
spotifyRunner.start()

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
        if IsMenuActive:
            menu.dial(f"{self.dialNumber}{dir}")
            return render(menu.get())

        try: pannels.packages[menu.selected].dial(f"{self.dialNumber}{dir}")
        except AttributeError: return print(f"{menu.selected} doesn't support dial")
        return render(pannels.packages[menu.selected].get())
    
    def btn(self):
        if self.isMenu:
            global IsMenuActive
            IsMenuActive = not IsMenuActive
            if IsMenuActive: render(menu.get())
            else: pannels.packages[menu.selected].needsRendering = True
            return
        
        try: pannels.packages[menu.selected].btn()
        except AttributeError: return print(f"{menu.selected} doesn't support buttons")
        return render(pannels.packages[menu.selected].get())

def render(im):
    global oldimage, lastRenderEvent
    lastRenderEvent = datetime.datetime.now()
    if oldimage != im:
        oldimage = im
        Display.render(im)
        sockFrame = functions.PIL2Socket(im)
        if consolerender: functions.renderConsole(sockFrame)
        return socketio.emit("refresh", sockFrame)

def autoSelector():
    global spotifyWasPlaying, menu, oldSelected, autoSelected

    spotifyIsPlaying = pannels.packages["Spotify"].data["playing"]

    if not spotifyWasPlaying and spotifyIsPlaying:
        oldSelected = menu.selected
        menu.selected = "Spotify"
        autoSelected = True

    elif spotifyWasPlaying and not spotifyIsPlaying and autoSelected:
        menu.selected = oldSelected
    
    spotifyWasPlaying = spotifyIsPlaying

if __name__ == "__main__":
    # Dials and buttons
    dial0 = dial(0, 26, 20, 21, True)
    dial1 = dial(1, 16, 19, 13)

    @socketio.on("connect")
    def onConnect(data=""):
        socketio.emit("refresh", functions.PIL2Socket(oldimage), to=request.sid)

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
        if DO_AUTOSELECTING: autoSelector()

        if IsMenuActive: render(menu.get())
        else:
            try: render(pannels.packages[menu.selected].get())
            except Exception as e:
                print(f"Error: {e}", traceback.format_exc())
                render(error.get())

        # print(f"Computation time: {round(time.time() - start, 3)}s") 
        # compTime = round(time.time() - start, 3)
        # if compTime >= 0.1: print(f"over: {compTime}")

        time.sleep(0.1 - min(0.05, round(time.time() - start, 3)))
