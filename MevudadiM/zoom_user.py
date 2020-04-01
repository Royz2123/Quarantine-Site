#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from base64 import b64encode
import json
import datetime

REDIRECT_URI = "http://5c3d600f.ngrok.io/"
REDIRECT_URI = "https://mevudadim.herokuapp.com/"

# ACCOUNT_CLIENT_APP_ID = "V3gUdgJnRTqkJZPHGyIczw"
# ACCOUNT_CLIENT_APP_SECRET = "I1ahJBhuGEr6DLHwMwCgJqf6tjuoGwKY"

USER_CLIENT_APP_ID = "QI59uv99QfN8pRb0AAqVA"
USER_CLIENT_APP_SECRET = "E72ROBhkuqQAzKeio07Pw1qeMwXqCtpL"

USER_CLIENT_APP_ID_PROD = "dHLRYFE5QhadcBZZLYMf6w"
USER_CLIENT_APP_SECRET_PROD = "hsnqJxcFCAjiRH2aIHLrVYHk4R9P61U1"

# MODES = (
#     USER_LEVEL,
#     ACCOUNT_LEVEL
# ) = range(2)
# APP_LEVEL = USER_LEVEL
#
# if APP_LEVEL == USER_LEVEL:
CLIENT_APP_ID = USER_CLIENT_APP_ID_PROD
CLIENT_APP_SECRET = USER_CLIENT_APP_SECRET_PROD
# else:
#     CLIENT_APP_ID = ACCOUNT_CLIENT_APP_ID
#     CLIENT_APP_SECRET = ACCOUNT_CLIENT_APP_SECRET

USER_AUTH_URL = (
        "https://zoom.us/oauth/authorize?"
        + "response_type=code"
        + "&client_id=" + CLIENT_APP_ID
        + "&redirect_uri=" + REDIRECT_URI
)
GET_ACCESS_TOKEN_URL = "https://api.zoom.us/oauth/token"
USER_INFO_URL = 'https://api.zoom.us/v2/users/me'
LIST_USERS_URL = 'https://api.zoom.us/v2/accounts/me/users'

LIST_MEETINGS_URL = 'https://api.zoom.us/v2/users/me/meetings'
CREATE_MEETING_URL = 'https://api.zoom.us/v2/users/me/meetings'


def refresh_user_access_token(user):
    res = requests.post(
        url=GET_ACCESS_TOKEN_URL,
        data={
            "grant_type": 'refresh_token',
            "refresh_token": REDIRECT_URI
        },
        headers={
            'authorization': 'Bearer %s' % user.access_token,
            'content-type': "application/json",
        }
    )
    values = json.loads(res.text)
    # print(values)

    user.access_token = values["access_token"]
    user.refresh_token = values["refresh_token"]

class User(object):
    # Every user starts with a code that we get after authorization

    def __init__(self, code=None, tokens=None):
        if tokens is None:
            self._code = code
            self.access_token = None
            self.refresh_token = None
            self.get_user_access_token()
        else:
            self.access_token, self._refresh_token = tokens

        self._account_id = None
        self.account_info = self.get_account_info()

        # self.list_users()
        # self.create_meeting()

        # self.list_meetings()
        # meeting = self.create_meeting()
        # self.list_meetings()

    # Returns dictionary of auth headers
    def get_code_auth_headers(self):
        return {
            "Authorization": b"Basic " + b64encode(("%s:%s" % (
                CLIENT_APP_ID,
                CLIENT_APP_SECRET
            )).encode())
        }

    def get_token_auth_headers(self):
        return {
            'authorization': 'Bearer %s' % self.access_token,
            'content-type': "application/json",
        }

    def get_user_access_token(self):
        res = requests.post(
            url=GET_ACCESS_TOKEN_URL,
            data={
                "grant_type": 'authorization_code',
                "code": self._code,
                "redirect_uri": REDIRECT_URI
            },
            headers=self.get_code_auth_headers()
        )
        values = json.loads(res.text)
        print(values)

        self.access_token = values["access_token"]
        self.refresh_token = values["refresh_token"]

    def refresh_user_access_token(self):
        res = requests.post(
            url=GET_ACCESS_TOKEN_URL,
            data={
                "grant_type": 'refresh_token',
                "refresh_token": REDIRECT_URI
            },
            headers=self.get_token_auth_headers()
        )
        values = json.loads(res.text)
        print(values)

        self.access_token = values["access_token"]
        self.refresh_token = values["refresh_token"]

    def get_account_info(self):
        res = requests.get(
            url=USER_INFO_URL,
            headers=self.get_token_auth_headers()
        )
        data = res.json()
        print(data)
        return data

    def list_users(self):
        res = requests.get(
            url="https://api.zoom.us/v2/users",
            headers=self.get_token_auth_headers()
        )
        data = res.json()
        print(data)

        return data

    def list_meetings(self):
        url = "https://api.zoom.us/v2/users/me/meetings"
        querystring = {"page_number": "0", "page_size": "30", "type": "live"}
        headers = self.get_token_auth_headers()
        response = requests.request("GET", url, headers=headers, params=querystring)
        print("\nMEETINGS LIST:\t\t" + response.text)
        return json.loads(response.text)

    def create_meeting(self, name="נפגשים ונהנים"):
        start_time = datetime.datetime.now()
        start_time = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        url = "https://api.zoom.us/v2/users/me/meetings"
        querystring = {
            "topic": name,
            "type": "2",
            "start_time": start_time,
            "duration": "30",
            "timezone": 'Asia/Jerusalem',
            "agenda": "Fun meeting",
            "settings": {
                "host_video": "true",
                "participant_video": "true",
                "join_before_host": "true",
                "use_pmi": "true",
                "mute_open_entry": "false",
                "watermark": "false",
                "approval_type": "0",
                "registration_type": "1",
                "enforce_login": "true",
                "audio": "both",
                "auto_recording": "none",
            },
        }
        headers = self.get_token_auth_headers()
        response = requests.request("POST", url, headers=headers, data=json.dumps(querystring))

        if response.status_code == 429:
            print("TOO MANY REQUESTS:\n" + str(response.text) + str(response.headers))
            return json.loads(response.text)

        print("\nCREATED MEETING:\t" + response.text)
        return json.loads(response.text)

    # def get_meeting_participants(self, meeting_id):
    #     url = "https://api.zoom.us/v2/meetings/%s/registrants" % meeting_id
    #     querystring = {"page_number": "1", "page_size": "30", "status": "approved"}
    #     headers = self.get_token_auth_headers()
    #     response = requests.request("GET", url, headers=headers, params=querystring)
    #     print("\nMEETING PARTICIPANTS:\t" + response.text)
    #     return json.loads(response.text)

    # def create_meeting(self):
    #     res = requests.post(
    #         url=CREATE_MEETING_URL,
    #         data={
    #             "topic": "Test Meeting",
    #             "type": 0,
    #             "agenda": "We will have a nice meeting"
    #         },
    #         headers=self.get_auth_headers()
    #     )
    #     values = json.loads(res.text)
    #     print(values)


if __name__ == "__main__":
    user1 = User('YBV8qQfcZy_WK1hjw7TRJKTJOuZdHdN2A')
    meeting = user1.create_meeting()
