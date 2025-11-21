import properties

def get():
    im, d = properties.getBlankIM()
    # d.multiline_text((0,0), "Nothing to see \nhere", font=small05)

    # White
    d.rectangle((0,0, 64,32), fill="#fff")

    # Red left
    d.rectangle((0, 0, 12, 11), fill="#BA0C2F")     # Top Left
    d.rectangle((0, 20, 12, 32), fill="#BA0C2F")    # Bottom Left

    # Red right
    d.rectangle((21, 0, 64, 11), fill="#BA0C2F")    # Top Right
    d.rectangle((21, 20, 64, 32), fill="#BA0C2F")   # Bottom Right

    # blue
    d.rectangle((0, 14, 64, 17), fill="#00205B")   # Horizontal line
    d.rectangle((15, 0, 18, 32), fill="#00205B")   # Vertical line

    return im

# 32*44 +20

# 22
# 6+1+2+1+12
# 12+2+4+2+24