from flask import Blueprint, request, render_template, make_response
import json

import MevudadiM.zoom_user as zoom_user

main = Blueprint("main", __name__)

users = []
rooms = []


@main.route('/', methods=["GET"])
def homepage():
    global rooms
    global users

    code = request.args.get("code")

    # TODO: Could be from cookie as well
    # check if this is a new user in the site, and if so add to the db of users
    username = "<Not logged in>"
    if code is not None:
        try:
            new_user = zoom_user.User(code=code)
            username = "%s %s" % (
                new_user.account_info["first_name"],
                new_user.account_info["last_name"],
            )
            users.append({
                "name": username,
                "access_token": new_user.access_token,
                "refresh_token": new_user.refresh_token,
            })
        except Exception as e:
            print("User probably already logged in: " + str(e))

    resp = make_response(render_template(
        'index.html',
        greeting="Welcome %s" % username,
        title="מחזור מ האגדי - דף הבית"
    ))
    resp.set_cookie("username", username)
    return resp


@main.route('/enter_room_first', methods=["POST", "GET"])
def enter_room():
    global rooms
    global users

    username = request.cookies.get("username")

    # get user object from list / db
    user_dict = [user for user in users if user["name"] == username][0]
    user_obj = zoom_user.User(tokens=(user_dict["access_token"], user_dict["refresh_token"]))
    print("GOT USER %s" % str(user_obj))

    meeting = user_obj.create_meeting()

    try:
        room_obj = {
            "room_id": request.args.get("room_id"),
            "meeting_name": request.args.get("topic"),
            "meeting_id": meeting["uuid"],
            "floor": request.args.get("floor"),
            "join_url": meeting["join_url"],
            "participants": [username]
        }
        rooms.append(room_obj)
    except Exception as e:
        print("\nERROR, Overused the Create:\t" + str(meeting))

    return str(meeting)


@main.route('/participant_joined', methods=["POST"])
def participant_joined():
    global rooms
    global users

    print("\nPARTICIPANT JOINED:\t" + str(request.data))
    content = json.loads(request.data)

    meeting_id = content["payload"]["object"]["uuid"]

    # Search
    possible_meetings = [room for room in rooms if room["meeting_id"] == meeting_id]
    print("\nPOSSIBLE MEETINGS:\t" + str(possible_meetings))

    if len(possible_meetings) != 0:
        username = content["payload"]["object"]["participant"]["user_name"]
        # TODO: username to FIRST and LAST name
        possible_meetings[0]["participants"].append(username)
    return "Finished"


@main.route('/participant_left', methods=["POST"])
def participant_left():
    global rooms
    global users

    print("\nPARTICIPANT LEFT:\t" + str(request.data))
    content = json.loads(request.data)

    meeting_id = content["payload"]["object"]["uuid"]

    # Search
    possible_meetings = [room for room in rooms if room["meeting_id"] == meeting_id]

    if len(possible_meetings) != 0:
        username = content["payload"]["object"]["participant"]["user_name"]
        # TODO: username to FIRST and LAST name
        possible_meetings[0]["participants"].remove(username)
    return "Finished"


@main.route('/meeting_ended', methods=["POST"])
def meeting_ended():
    global rooms
    global users

    print("\nMEETING ENDED:\t" + str(request.data))
    content = json.loads(request.data)

    meeting_id = content["payload"]["object"]["uuid"]

    # Search and remove all meetings that are not in the meeting id
    rooms = [room for room in rooms if room["meeting_id"] != meeting_id]
    return "Finished"