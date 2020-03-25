from .extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer)
    room_name = db.Column(db.String)
    floor = db.Column(db.Integer)
    meeting_id = db.Column(db.String(20))
    participants = db.Column(db.Text)