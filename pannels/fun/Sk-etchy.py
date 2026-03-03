import properties

x, y = properties.WIDTH//2, properties.HEIGHT//2
drawing = [(x,y),]

def get():
    im, d = properties.getBlankIM()
    d.point(drawing, "#fff")
    return im

def dial(e):
    # print(e)
    global x, y
    if e == "0R":   x += (1 if x <= properties.WIDTH else 0)
    elif e == "0L": x -= (1 if x > 0 else 0)
    elif e == "1R": y += (1 if y <= properties.HEIGHT else 0)
    elif e == "1L": y -= (1 if y > 0 else 0)
    if (x, y) not in drawing: drawing.append((x,y))

def btn(): 
    global drawing
    print("SkEtchy: Clearing")
    drawing = [(x, y)]