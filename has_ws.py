"""
TO USE THIS EXTENSION

You need to add this to your secrets.json file in the project-root

"has": {
    "access_token": "[Long-lived access tokens from thge security tab in user settings]"
    "ip":"[IP:PORT of your homeassistant instance]"
    "devices": {
        "[local friendly alias, accessible from all pannels]": "[template string getting only the value]"
        ...
    }
}

The devices specified will be listened to by the program and will be
Only the result of their templates and the local friendly alias will be surfaced in the properties.ha object

"""

import properties, threading, json, time, traceback
from websockets.sync.client import connect

def ha_data_thread():
    global properties
    while True:
        ws = ""
        try:
            ws = connect(f"ws://{properties.secrets["has"]["ip"]}/api/websocket")
            print("Connected to WebSocket")
            while True:
                time.sleep(0.1)
                message = json.loads(ws.recv())
                # print(message)
                if "type" not in message: continue
                elif message["type"] == "auth_required": ws.send(f'{{"type":"auth","access_token":"{properties.secrets["has"]["access_token"]}"}}')
                elif message["type"] == "auth_ok":
                    print("Successfully authorized with HA")
                    ws.send(f'{{"id":1,"type":"render_template","template":"{{{{{",".join(properties.secrets["has"]["devices"].values())}}}}}"}}')
                elif (message["type"] == "event" and "id" in message and message["id"] == 1):
                    for i, d in enumerate(properties.secrets["has"]["devices"].keys()): properties.ha[d] = message["event"]["result"][i]
                    print(f"HA State updated: {', '.join([str(x) for x in message["event"]["result"]])}")
        except Exception as e: print(f"HA: Disconnected from WS... reconnecting in 5s {traceback.format_exc()}")
        if ws != "": ws.close(code=1000, reason="Something messed up here sry")
        time.sleep(5)

def setup(): threading.Thread(target=ha_data_thread, name="HAS Websocket", daemon=True).start()
