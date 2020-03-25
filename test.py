import requests
from base64 import b64encode
import json

code = "wCsFjW1bAa_WK1hjw7TRJKTJOuZdHdN2A"
GET_ACCESS_TOKEN_URL = "https://api.zoom.us/oauth/token"
REDIRECT_URI = "https://mevudadim.herokuapp.com/"

res = requests.post(
    url=GET_ACCESS_TOKEN_URL,
    data={
        "grant_type": 'authorization_code',
        "code": code,
        "redirect_uri": REDIRECT_URI
    },
    headers={
        "Authorization": b"Basic " + b64encode(("%s:%s" % (
            "QI59uv99QfN8pRb0AAqVA",
            "E72ROBhkuqQAzKeio07Pw1qeMwXqCtpL"
        )).encode())
    }
)
values = json.loads(res.text)
access_token = values["access_token"]
print(access_token)

url = "https://api.zoom.us/v2/users/me/meetings"

querystring = {"page_number": "0", "page_size": "30", "type": "live"}

headers = {'authorization': 'Bearer ' + access_token}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)
