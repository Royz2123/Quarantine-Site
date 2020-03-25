from flask import Flask, request, render_template

import zoom_user

app = Flask(__name__, template_folder="./templates", static_folder="./static")


@app.route('/', methods=["GET"])
def hello():
    code = request.args.get("code")

    # check if this is a new user in the site, and if so add to the db of users
    if code is not None:
        new_user = zoom_user.User(code=code)

    print(code)
    return render_template(
        'index.html',
        title="Jinja Demo Site")

if __name__ == '__main__':
    app.run()