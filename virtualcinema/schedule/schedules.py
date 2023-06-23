from flask import Blueprint, request

from virtualcinema.auth import auth
from virtualcinema.db import db_session
from virtualcinema.model.models import ModelFilm, ModelAccount, ModelFilmSchedule

film_schedule = Blueprint('film_schedule', __name__)


@film_schedule.route('/film_schedule', methods=['GET'])
def handler_get_film_schedule():
    query = ModelFilmSchedule.query.all()
    response = [{
        "film_name": row.film.film_name,
        "schedule_studio": row.schedule_studio,
        "schedule_date": row.schedule_date,
        "schedule_time": row.schedule_time,
        "schedule_price": row.schedule_price,
    } for row in query]
    return {"Message": "Success", "Count": len(response), "Data": response}, 200


@film_schedule.route('/film_schedule/search', methods=['GET'])
def handler_search_film_schedule():
    args = request.args
    query = ModelFilmSchedule.query.all()
    if 'film_name' in args:
        query = ModelFilmSchedule.query.filter(ModelFilm.film_name.like('%' + args['film_name'] + '%')).all()
    if 'date' in args:
        query = ModelFilmSchedule.query.filter(ModelFilmSchedule.schedule_date.like('%' + args['date'] + '%')).all()
    if not query:
        return {"Error": "Film not found"}, 404

    response = [{
        "id_schedule": row.id_schedule,
        "film_name": row.film.film_name,
        "schedule_studio": row.schedule_studio,
        "schedule_date": row.schedule_date,
        "schedule_time": row.schedule_time,
        "schedule_price": row.schedule_price,
    } for row in query]
    return {"Message": "Success", "Count": len(response), "Data": response}, 200


@film_schedule.route('/film_schedule', methods=['POST'])
@auth
def handler_post_film_schedule():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if request.is_json:
            json = request.get_json()
            add_film_schedule = ModelFilmSchedule(
                id_film=json['id_film'],
                schedule_studio=json['schedule_studio'],
                schedule_date=json['schedule_date'],
                schedule_time=json['schedule_time'],
                schedule_price=ModelFilm.query.filter_by(id_film=json['id_film']).first().film_price
            )
            db_session.add(add_film_schedule)
            db_session.commit()
            return {"Message": "Film schedule added succesfully", "Data": f"{add_film_schedule.id_film}"}, 200
        else:
            return {"Message": "Invalid Request"}, 400
    else:
        return {"Message": "Unauthorized"}, 403
