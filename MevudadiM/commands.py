import click
from flask.cli import with_appcontext

from .extensions import db
from .models import *


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()


@click.command(name='drop_all_database')
@with_appcontext
def drop_all_database():
    db.drop_all()


@click.command(name='add_user')
@with_appcontext
def add_user():
    u = User(name="Asaf", access_token="Blabla", refresh_token="Bla Bla")

    db.session.add(u)
    db.session.commit()
