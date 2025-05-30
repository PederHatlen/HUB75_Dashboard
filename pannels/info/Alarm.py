import functions, datetime

small05 = functions.font["small05"]
large10 = functions.font["large10"]

TL = (4,4)
BR = (27, 27)

START_DEG = -90

endTime = None
startTime = None

hasEnded = False

setSel = 0
setSelColor = functions.color["orange"]
setSelColorInp = functions.color["lightred"]
setSelIsInp = False

hour, minute = 0, 0

def dial(e):
    global hour, minute, setSel, setSelIsInp
    if setSelIsInp:
        if setSel == 0:
            if e == "1R": hour = (hour+1)%24
            elif e == "1L": hour = (hour-1 if hour > 0 else 24)
        if setSel == 1:
            if e == "1R": minute = (minute+1)%60
            elif e == "1L": minute = (minute-1 if minute > 0 else 59)
    else:
        if e == "1R": setSel = (setSel+1)%3
        elif e == "1L": setSel = (setSel-1 if setSel > 0 else 2)

def btn():
    global setSelIsInp, setSel, startTime, endTime, hasEnded, hour, minute

    if hasEnded or (not hasEnded and endTime != None):
        endTime = None
        startTime = None
        hasEnded = False
        return

    if setSel == 2:
        startTime = datetime.datetime.now()
        endTime = startTime + datetime.timedelta(hours=hour, minutes=minute)
        hour, minute, setSel = 0, 0, 0
        if (endTime - startTime).total_seconds() <= 0:
            endTime = None
            startTime = None
            hasEnded = True
    else:
        setSelIsInp = not setSelIsInp

def selectTime():
    im, d = functions.getBlankIM()

    d.text((20,4),"H", font=large10, fill="#fff")
    d.text((48,4),"M", font=large10, fill="#fff")

    col = setSelColorInp if setSelIsInp else setSelColor

    d.text((4,4),str(hour).rjust(2,"0"), font=large10, fill=(col if setSel == 0 else "#fff"))
    d.text((32,4),str(minute).rjust(2,"0"), font=large10, fill=(col if setSel == 1 else "#fff"))

    d.text((32,24),"Start", font=small05, anchor="mm", fill=(col if setSel == 2 else "#fff"))

    return im

def ended():
    im, d = functions.getBlankIM()
    d.text((32,16), "ENDED!!", fill=functions.color["orange"], font=large10, anchor="mm")

    return im


def get():
    global startTime, endTime, hasEnded

    if hasEnded: return ended()
    if endTime == None: return selectTime()

    currentFraction = (datetime.datetime.now() - startTime).total_seconds() / (endTime - startTime).total_seconds()

    # print(currentFraction)

    if currentFraction > 1:
        endTime = None
        hasEnded = True
        return ended()
    
    im, d = functions.getBlankIM()
    # d.text((32,1), "Alarm", font=small05)s

    d.arc((TL, BR), 0, 360, fill="#aaa", width=3)
    d.arc((TL, BR), START_DEG, (360 * currentFraction) + START_DEG, fill=functions.color["orange"], width=3)

    timeLeft = (endTime - datetime.datetime.now()).total_seconds()

    # timeStr = f"{int(timeLeft//3600)} {int((timeLeft%3600)//60)} {int(timeLeft%60):0>2}"

    # timeStr = f"{int(timeLeft//3600)}H  " if int(timeLeft//3600) != 0 else ""
    # timeStr += f"{int((timeLeft%3600)//60):0>2}M  {int(timeLeft%60):0>2}S"
    # d.text((64,1), timeStr, font=small05, anchor="ra")

    lableColor = functions.color["orange"]
    d.text((63, 1), "S", fill=lableColor, font=small05, anchor="ra")
    d.text((50, 1), "M", fill=lableColor, font=small05, anchor="ra")
    d.text((35, 1), "H", fill=lableColor, font=small05, anchor="ra")

    d.text((59, 1), f"{int(timeLeft%60):0>2}", font=small05, anchor="ra")
    d.text((44, 1), f"{int((timeLeft%3600)//60):0>2}", font=small05, anchor="ra")
    d.text((31, 1), f"{int(timeLeft//3600)}", font=small05, anchor="ra")

    d.text((64,8), endTime.strftime('%H:%M'), font=small05, anchor="ra")

    # d.text((32,), , font=small05)

    return im