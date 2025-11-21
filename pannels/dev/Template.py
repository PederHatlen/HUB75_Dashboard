import properties

def get():
    im, d = properties.getBlankIM()
    d.multiline_text((1,1), "Nothing to see \nhere", font=properties.font[5])

    return im