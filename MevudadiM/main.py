from flask import Blueprint, request, render_template, make_response, redirect, url_for, flash, current_app
from apscheduler.schedulers.background import BackgroundScheduler

import json
import os

import MevudadiM.zoom_user as zoom_user
from MevudadiM.models import *


MINUTES_BETWEEN_REFRESH_TOKENS = 1

SERVICE_MEMES = "SERVICE_MEMES"

HEROKU_AUTH = "https://zoom.us/oauth/authorize?response_type=code&client_id=dHLRYFE5QhadcBZZLYMf6w&redirect_uri=https://mevudadim.herokuapp.com/"
TEST_AUTH = "https://zoom.us/oauth/authorize?response_type=code&client_id=dHLRYFE5QhadcBZZLYMf6w&redirect_uri=http://5c3d600f.ngrok.io/"

main = Blueprint("main", __name__)
debug = Blueprint("debug", __name__)


@debug.route('/debug', methods=["GET"])
def debug_func():
    print("Users: ", Users.query.all(), "\n")
    print("Rooms: ", Rooms.query.all(), "\n")


def job_refresh_tokens(app):
    with app.app_context():
        all_users = Users.query.all()
        for user in all_users:
            zoom_user.refresh_user_access_token(user)

        db.session.commit()

    print("refreshed_tokens!")


@main.before_app_first_request
def initialize_app():
    apsched = BackgroundScheduler()
    apsched.start()

    apsched.add_job(job_refresh_tokens, 'interval', args=[current_app._get_current_object()], minutes=MINUTES_BETWEEN_REFRESH_TOKENS)

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

            # delete all previous users with this username
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
    return redirect(HEROKU_AUTH)


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
        "topic": room.meeting_name,
        "door_state": room.is_locked
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

    print("MEETING ID: ", meeting_id)

    # Search
    possible_meeting = Rooms.query.filter(Rooms.meeting_id == meeting_id).first()

    if possible_meeting is not None:
        try:
            username = content["payload"]["object"]["participant"]["user_name"]

            print(username)
            print(possible_meeting.participants)
            # TODO: username to FIRST and LAST name
            tmp = json.loads(possible_meeting.participants)
            tmp.remove(username)
            possible_meeting.participants = json.dumps(tmp)
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


@main.route('/change_door_state', methods=["POST"])
def change_door_state():
    content = json.loads(request.data)

    room_id = content["payload"]["object"]["room_id"]
    state = content["payload"]["object"]["door_state"]

    curr_room = Rooms.query.filter(Rooms.room_id == room_id).first()
    curr_room.is_locked = state

    db.session.commit()
    return "Finished"

# Debug Stuff


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

# Marketplace stuff


@main.route('/policy', methods=["GET"])
def policy():
    return render_template(
        "redirect.html",
        redirect_url="https://www.privacypolicygenerator.info/live.php?token=QWyn09msrZjztzgZURJRstG44VF1yC24"
    )


@main.route('/terms', methods=["GET"])
def terms():
    return render_template(
        "redirect.html",
        redirect_url="https://www.termsfeed.com/terms-conditions/6127647aad9dd63af82a6e7de0b86b9e"
    )


# BLOG STUFF

def get_images():
    result = [(str(x.id), x.creator) for x in Data.query.filter(Data.service == SERVICE_MEMES).all()]
    print(result)
    return result


@main.route("/get_image", methods=["GET"])
def get_image():
    x = Data.query.filter(Data.id == int(request.args.get("pic"))).first()
    return x.binary_data

@main.route('/memes')
def get_memes():
    return render_template('memes.html', result=get_images())


@main.route('/videos')
def get_videos():
    videos = [
        ("https://drive.google.com/file/d/1qBWrofWpj33k9k0Yy72LePw-2bP_wbkQ/preview", "Ariel Shnitz"),
        ("https://drive.google.com/file/d/1SiJoTd3Tx3Vblqs5G3rSAhF00If_q87q/preview", "Omer Prives"),
        ("https://drive.google.com/file/d/1qEb2EorvLGoBNYGq_rzU1FnhYcOLHd-1/preview", "Lior Lederer"),
        ("https://drive.google.com/file/d/1H9_iRmc7Q8bBOTFvNU21NAF8ExSI-UGy/preview", "Topaz Enbar"),
    ]
    return render_template('videos.html', result=videos)


@main.route('/up', methods=['GET', 'POST'])
def upload_file():
    import os
    from werkzeug.utils import secure_filename
    UPLOAD_FOLDER = 'Mevudadim/static/memes'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            username = ""
            if request.cookies.get("username") is not None:
                username += request.cookies.get("username")
            d = Data(creator=username, service=SERVICE_MEMES, binary_data=file.read())

            db.session.add(d)
            db.session.commit()
        return redirect(url_for('main.get_memes'))


def countDir(path):
    files = folders = 0
    for _, dirnames, filenames in os.walk(path):
      # ^ this idiom means "we won't be using this value"
        files += len(filenames)
        folders += len(dirnames)
    return folders,files



@main.route('/blog')
def blog():
    print("BLOGGG", blogHelper())
    return render_template('blog.html', episodes=blogHelper())
    # srcs = [{'source':'statics/prosak/ep1/a.png'}
    #        ,{'source':'statics/prosak/ep1/b.png'}]
    # episodes = [{'episodeNum':1,'srcs':srcs}]
    # return render_template('blog.html', episodes = episodes)

def blogHelper():
    num_of_episodes = countDir('./Mevudadim/static/prosak')[0]
    print("EPISODES", num_of_episodes)
    episodes = []
    for i in range(1,num_of_episodes+1):
        j = num_of_episodes+1-i
        episodes.append({'episodeNum':(j),'srcs':srcsHelper(j)})
    return episodes


def srcsHelper(num):
    numToWords = {1:'a',2:'b',3:'c',4:'d',5:'e',6:'f'}
    srcs = []
    num_of_srcs = countDir('./Mevudadim/static/prosak/ep'+str(num))[1]
    for i in range(1,num_of_srcs+1):
        srcs.append({'source':'static/prosak/ep'+str(num)+'/'+numToWords[i]+'.png'})
    print(srcs)
    return srcs
# def blogHelper():


@main.route('/blog/<string:blog_id>')
def blogspot(blog_id):
    return 'This is blog post number '+blog_id