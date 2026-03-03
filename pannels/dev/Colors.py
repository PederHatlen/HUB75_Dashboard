import properties
c = 0
def dial(e):
    global c
    c = (c + (1 if e[1] == "R" else -1))%3

def get(): return properties.getBlankIM((255*(c==0),255*(c==1),255*(c==2)))[0]