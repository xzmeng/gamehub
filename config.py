import os

from dotenv import load_dotenv
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', '123456')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.163.com')
    MAIL_PORT = os.environ.get('MAIL_PORT', '25')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    GAMEHUB_MAIL_SUBJECT_PREFIX = '[GameHub]'
    GAMEHUB_MAIL_SENDER = os.environ.get('MAIL_SENDER', 'GameHub Admin <example@example.com>')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_ECHO = False

    PHOTOS_FOLDER = os.path.abspath('app/static/photos')