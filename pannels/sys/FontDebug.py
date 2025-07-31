import functions

small05 = functions.font["small05"]

def get():
    im, d = functions.getBlankIM()

    d.multiline_text((1,1), "ABCDEFGHIJKLMNO\nPQRSTUVWXYZÆØÅ\n0123456789", spacing=2, font=small05)

    for c in range(len(functions.color.keys())):
        d.rectangle(((4*c + 1, 23), (4*c + 4, 28)), fill=list(functions.color.values())[c])

    return im