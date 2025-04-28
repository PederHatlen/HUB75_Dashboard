import functions, pannels
from PIL import Image, ImageDraw
from functions import color

small05 = functions.font["small05"]

selected = "Weather" # Default pannel can be sett here
active = False

DISPLAY_DEBUG = True

PADDX = 4
PADDY = 3

menuColor = {
    "sys":color["lightred"],
    "dev":color["yellow"],
    "fun":color["purple"],
    "info":color["green"],
    "DEFAULT":"#444"
}

PNames = [p for p in pannels.__all__ if DISPLAY_DEBUG or p not in pannels.menu["dev"]]

allDirs = list(pannels.menu.keys())
if not DISPLAY_DEBUG: allDirs.remove("dev")

titleLength = max([small05.getlength(dir) for dir in allDirs])

def dial(dir):
    global selected
    selectedI = PNames.index(selected)
    if dir == "0R": selected = PNames[(selectedI+1)% len(PNames)]
    elif dir == "0L": selected = PNames[((selectedI-1) if selectedI > 0 else len(PNames)-1)]

# def menuTurn(dir): 
#     global menuActive, menuSelected, autoSelected
#     if not menuActive: return menuDial.dial(dir)
#     elif dir == "1R": menuSelected = (menuSelected+1) % len(pannels.packages)
#     elif dir == "1L": menuSelected = ((menuSelected-1) if menuSelected > 0 else len(pannels.packages)-1)
#     autoSelected = False
#     render(menu())

def old_get():
    im, d = functions.getBlankIM()

    for i in range(len(pannels.packages)):
        x, y = ((i*4)%64), ((i//64)*4)
        if PNames[i] == selected: d.rectangle(((x, y), (x+2, y+2)), "#fff")
        tColor = menuColor[pannels.menuINV[PNames[i]]] if (pannels.menuINV[PNames[i]] in menuColor) else "#aaa"
        d.point((x+1, y+1), tColor)

    tColor = menuColor[pannels.menuINV[selected]] if (pannels.menuINV[selected] in menuColor) else "#aaa"
    d.text((0, 8), pannels.menuINV[selected], tColor, small05)
    d.text((0, 16), selected, "#fff", small05)

    return im

def get():
    im, d = functions.getBlankIM()

    for i in range(len(allDirs)):
        dir = allDirs[i]
        dirColor = menuColor[dir] if dir in menuColor else menuColor["DEFAULT"]

        if selected in pannels.menu[dir]:
            d.rectangle(((PADDX, (i*7)+PADDY-1), (titleLength+PADDX, (i*7)+PADDY+5)), dirColor)
            d.text((PADDX+1, (i*7)+PADDY), dir, "#000", small05)

            chunk = range(len(pannels.menu[dir]))
            if len(chunk) > 4:
                chunkN = (pannels.menu[dir].index(selected)//4)
                chunk = range(chunkN*4, min(len(pannels.menu[dir]), (chunkN*4)+4))

                if len(pannels.menu[dir]) > (chunkN*4)+4: 
                    LC, BC = functions.hex2rgb(dirColor), (0,0,0)
                    arrowIcon = functions.imFromArr([[LC,BC,LC],[BC,LC,BC]])
                    im.paste(arrowIcon, (int(titleLength+(2*PADDX)+1), 30))
            for j in chunk:
                tcolor = dirColor if selected == pannels.menu[dir][j] else "#fff"
                d.text((2*PADDX+titleLength+1, 7*(j%4)+PADDY), pannels.menu[dir][j], tcolor, small05)
        else: d.text((PADDX+1, (i*7)+PADDY), dir, "#fff", small05)

        for i in range(len(PNames)):
            color = menuColor[pannels.menuINV[PNames[i]]] if (pannels.menuINV[PNames[i]] in menuColor) else menuColor["DEFAULT"]
            d.point((1, PADDY+i), color)
            if PNames[i] == selected: d.point((2, PADDY+i), "#fff")
    return im