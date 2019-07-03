from flask import Blueprint

back = Blueprint('back', __name__)

from . import views
