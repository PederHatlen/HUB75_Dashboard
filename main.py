import properties, pannels, display, virtual_display, menu, has_ws, error
import time, gpiozero, traceback


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
        except AttributeError: return print(f"System:  {menu.selected} doesn't support dial")
        return render(pannels.packages[menu.selected].get())

    def btn(self):
        if self.isMenu:
            menu.active = not menu.active
            if menu.active: render(menu.get())
            return

        try: pannels.packages[menu.selected].btn()
        except AttributeError: return print(f"System:  {menu.selected} doesn't support buttons")
        return render(pannels.packages[menu.selected].get())

    def close(self):
        self.BTN.close()
        self.DIAL.close()

def render(im):
    if properties.ha["display_status"]: display.render(im)
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

    properties.pannels = pannels
    menu.setup()

    has_ws.setup()
    display.setup()
    virtual_display.setup(1337, dials=dials, allow_cors=True)

    # Render loop
    while True:
        start = time.time()
        if "Spotify" in pannels.packages: autoSelector()

        try:
            render(menu.get() if menu.active else pannels.packages[menu.selected].get())
            compTime = time.time() - start
            # print(compTime)
            time.sleep(frameTime - min(frameTime-0.01, compTime))
        except KeyboardInterrupt as E: break
        except Exception as e:
            print(f"System:  Error: {e}", traceback.format_exc())
            render(error.get())
            time.sleep(2)

    for d in dials: d.close()
    display.render(properties.getBlankIM()[0])
    exit("System:  Stopping...")