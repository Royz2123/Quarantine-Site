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