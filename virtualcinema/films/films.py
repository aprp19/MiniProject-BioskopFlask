from flask import Blueprint

from virtualcinema.auth import auth
from virtualcinema.model.models import ModelAccount

film = Blueprint('film', __name__)


@film.route('/film')
@auth
def handler_get_account():
    return 'Hello World!'


@film.route('/film')
@auth
def handler_post_account():
    return 'Hello World!'