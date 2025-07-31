import functions

small05 = functions.font["small05"]
color = 0

def dial(e):
    global color
    color = (color + (1 if e[1] == "R" else -1))%3


def get(): return functions.getBlankIM(functions.rgb2hex([255 if color == i else 0 for i in range(3)]))[0]