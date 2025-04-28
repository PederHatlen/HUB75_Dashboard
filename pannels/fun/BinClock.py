import functions, datetime

ps, gap = 4, 2 # Pixel size, pixel gap

def get():
    im, d = functions.getBlankIM()

    now = datetime.datetime.now()
    time = list(f"{str(now.hour).rjust(2,'0')}{str(now.minute).rjust(2,'0')}{str(now.second).rjust(2,'0')}")
    for x, n in enumerate(time):
        for y in range(0,4):
            xc = x*(gap+ps) + (32-(ps*6+gap*5)/2)           # pixel and gap size offsetting + centering on the screen
            yc = (3-y)*(gap+ps) + (16-(ps*4 + gap*3)/2)     # reversing, pixel and gap size offsetting + centering on the screen

            if int(n) | (2**y) == int(n): d.rectangle(((xc,yc), (xc+ps-1,yc+ps-1)), "#fff")     # if number is the same when you turn on bit at n position bit is in number
            elif y<3 or x%2: d.rectangle(((xc,yc), (xc+ps-1,yc+ps-1)), "#222")                  # The times 10 spot should be 1 lower (hour has no need for 3, but it looks bad without)

    return im