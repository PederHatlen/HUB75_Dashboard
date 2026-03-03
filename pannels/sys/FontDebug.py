import properties

def get():
    im, d = properties.getBlankIM()

    d.multiline_text((1,1), "ABCDEFGHIJKLMNO\nPQRSTUVWXYZÆØÅ\n0123456789", spacing=2, font=properties.font[5])

    for c in range(len(properties.color.keys())):
        d.rectangle(((4*c + 1, 23), (4*c + 4, 28)), fill=list(properties.color.values())[c])

    return im