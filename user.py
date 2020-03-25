import json
from zoomus import ZoomClient

client = ZoomClient('BLJi4nPkTLisS1-Og8xgtw', 'MxOrCn5y52r6LqN73Vddprs0XwIpn5Hfq0Jb')

user_list_response = client.user.list()
print(user_list_response.content)
user_list = json.loads(user_list_response.content)

for user in user_list['users']:
    user_id = user['id']
    print(json.loads(client.meeting.list(user_id=user_id).content))
    # print(client.meeting.create(user_id=user_id, ).content)