from flask import Flask, request, render_template, make_response
import json

import zoom_user

app = Flask(__name__, template_folder="./templates", static_folder="./static")

users = []
rooms = []

def debug():
    print("ROOMS: ", rooms)
    print("USERS: ", users)

@app.route('/', methods=["GET"])
def homepage():
    global rooms
    global users

    # get the user code
    code = request.args.get("code")
    username = request.cookies.get("username")

    # check for cookie
    if username is not None:
        # continue if in database
        user_dict = Users.query.filter(Users.name == username).first()

        if user_dict is not None:
            resp = make_response(render_template(
                'index.html',
                greeting="Welcome %s" % username,
            ))
            resp.set_cookie("username", username)

            print("\n\nUSED COOKIE\n")
            return resp

    # check if this is a new user in the site, and if so add to the db of users
    if code is not None:
        try:
            new_user = zoom_user.User(code=code)
            username = "%s %s" % (
                new_user.account_info["first_name"],
                new_user.account_info["last_name"],
            )
            new_user_db = Users(name=username, access_token=new_user.access_token, refresh_token=new_user.refresh_token)
            db.session.add(new_user_db)
            db.session.commit()

            resp = make_response(render_template(
                'index.html',
                greeting="Welcome %s" % username,
            ))
            resp.set_cookie("username", username)

            print("\n\nUSED CODE\n")
            return resp
        except Exception as e:
            print("User probably already logged in: " + str(e))


    resp = make_response(render_template(
        'index.html',
        greeting="LOG IN",
    ))
    resp.set_cookie("username", username)
    return resp


@app.route('/enter_room_first', methods=["POST", "GET"])
def enter_room():
    global rooms
    global users

    username = request.cookies.get("username")

    # get user object from list / db
    user_dict = [user for user in users if user["name"] == username][0]
    user_obj = zoom_user.User(tokens=(user_dict["access_token"], user_dict["refresh_token"]))
    print("GOT USER %s" % str(user_obj))

    meeting = user_obj.create_meeting()

    floor_num = request.args.get("floor")
    if floor_num is None:
        floor_num = 2

    try:
        room_obj = {
            "room_id": request.args.get("room_id"),
            "room_name": request.args.get("room_name"),
            "meeting_name": request.args.get("topic"),
            "meeting_id": meeting["pmi"],
            "floor": floor_num,
            "join_url": meeting["join_url"],
            "participants": [username],
        }
        rooms.append(room_obj)
    except Exception as e:
        print("\nERROR, Overused the Create:\t" + str(meeting))

    debug()
    return str(meeting)


@app.route('/update_floor', methods=["GET"])
def update_floor():
    global rooms
    global users

    floor_num = request.args.get("floor")
    username = request.cookies.get("username")

    if floor_num is None:
        floor_num = 2

    print(rooms)

    floor_rooms = [{
        "room_id": room["room_id"],
        "room_name": room["room_name"],
        "link": room["join_url"],
        "participants_names": room["participants"],
        "meeting_name": room["meeting_name"]
    } for room in rooms if room["floor"] == floor_num]
    content = {
        "username": username,
        "rooms": floor_rooms
    }
    debug()
    return json.dumps(content)




@app.route('/participant_joined', methods=["POST"])
def participant_joined():
    global rooms
    global users

    print("\nPARTICIPANT JOINED:\t" + str(request.data))
    content = json.loads(request.data)

    meeting_id = content["payload"]["object"]["id"]

    # Search
    possible_meetings = [room for room in rooms if room["meeting_id"] == meeting_id]
    print("\nPOSSIBLE MEETINGS:\t" + str(possible_meetings))

    if len(possible_meetings) != 0:
        username = content["payload"]["object"]["participant"]["user_name"]
        # TODO: username to FIRST and LAST name
        possible_meetings[0]["participants"].append(username)
    return "Finished"


@app.route('/participant_left', methods=["POST"])
def participant_left():
    global rooms
    global users

    print("\nPARTICIPANT LEFT:\t" + str(request.data))
    content = json.loads(request.data)

    meeting_id = content["payload"]["object"]["id"]

    # Search
    possible_meetings = [room for room in rooms if room["meeting_id"] == meeting_id]
    print("\nPOSSIBLE MEETINGS:\t" + str(possible_meetings))

    if len(possible_meetings) != 0:
        try:
            username = content["payload"]["object"]["participant"]["user_name"]
            # TODO: username to FIRST and LAST name
            possible_meetings[0]["participants"].remove(username)
        except Exception as e:
            print(e)
    return "Finished"


@app.route('/meeting_ended', methods=["POST"])
def meeting_ended():
    global rooms
    global users

    print("\nMEETING ENDED:\t" + str(request.data))
    content = json.loads(request.data)

    meeting_id = content["payload"]["object"]["id"]

    # Search and remove all meetings that are not in the meeting id
    rooms = [room for room in rooms if room["meeting_id"] != meeting_id]
    return "Finished"

if __name__ == '__main__':
    app.run()