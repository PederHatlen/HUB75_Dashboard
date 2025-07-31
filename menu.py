import functions

small05 = functions.font["small05"]

selected = "Weather" # Default pannel can be sett here
active = False

DISPLAY_DEBUG = True

PADDX, PADDY = 4, 3

menuColor = {
    "sys":functions.color["lightred"],
    "dev":functions.color["yellow"],
    "fun":functions.color["purple"],
    "info":functions.color["green"],
    "DEFAULT":"#444"
}

pannels = ""
pannelList, folderList = [], []

def setup(pannelsIn):
    global pannels, pannelList, folderList
    pannels = pannelsIn

    pannelList = [p for p in pannels.__all__ if DISPLAY_DEBUG or p not in pannels.folders["dev"]]
    folderList = [f for f in pannels.dirs if DISPLAY_DEBUG or f != "dev"]

def dial(dir):
    global selected
    selectedI = pannelList.index(selected)
    if dir == "0R": selected = pannelList[(selectedI+1)% len(pannelList)]
    elif dir == "0L": selected = pannelList[((selectedI-1) if selectedI > 0 else len(pannelList)-1)]

def get():
    im, d = functions.getBlankIM()

    titleLength = max([small05.getlength(dir) for dir in folderList])

    for i in range(len(folderList)):
        dir = folderList[i]
        if dir == "dev" and not DISPLAY_DEBUG: continue

        dirColor = menuColor[dir] if dir in menuColor else menuColor["DEFAULT"]

        if selected in pannels.folders[dir]:
            d.rectangle(((PADDX, (i*7)+PADDY-1), (titleLength+PADDX, (i*7)+PADDY+5)), dirColor)
            d.text((PADDX+1, (i*7)+PADDY), dir, "#000", small05)

            chunk = range(len(pannels.folders[dir]))
            if len(chunk) > 4:
                chunkN = (pannels.folders[dir].index(selected)//4)
                chunk = range(chunkN*4, min(len(pannels.folders[dir]), (chunkN*4)+4))

                if len(pannels.folders[dir]) > (chunkN*4)+4: 
                    LC, BC = functions.hex2rgb(dirColor), (0,0,0)
                    arrowIcon = functions.imFromArr([[LC,BC,LC],[BC,LC,BC]])
                    im.paste(arrowIcon, (int(titleLength+(2*PADDX)+1), 30))
            for j in chunk:
                tcolor = dirColor if selected == pannels.folders[dir][j] else "#fff"
                d.text((2*PADDX+titleLength+1, 7*(j%4)+PADDY), pannels.folders[dir][j], tcolor, small05)
        else: d.text((PADDX+1, (i*7)+PADDY), dir, "#fff", small05)

        for i in range(len(pannelList)):
            color = menuColor[pannels.foldersINV[pannelList[i]]] if (pannels.foldersINV[pannelList[i]] in menuColor) else menuColor["DEFAULT"]
            d.point((1, PADDY+i), color)
            if pannelList[i] == selected: d.point((2, PADDY+i), "#fff")
    return im