"""
TO USE THIS EXTENSION

You need to add this to your secrets.json file in the project-root

"has": {
    "access_token": "[Long-lived access tokens from thge security tab in user settings]"
    "ip":"[IP:PORT of your homeassistant instance]"
    "devices": {
        "[device]": "[local friendly alias, (not the same as homeassistant friendly name) (this will be accessible for all pannels)]"
        ...
    },
    "spotify_lights":"[homeassistant light group object with all the lights to use with spotify if that is setup]"
}

The devices specified will be listened to by the program
Only their values and the local friendly alias will be surfaced in the properties.ha object and 

"""

import properties, threading, json, re, time
from websockets.sync.client import connect

properties.ha = {"display_status":True, "spotify_lighting": False, "spotify_lights": []}

ws = "", 
def ha_data_thread():
    global ws, prop
    while True:
        try:
            ws = connect(f"ws://{properties.secrets['has']['ip']}/api/websocket")
            print("HASS-WS: Connected to WebSocket")
            while True:
                time.sleep(0.25)
                raw_message = ws.recv(timeout=None)
                message = json.loads(raw_message)
                if "type" not in message: continue
                if message["type"] == "auth_required": ws.send(json.dumps({"type": "auth", "access_token": properties.secrets["has"]["access_token"]}))
                # if message["type"] == "result": print(raw_message)
                if message["type"] == "auth_ok":
                    print("HASS-WS: Successfully authorized with HA")
                    ws.send('{"id": 1, "type": "subscribe_entities", "entity_ids": [' + ", ".join([f'"{x}"' for x in properties.secrets["has"]["devices"].keys()]) + ']}')
                    if properties.secrets["has"]["spotify_lights"]: ws.send('{"id": 2, "type": "subscribe_entities", "entity_ids": ["' + properties.secrets["has"]["spotify_lights"] + '"]}')
                if message["type"] == "event" and "event" in message:
                    if message["id"] == 1:
                        devices = message["event"]["a"] if "a" in message["event"] else message["event"]["c"]
                        for d in devices:
                            value = devices[d]["s"] if "a" in message["event"] else devices[d]["+"]["s"]
                            if value in ["off", "on"]: properties.ha[properties.secrets["has"]["devices"][d]] = (value == "on")
                            else: properties.ha[properties.secrets["has"]["devices"][d]] = float(value)
                    else:
                        entity_ids = re.search(r'(?<=\"entity_id\"\:\[).*?(?=\])', raw_message)
                        if entity_ids: properties.ha["spotify_lights"] = entity_ids[0].replace('"','').split(",")

        except Exception as e: print(f"HASS-WS: Disconnected from HA, trying to reconnect in 5s {e}")
        if ws != "": ws.close(code=1000, reason="Something messed up here sry")
        time.sleep(5)

def setup(): threading.Thread(target=ha_data_thread, name="HAS Websocket", daemon=True).start()