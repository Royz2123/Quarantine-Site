from .extensions import db
import datetime


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)

    def __repr__(self):
        return "USER OBJ: %s, %s..., %s...\n" % (self.name, self.access_token[:10], self.refresh_token[:10])


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

    def __repr__(self):
        return "ROOM OBJ: %s, %s, %s, %s, %s\n" % (self.room_name, self.meeting_id, self.meeting_name, self.join_url, self.participants)


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.String(200))
    service = db.Column(db.String(200))
    text_data = db.Column(db.Text)
    binary_data = db.Column(db.LargeBinary)
    timestamp = db.Column(db.TIMESTAMP, default=datetime.datetime.now())
