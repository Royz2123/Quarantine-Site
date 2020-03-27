from .extensions import db


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)


class Rooms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(200))
    room_name = db.Column(db.String(200))
    meeting_name = db.Column(db.String(200))
    floor = db.Column(db.Integer)
    join_url = db.Column(db.String(200))
    meeting_id = db.Column(db.String(200))
    participants = db.Column(db.Text)
    is_locked = db.Column(db.String(200))
