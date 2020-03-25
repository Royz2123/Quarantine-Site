from flask import Flask, request, render_template, make_response

import MevudadiM.zoom_user as zoom_user

app = Flask(__name__, template_folder="./templates", static_folder="./static")

users = []

@app.route('/', methods=["GET"])
def homepage():
    code = request.args.get("code")

    # check if this is a new user in the site, and if so add to the db of users
    username = "<Not logged in>"
    if code is not None:
        new_user = zoom_user.User(code=code)
        username = "%s %s" % (
            new_user.account_info["first_name"],
            new_user.account_info["last_name"],
        )
        users.append((username, new_user))

    resp = make_response(render_template(
        'index.html',
        greeting="Welcome %s" % username,
        title="מחזור מ האגדי - דף הבית"
    ))
    resp.set_cookie("username", username)
    return resp


@app.route('/enter_room_first', methods=["POST", "GET"])
def enter_room():
    # TODO: Get room argument and store in database

    username = request.cookies.get("username")

    # get user object from list / db
    user_obj = [user for name, user in users if name == username][0]
    print("GOT USER %s" % str(user_obj))

    meeting = user_obj.create_meeting()

    return str(meeting)


@app.route('/participant_joined', methods=["POST"])
def participant_joined():
    pass


@app.route('/participant_left', methods=["POST"])
def participant_joined():
    pass


@app.route('/meeting_ended', methods=["POST"])
def participant_joined():
    pass




if __name__ == '__main__':
    app.run()