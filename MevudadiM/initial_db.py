from MevudadiM.models import *
from flask import Flask

app = Flask(__name__)
db.init_app(app)

with app.app_context():
    db.create_all()
u = Users(name="Asaf Haas", access_token="bla", refresh_token="Bla")

db.session.add(u)
db.session.commit()