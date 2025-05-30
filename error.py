from functions import *

large10 = font["large10"]
im, d = getBlankIM()
d.text((32,16), "ERROR!", font=large10, anchor="mm", fill=color["lightred"])

def get(): return im