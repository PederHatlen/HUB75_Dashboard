import properties, random

class trail:
    def __init__(self, x = "", y = ""):
        self.x = x if x != "" else random.randint(0, 63)
        self.y = y if y != "" else random.randint(0, 48)
        
        self.speed = random.randint(5, 20)/10
        self.length = random.randint(8, 32)

trails = [trail() for i in range(128)]

def get():
    im, d = properties.getBlankIM()

    remove = []

    for t in trails:
        mY = round(t.y)

        d.point((t.x, mY), "#fff")#f"#{hex(t.shade)[2:]*3}")
        for y in range(1, t.length-1):
            shade = hex(round(((t.length-y)/t.length)*255))[2:].rjust(2,'0')
            d.point((t.x, mY - y), f"#00{shade}00")

        if mY >= 32+t.length: remove.append(t)
        t.y += t.speed
    
    for t in remove:
        trails.remove(t)
        trails.append(trail(y=0))

    return im