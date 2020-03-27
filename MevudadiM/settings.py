import os

lcl = True

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'data.db') if lcl else os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY') if not lcl else None
SQLALCHEMY_TRACK_MODIFICATIONS = False