from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

from .commands import create_tables, drop_all_database, add_user, add_room
from .extensions import db
from .main import main, debug


def create_app(config_file='settings.py'):
    app = Flask(__name__)


    app.config.from_pyfile(config_file)

    db.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(debug)



    app.cli.add_command(create_tables)
    app.cli.add_command(drop_all_database)
    app.cli.add_command(add_user)
    app.cli.add_command(add_room)

    return app
