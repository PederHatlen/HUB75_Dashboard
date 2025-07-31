import functions, requests, re
from datetime import datetime, timedelta

small05 = functions.font["small05"]

r = requests.get("https://www.nbim.no/no/")
key = re.findall('data-key="[0-9a-f-]+"', r.text)[0][len('data-key="'):-1]

nextDataTS = datetime.now()
dataChange = []
graphData = []
nbimValues = []

def lerp(x, y, points):
    diff = y-x
    return [x + ((diff/points)*i) for i in range(points)]

def normalization(data, tMin=0, tMax=24):
    # https://stats.stackexchange.com/questions/281162/scale-a-number-between-a-range
    rMin, rMax = min(data), max(data)
    if len(data) <= 1 or (rMax - rMin) == 0: return data
    nData = []
    for i in range(len(data)): nData.append(((data[i]-rMin)/(rMax - rMin)) * (tMax - tMin) + tMin)
    return nData

def newData(lerpPoints = 0):
    global key, nbimValues
    if key == "": return False
    r = requests.get(f"https://www.nbim.no/LiveNavHandler/Current.ashx?l=no{f'&PreviousNavValue={nbimValues[0]}' if len(nbimValues) else ''}&key={key}")
    if r.status_code != 200: return False

    data = r.json()
    key = data["d"]["liveNavList"][0]["key"]
    values = [int(re.sub(" ", "", datapoint["Value"])) for datapoint in data["d"]["liveNavList"][0]["values"]]

    # print(data)

    if lerpPoints == 0: return values

    lerpedValues = []
    for i in range(1, len(values)): lerpedValues.extend(lerp(values[i-1], values[i], 10))
    return lerpedValues + [values[-1]]

def get():
    global nextDataTS, nbimValues, dataChange, graphData

    im, d = functions.getBlankIM()

    # Countdown until data expires
    dataExpired = (nextDataTS - datetime.now()).total_seconds()
    if dataExpired <= 0:
        nbimValues = newData(10)
        dataChange = dataChange[-62:] + [(((nbimValues[-1]-nbimValues[0])/abs(nbimValues[0]))*100)]

        dataChangeApplied = [dataChange[0]]
        for i in range(1, len(dataChange)): dataChangeApplied.append(dataChange[i]+dataChangeApplied[i-1])
    
        graphData = [] if len(dataChange) <= 1 else normalization(dataChangeApplied, 1, 18)
        nextDataTS = datetime.now() + timedelta(seconds=len(nbimValues)//10)

        # print(dataChange)

    # Graph
    if len(graphData) > 1:
        for x in range(1, len(graphData)):
            d.line(((x, 31 - graphData[x-1]), (x, 31 - graphData[x])), "#0F0" if graphData[x-1] < graphData[x] else "#F00")

    d.point((len(nbimValues)//10-dataExpired, 31))
    d.text((1, 1), f'Oljefondet', "#0093b5", font=small05, spacing=2)
    d.text((1, 7), f'{int(nbimValues[-int(dataExpired*10)])}', "#FFF", font=small05, spacing=2)
    return im
