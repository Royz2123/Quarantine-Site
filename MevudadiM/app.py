from flask import Flask
from .extensions import db
from .models import User, Room

app = Flask(__name__, template_folder="./templates", static_folder="./static")


@app.route('/update_floor', methods=["GET"])
def update_floor():

    return

if __name__ == '__main__':
    app.run()