import functions

x, y = 32, 16

drawing = [(x,y),]

def get():
    im, d = functions.getBlankIM()
    d.point(drawing, "#fff")
    return im

def dial(e):
    print(e)
    global x, y
    if e == "0R":   x += (1 if x < 63 else 0)
    elif e == "0L": x -= (1 if x > 0 else 0)
    elif e == "1R": y += (1 if y < 31 else 0)
    elif e == "1L": y -= (1 if y > 0 else 0)
    if (x, y) not in drawing: drawing.append((x,y))

def btn(): 
    global drawing
    print("Clearing")
    drawing = [(x, y)]