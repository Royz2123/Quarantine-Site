from .extensions import db
from .models import *

u = User(name="Asaf Haas", access_token="bla", refresh_token="Bla")

db.session.add(u)
db.session.commit()