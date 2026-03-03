import secrets, flask_socketio, flask, threading

socketio, lastSentFrame = "", ""

def render(im):
    global lastSentFrame
    newFrame = list(im.getdata())
    if lastSentFrame != newFrame:
        lastSentFrame = newFrame
        socketio.emit("refresh", newFrame)

def setup(port, dials="", host="0.0.0.0", allow_cors=False):
    global socketio
    app=flask.Flask(__name__)
    app.config['SECRET_KEY']=secrets.token_urlsafe(16)
    # logging.getLogger("werkzeug").disabled = True
    # logging.getLogger("geventwebsocket.handler").disabled = True

    @app.route("/v")
    def viewer():return flask.send_file("./web/viewer.html")

    @app.route("/s")
    def slow():return flask.send_file("./web/slow.html")

    @app.route("/")
    @app.route("/<path:path>")
    def index(path="index.html"):
        if "." not in path: path = f"{path}.html"
        return flask.send_from_directory("./web/",path)

    socketio=flask_socketio.SocketIO(app, async_mode='threading', cors_allowed_origins=("*" if allow_cors else ""))

    @socketio.on("connect")
    def onConnect(data=""):
        if lastSentFrame == "": return
        socketio.emit("refresh", lastSentFrame, to=flask.request.sid)
    
    @socketio.on('inp')
    def on_connection(data):
        print(f"VRTDisp: Input from virtual display: {data}") #type:ignore
        if dials != "":
            if "dir" in data and data["dir"][0] in ["0", "1"]: dials[int(data["dir"][0])].dial(data["dir"][1])
            elif "btn" in data and data["btn"] in [0, 1]: dials[data["btn"]].btn()

    print("VRTDisp: Starting web server...")
    socketio_thread = threading.Thread(name="SocketIO server", target=(lambda:socketio.run(app=app, port=port, host=host, debug=False, log_output=True)), daemon=True)
    socketio_thread.start()
    print("VRTDisp: Webserver started!")
    return socketio