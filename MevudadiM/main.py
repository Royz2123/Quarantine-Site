from flask import Blueprint, request, render_template, make_response
import json

import MevudadiM.zoom_user as zoom_user
from MevudadiM.models import *

main = Blueprint("main", __name__)
debug = Blueprint("debug", __name__)


@main.route('/', methods=["GET"])
def homepage():
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
            new_user_db = Users(name=username, access_token=new_user.access_token, refresh_token=new_user.refresh_token)

            db.session.add(new_user_db)
            db.session.commit()
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

    username = request.cookies.get("username")

    user_dict = Users.query.filter(Users.name == username).first()
    user_obj = zoom_user.User(tokens=(user_dict.access_token, user_dict.refresh_token))
    print("GOT USER %s" % str(user_obj))

    meeting = user_obj.create_meeting()

    try:
        room_obj = Rooms(
            room_name=request.args.get("room_id"),
            meeting_name=request.args.get("topic"),
            meeting_id=meeting["uuid"],
            floor=request.args.get("floor"),
            join_url=meeting["join_url"],
            participants=json.dumps([username]))
        db.session.add(room_obj)
        db.commit()
        
    except Exception as e:
        print("\nERROR, Overused the Create:\t" + str(e))

    return str(meeting)


@main.route('/participant_joined', methods=["POST"])
def participant_joined():

    print("\nPARTICIPANT JOINED:\t" + str(request.data))
    content = json.loads(request.data)

    meeting_id = content["payload"]["object"]["uuid"]

    possible_meetings = Rooms.query.filter(Rooms.meeting_id == meeting_id).first()
    print("\nPOSSIBLE MEETINGS:\t" + str(possible_meetings))

    if possible_meetings is not None:
        username = content["payload"]["object"]["participant"]["user_name"]
        # TODO: username to FIRST and LAST name
        possible_meetings.participants = json.dumps(json.loads(possible_meetings.participants) + [username])

    db.session.commit()
    return "Finished"


@main.route('/participant_left', methods=["POST"])
def participant_left():

    print("\nPARTICIPANT LEFT:\t" + str(request.data))
    content = json.loads(request.data)

    meeting_id = content["payload"]["object"]["uuid"]

    # Search
    possible_meetings = Rooms.query.filter(Rooms.meeting_id == meeting_id).first()

    if possible_meetings is not None:
        username = content["payload"]["object"]["participant"]["user_name"]
        # TODO: username to FIRST and LAST name
        tmp = json.loads(possible_meetings[0].participants)
        tmp.remove(username)
        possible_meetings[0].participants = json.dumps(tmp)

    db.session.commit()
    return "Finished"


@main.route('/meeting_ended', methods=["POST"])
def meeting_ended():

    print("\nMEETING ENDED:\t" + str(request.data))
    content = json.loads(request.data)

    meeting_id = content["payload"]["object"]["uuid"]

    d = Rooms.delete().where(Rooms.meeting_id == meeting_id)
    d.execute()
    db.session.commit()
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