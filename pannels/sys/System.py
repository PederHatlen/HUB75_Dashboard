import functions, os, psutil
from functions import color

small05 = functions.font["small05"]

oldframe = ""
fn = 0

graph = {
    "cpu":[],
    "tmp":[],
    "fan":[]
}
graphColors = {
    "cpu":color["mint"],
    "tmp":color["purple"],
    "fan":color["lightblue"]
}

def getColor(value, max=100):
    if (value/max) < 0.25: return color["green"]
    if (value/max) < 0.5: return color["yellow"]
    if (value/max) < 0.75: return color["orange"]
    if (value/max) < 1: return color["red"]
    return color["purple"]

def get():
    global oldframe, fn
    im, d = functions.getBlankIM()

    fn += 1
    if fn % 10 != 0 and oldframe != "": return oldframe

    # d.point([(n,0) for n in range(1,64,2)] + [(0,n) for n in range(1,32,2)], fill="#f00")

    d.text((0, 0), "CPU", fill=graphColors["cpu"], font=small05)
    d.text((0, 7), "TMP", fill=graphColors["tmp"], font=small05)
    d.text((0, 14), "FAN", fill=graphColors["fan"], font=small05)

    cpu = psutil.cpu_percent()
    tmp = round(psutil.sensors_temperatures()['cpu_thermal'][0].current)
    fan = round((psutil.sensors_fans()['pwmfan'][0].current/8000)*100)

    # cpuColor = color["green"] if cpu < 25 else color["orange"] if cpu < 75 else color["red"]
    # tmpColor = color["green"] if tmp < 40 else color["yellow"] if tmp < 60 else color["orange"] if tmp < 80 else color["red"]
    # fanColor = color["blue"]  if fan < 10 else color["green"]  if fan < 50 else color["orange"] if fan < 75 else color["red"]

    d.text((32,0), f"{cpu}%", font=small05, fill=getColor(cpu), anchor="rt")
    d.text((32,7), f"{tmp}C", font=small05, fill=getColor(tmp), anchor="rt")
    d.text((32,14), f"{fan}%", font=small05, fill=getColor(fan), anchor="rt")

    graph["cpu"].append(round(31-(31*(cpu/100))))
    graph["tmp"].append(round(31-(31*(tmp/100))))
    graph["fan"].append(round(31-(31*(fan/100))))

    for p in graph:
        if len(graph[p]) > 32: graph[p] = graph[p][-32:]
        d.line([(i+32, graph[p][i]) for i in range(len(graph[p]))], fill=graphColors[p])

    oldframe = im
    return im