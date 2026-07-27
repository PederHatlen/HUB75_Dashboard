from urllib.parse import urlencode, urlparse, parse_qs
import json, base64, requests

redirect_uri = "http://127.0.0.1:1337/"

with open("./secrets.json", "r") as fi: secret = json.load(fi)["spotify"]
clientCode = base64.b64encode(f"{secret['client_id']}:{secret['client_secret']}".encode()).decode('utf-8')

scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming'

params = urlencode({
    "response_type": "code",
    "client_id": secret["client_id"],
    "scope": scope,
    "redirect_uri": redirect_uri
})
authed = parse_qs(urlparse(input(f"Go to this URL:\nhttps://accounts.spotify.com/authorize?{params}\n\nThe resulting redirect url?: ")).query)

res = requests.post("https://accounts.spotify.com/api/token",
    data={
        "code": authed["code"],
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    },
    headers={
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': f"Basic {clientCode}"
    }
).json()

print(res)
