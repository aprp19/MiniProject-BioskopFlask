from flask import Blueprint, request

from virtualcinema.auth import auth
from virtualcinema.db import db_session
from virtualcinema.models.models import ModelFilm, ModelAccount, ModelFilmSchedule

film_schedule = Blueprint('film_schedule', __name__)


@film_schedule.route('/film_schedule', methods=['GET'])
def handler_get_film_schedule():
    query = ModelFilmSchedule.query.all()
    response = [{
        "id_schedule": row.id_schedule,
        "id_film": row.film.id_film,
        "film_name": row.film.film_name,
        "film_poster": row.film.film_poster,
        "schedule_studio": row.schedule_studio,
        "schedule_date": row.schedule_date,
        "schedule_time": row.schedule_time,
        "schedule_price": row.schedule_price,
    } for row in query]
    if not query:
        return {"Error": "Schedule empty"}, 404
    return {"Message": "Success", "Count": len(response), "Data": response}, 200


@film_schedule.route('/film_schedule/<id_film>', methods=['GET'])
def handler_get_film_schedule_by_id(id_film):
    query = ModelFilmSchedule.query.filter_by(id_film=id_film).all()
    response = [{
        "id_schedule": row.id_schedule,
        "film_name": row.film.film_name,
        "schedule_studio": row.schedule_studio,
        "schedule_date": row.schedule_date,
        "schedule_time": row.schedule_time,
        "schedule_price": row.schedule_price,
    } for row in query]
    if not query:
        return {"Error": "Schedule not found"}, 404
    return {"Message": "Success", "Data": response}, 200


@film_schedule.route('/film_schedule/search', methods=['GET'])
def handler_search_film_schedule():
    args = request.args
    query = ModelFilmSchedule.query.all()
    if 'film_name' in args:
        query = ModelFilmSchedule.query.join(ModelFilm).filter(ModelFilm.film_name.contains(args['film_name'])).all()
    if 'date' in args:
        query = ModelFilmSchedule.query.filter(ModelFilmSchedule.schedule_date.contains(args['date'])).all()
    if not query:
        return {"Error": "Film not found"}, 404

    response = [{
        "id_schedule": row.id_schedule,
        "id_film": row.film.id_film,
        "film_name": row.film.film_name,
        "film_poster": row.film.film_poster,
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
            return {"Message": "Film schedules added succesfully", "Data": f"{add_film_schedule.id_film}"}, 200
        else:
            return {"Message": "Invalid Request"}, 400
    else:
        return {"Message": "Unauthorized"}, 403


@film_schedule.route('/film_schedule/<id_schedule>', methods=['PUT'])
@auth
def handler_put_film_schedule(id_schedule):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if request.is_json:
            json = request.get_json()
            update_film_schedule = ModelFilmSchedule.query.filter_by(id_schedule=id_schedule).first()
            if not update_film_schedule:
                return {"Error": "Film schedules not found"}, 404
            else:
                update_film_schedule.schedule_studio = json['schedule_studio']
                update_film_schedule.schedule_date = json['schedule_date']
                update_film_schedule.schedule_time = json['schedule_time']
                update_film_schedule.schedule_price = json['schedule_price']
                db_session.add(update_film_schedule)
                db_session.commit()
                return {"Message": "Film schedules updated succesfully",
                        "Data": f"{update_film_schedule.film.film_name}"}, 200
        else:
            return {"Message": "Invalid Request"}, 400
    else:
        return {"Message": "Unauthorized"}, 403


@film_schedule.route('/film_schedule/<id_schedule>', methods=['DELETE'])
@auth
def handler_delete_film_schedule(id_schedule):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        query = ModelFilmSchedule.query.filter_by(id_schedule=id_schedule).first()
        if not query:
            return {"Error": "Film schedules not found"}, 404
        db_session.delete(query)
        db_session.commit()
        return {"Message": "Film schedules deleted succesfully"}, 200
    else:
        return {"Message": "Unauthorized"}, 403
