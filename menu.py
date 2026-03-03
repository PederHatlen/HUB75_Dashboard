import properties

selected = "Clocks" # Default pannel can be sett here
active = False

PADDX, PADDY = 4, 3

pannels, pannelList, folderList = "", [], []
def setup():
    global pannels, pannelList, folderList
    pannels = properties.pannels

    pannelList = [p for p in pannels.__all__ if properties.DISPLAY_DEBUG_MENU or p not in pannels.folders["dev"]]
    folderList = [f for f in pannels.dirs if properties.DISPLAY_DEBUG_MENU or f != "dev"]

def dial(dir):
    global selected
    selectedI = pannelList.index(selected)
    if dir == "0R": selected = pannelList[(selectedI+1)% len(pannelList)]
    elif dir == "0L": selected = pannelList[((selectedI-1) if selectedI > 0 else len(pannelList)-1)]

def get():
    im, d = properties.getBlankIM()
    d.font = properties.font[5]

    titleLength = max([properties.font[5].getlength(dir) for dir in folderList])

    for i in range(len(folderList)):
        dir = folderList[i]
        if dir == "dev" and not properties.DISPLAY_DEBUG_MENU: continue

        dirColor = properties.menuColor[dir] if dir in properties.menuColor else properties.menuColor["DEFAULT"]

        if selected in pannels.folders[dir]:
            d.rectangle(((PADDX, (i*7)+PADDY-1), (titleLength+PADDX, (i*7)+PADDY+5)), dirColor)
            d.text((PADDX+1, (i*7)+PADDY), dir, "#000")

            chunk = range(len(pannels.folders[dir]))
            if len(chunk) > 4:
                chunkN = (pannels.folders[dir].index(selected)//4)
                chunk = range(chunkN*4, min(len(pannels.folders[dir]), (chunkN*4)+4))

                if len(pannels.folders[dir]) > (chunkN*4)+4: 
                    LC, BC = dirColor, (0,0,0)
                    arrowIcon = properties.imFromArr([[LC,BC,LC],[BC,LC,BC]])
                    im.paste(arrowIcon, (int(titleLength+(2*PADDX)+1), 30))
            for j in chunk:
                tcolor = dirColor if selected == pannels.folders[dir][j] else "#fff"
                d.text((2*PADDX+titleLength+1, 7*(j%4)+PADDY), pannels.folders[dir][j], tcolor)
        else: d.text((PADDX+1, (i*7)+PADDY), dir, "#fff")

        for i in range(len(pannelList)):
            color = properties.menuColor[pannels.foldersINV[pannelList[i]]] if (pannels.foldersINV[pannelList[i]] in properties.menuColor) else properties.menuColor["DEFAULT"]
            d.point((1, PADDY+i), color)
            if pannelList[i] == selected: d.point((2, PADDY+i), "#fff")
    return im