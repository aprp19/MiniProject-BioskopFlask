from flask import request
from virtualcinema.models.models import ModelAccount


def auth(func):
    def decorator(*args, **kwargs):
        session = request.authorization
        if not session or not check_session(session.username, session.password):
            return {"Error": "Unauthorized"}, 401
        return func(*args, **kwargs)

    decorator.__name__ = func.__name__
    return decorator


def check_session(username, password):
    query = ModelAccount.query.filter_by(u_username=username).first()
    return username == query.u_username and password == query.u_password
