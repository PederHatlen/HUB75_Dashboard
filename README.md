# Matrix LED display - Dashboard

This is a system meant to be run on a matrix LED display connected to something like the Raspberrypi.  
It is under development, and i have not implemented the acctuall display part yet (i havent received it yet).  
There is however a verry basic (and probably insecure) simulator/viewer implemented.  
My display is 64x32, It works good, havent made my pannels scaleable but shouldnt be hard to implement.

## NOTE

This is a hobby project, i have not prioritized code optimizations or cleanness.  
I'm just having fun here : )

## What you need

* A raspberrypi (tested on RPI-5)
* Rotary encoders (Can be however manny you want, i use 3 (2 properties, 1 menu))
* A matrix LED display (available on ebay, aliexpres, etc. for cheap and from waveshare or genneral hobby-electronics stores at less risk)
    * I use a pitch of P3 (mm between pixels)
    * 64px x 32px ~ 200mm x 100mm
* 3D Printer, or access to one

## Features

* Spotify Integration (Has to be set up, follow guide not written yet :) )
* Sun-possition screen (This took a whole day, please use)
* Menu system
* Make your own pannels!
  * The rendering function takes a matrix of hex values, PIL Image to Matrix function is also supplied in the functions package.
  * The pannel is automatically picked up when in the pannels folder.

## Dependencies

gpiozero flask_socketio flask Pillow numpy (astral psutil docker, for sky and system pannels)

"""
python3 -m pip install flask-socketio pillow numpy astral psutil docker
"""

## Images
Spotify Integration (The text scroll, I promise)
![Spotify Integration](./images/Spotify_Illustration.png)
Sun Integration
![Sun Integration](./images/Sun_Illustration.png)


# BarrelJack Pinout:

Outside = Long  = GND
Pin     = short = VC+

# In Adafruit Piomatter

the file pins.h must be changed before compilation, to include the pin layout  
I use this one: 
```
struct adafruit_matrix_bonnet_pinout {
    static constexpr pin_t PIN_RGB[] = {2,3,4,17,27,22};
    static constexpr pin_t PIN_ADDR[] = {14,15,18,23};
    static constexpr pin_t PIN_OE = 24;   // /OE: output enable when LOW
    static constexpr pin_t PIN_CLK = 10; // SRCLK: clocks on RISING edge
    static constexpr pin_t PIN_LAT = 9; // RCLK: latches on RISING edge
```

RPI Pinouts:  
```
(LVL) 3V  |#   #|  .   (5V)
      R1  |2   #|  .   (5V)
      G1  |3   #|  .   (GND)
      B1  |4  14|  A
(GND)  .  |#  15|  B
      R2  |17 18|  C
      G2  |27  #|  .   (GND)
      B2  |22 23|  D
(LVL) 3V  |#  24|  OE
     CLK  |10  #|  .   (GND)
     LAT  |9  25|  .
```

HUB75 Connector pinout:  

```
 R1   |X X|   G1
 B1   |X #|   GND
 R2   |X X|   G2
 B2  [ X #|   NC
  A  [ X X|   B
  C   |X X|   D
CLK   |X X|   LAT
 OE   |X #|   GND
```