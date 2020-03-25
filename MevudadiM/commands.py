import click
from flask.cli import with_appcontext

from .extensions import db
from .models import *


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()

    u = User(name="Asaf Haas", access_token="bla", refresh_token="bla")
    db.session.add(u)
    db.session.commit()