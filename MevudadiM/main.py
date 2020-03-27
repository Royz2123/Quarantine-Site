from flask import Blueprint, request, render_template, make_response
import json

import MevudadiM.zoom_user as zoom_user
from MevudadiM.models import *


main = Blueprint("main", __name__)
debug = Blueprint("debug", __name__)


@debug.route('/debug', methods=["GET"])
def debug_func():
    print("Users: ", Users.query.all(), "\n")
    print("Rooms: ", Rooms.query.all(), "\n")


@main.route('/', methods=["GET"])
def homepage():
    # get the user code
    code = request.args.get("code")
    username = request.cookies.get("username")

    print(code, username)

    # check if this is a new user in the site, and if so add to the db of users
    if code is not None:
        try:
            new_user = zoom_user.User(code=code)
            username = "%s %s" % (
                new_user.account_info["first_name"],
                new_user.account_info["last_name"],
            )

            # delete all previous users with this code
            Users.query.filter(Users.name == username).delete(synchronize_session="evaluate")
            db.session.commit()

            new_user_db = Users(name=username, access_token=new_user.access_token, refresh_token=new_user.refresh_token)
            db.session.add(new_user_db)
            db.session.commit()

            resp = make_response(render_template(
                'index.html',
                greeting="Welcome %s" % username,
            ))
            resp.set_cookie("username", username)

            print("\n\nUSED CODE\n")
            debug_func()
            return resp
        except Exception as e:
            print("User probably already logged in: " + str(e))

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
            debug_func()
            return resp

    debug_func()
    resp = make_response(render_template(
        'index.html',
        greeting="LOG IN",
    ))
    return resp


@main.route('/enter_room_first', methods=["POST"])
def enter_room():
    username = request.cookies.get("username")

    user_dict = Users.query.filter(Users.name == username).first()
    user_obj = zoom_user.User(tokens=(user_dict.access_token, user_dict.refresh_token))
    print("GOT USER %s" % str(user_obj))

    meeting = user_obj.create_meeting()

    floor_num = request.form.get("floor")
    if floor_num is None:
        floor_num = 2
    else:
        floor_num = int(floor_num)

    try:
        room_obj = Rooms(
            room_id=request.form.get("room_id"),
            room_name=request.form.get("room_name"),
            meeting_name=request.form.get("topic"),
            meeting_id=meeting["pmi"],
            floor=floor_num,
            join_url=meeting["join_url"],
            participants=json.dumps([]))
        db.session.add(room_obj)
        db.session.commit()

    except Exception as e:
        print("\nERROR, Overused the Create:\t" + str(e))

    debug_func()
    return str(meeting)


@main.route('/update_floor', methods=["GET"])
def update_floor():
    print("UPDATE_FLOOR REQUEST")

    floor_num = request.args.get("floor")
    username = request.cookies.get("username")

    if floor_num is None:
        floor_num = 2
    else:
        floor_num = int(floor_num)

    rooms = Rooms.query.filter(Rooms.floor == floor_num).all()
    floor_rooms = [{
        "room_id": room.room_id,
        "room_name": room.room_name,
        "link": room.join_url,
        "participants_names": room.participants,
        "meeting_name": room.meeting_name
    } for room in rooms]
    content = {
        "username": username,
        "rooms": floor_rooms
    }

    debug_func()
    return json.dumps(content)


@main.route('/participant_joined', methods=["POST"])
def participant_joined():

    print("\nPARTICIPANT JOINED:\t" + str(request.data))
    content = json.loads(request.data)

    meeting_id = content["payload"]["object"]["id"]

    possible_meetings = Rooms.query.filter(Rooms.meeting_id == meeting_id).first()
    print("\nPOSSIBLE MEETINGS:\t" + str(possible_meetings))

    if possible_meetings is not None:
        username = content["payload"]["object"]["participant"]["user_name"]
        # TODO: username to FIRST and LAST name
        possible_meetings.participants = json.dumps(json.loads(possible_meetings.participants) + [username])

    db.session.commit()

    debug_func()
    return "Finished"


@main.route('/participant_left', methods=["POST"])
def participant_left():
    print("\nPARTICIPANT LEFT:\t" + str(request.data))
    content = json.loads(request.data)

    meeting_id = content["payload"]["object"]["id"]

    # Search
    possible_meetings = Rooms.query.filter(Rooms.meeting_id == meeting_id).first()

    if possible_meetings is not None:
        try:
            username = content["payload"]["object"]["participant"]["user_name"]
            # TODO: username to FIRST and LAST name
            tmp = json.loads(possible_meetings[0].participants)
            tmp.remove(username)
            possible_meetings[0].participants = json.dumps(tmp)
        except Exception as e:
            print(e)

    db.session.commit()

    debug_func()
    return "Finished"


@main.route('/meeting_ended', methods=["POST"])
def meeting_ended():
    print("\nMEETING ENDED:\t" + str(request.data))
    content = json.loads(request.data)

    meeting_id = content["payload"]["object"]["id"]

    Rooms.query.filter(Rooms.meeting_id == meeting_id).delete(synchronize_session="evaluate")
    db.session.commit()

    debug_func()
    return "Finished"


@debug.route('/debug_drop_db', methods=["GET"])
def debug_drop_db():
    db.drop_all()
    return "Finished"


@debug.route('/debug_create_db', methods=["GET"])
def debug_create_db():
    db.drop_all()
    db.create_all()
    return "Finished"


@debug.route('/debug_add_user', methods=["GET"])
def debug_add_user():
    u = Users(name="Asaf", access_token="Blabla", refresh_token="Bla Bla")

    db.session.add(u)
    db.session.commit()
    return "Finished"


@debug.route('/debug_add_room', methods=["GET"])
def debug_add_room():
    r = Rooms(room_name="rr", floor=2, meeting_name="mm", participants="Blablabla", join_url="http://urlfine")

    db.session.add(r)
    db.session.commit()
    return "Finished"