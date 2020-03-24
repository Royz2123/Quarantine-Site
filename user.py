import requests
from base64 import b64encode
import json

REDIRECT_URI = "https://mevudadim.herokuapp.com/"
CLIENT_APP_ID = "dHLRYFE5QhadcBZZLYMf6w"
CLIENT_APP_SECRET = "hsnqJxcFCAjiRH2aIHLrVYHk4R9P61U1"

USER_AUTH_URL = (
    "https://zoom.us/oauth/authorize?"
    + "response_type=code"
    + "&client_id=" + CLIENT_APP_ID
    + "&redirect_uri=" + REDIRECT_URI
)
GET_ACCESS_TOKEN_URL = "https://api.zoom.us/oauth/token"
USER_INFO_URL = 'https://api.zoom.us/v2/users/me'



class User(object):
    # Every user starts with a code that we get after authorization

    def __init__(self, code):
        self._code = code

        self._access_token = None
        self._refresh_token = None
        self.get_user_access_token()

        self._user_info = self.get_user_info()

    # Returns dictionary of auth headers
    def get_auth_headers(self):
        return {
            "Authorization" : b"Basic " + b64encode(("%s:%s" % (
                CLIENT_APP_ID,
                CLIENT_APP_SECRET
            )).encode())
        }

    def get_user_access_token(self):
        res = requests.post(
            url=GET_ACCESS_TOKEN_URL,
            data={
                "grant_type": 'authorization_code',
                "code": self._code,
                "redirect_uri": REDIRECT_URI
            },
            headers=self.get_auth_headers()
        )
        values = json.loads(res.text)
        print(values)

        self._access_token = values["access_token"]
        self._refresh_token = values["refresh_token"]

    def refresh_user_access_token(self):
        res = requests.post(
            url=GET_ACCESS_TOKEN_URL,
            data={
                "grant_type": 'refresh_token',
                "refresh_token": REDIRECT_URI
            },
            headers=self.get_auth_headers()
        )
        values = json.loads(res.text)
        print(values)

        self._access_token = values["access_token"]
        self._refresh_token = values["refresh_token"]

    def get_user_info(self):
        res = requests.get(
            url=USER_INFO_URL,
            headers = {
                "Authorization": "Bearer %s" % self._access_token
            }
        )
        data = res.json()
        return data

user1 = User('3XvHN12EwC_WK1hjw7TRJKTJOuZdHdN2A')
