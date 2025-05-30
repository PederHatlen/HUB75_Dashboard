import secrets, flask_socketio, flask, threading, io

pannelSocket = ""
def setPannelConnection(pannels):
    global pannelSocket
    print("Virtual display got pannel socket")
    pannelSocket = pannels

def run(port, host="0.0.0.0", allow_cors=False):
    app=flask.Flask(__name__)
    app.config['SECRET_KEY']=secrets.token_urlsafe(16)

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

    @app.route("/api/<path:path>")
    def api(path=""):
        if path == "spotifycover":
            img_io = io.BytesIO()
            
            pannelSocket.packages["Spotify"].currentCover.save(img_io, "PNG")
            img_io.seek(0)
            
            return flask.send_file(img_io, mimetype="image/png")
        
    print("Starting web server!")
    threading.Thread(target=(lambda:socketio.run(app=app, port=port, host=host, debug=False))).start()
    return socketio