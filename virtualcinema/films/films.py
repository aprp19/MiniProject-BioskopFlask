from flask import Blueprint, request

from virtualcinema.auth import auth
from virtualcinema.db import db_session
from virtualcinema.model.models import ModelAccount, ModelFilm, ModelFilmCategory, ModelFilmSchedule, ModelCategory

film = Blueprint('film', __name__)


@film.route('/film/<id_film>', methods=['GET'])
def handler_get_film(id_film):
    if id_film == 'all':
        query = ModelFilm.query.all()
        response = [{
            'id_film': row.id_film,
            'film_name': row.film_name,
            'film_duration': row.film_duration,
            'category': ['Not yet available' if ModelCategory.query.filter(ModelFilmCategory.id_film == row.id_film,
                                                                           ModelCategory.id_category == ModelFilmCategory.id_film).first() is None else cat.category_name
                         for cat in ModelCategory.query.filter(ModelFilmCategory.id_film == row.id_film,
                                                               ModelCategory.id_category == ModelFilmCategory.id_film).all()],
            'film_price': row.film_price,
            'film_selling': row.film_selling,
        } for row in query]

        return {"Message": "Success", "Count": len(response), "Data": response}, 200

    query = ModelFilm.query.filter_by(id_film=id_film).first()
    if not query:
        return {"Error": "Film not found"}, 404
    else:
        response = {
            'id_film': query.id_film,
            'film_name': query.film_name,
            'film_duration': query.film_duration,
            'category': ['Not yet available' if ModelCategory.query.filter(ModelFilmCategory.id_film == query.id_film,
                                                                           ModelCategory.id_category == ModelFilmCategory.id_film).first() is None else cat.category_name
                         for cat in ModelCategory.query.filter(ModelFilmCategory.id_film == query.id_film,
                                                               ModelCategory.id_category == ModelFilmCategory.id_film).all()],
            'film_price': query.film_price,
            'film_selling': query.film_selling,
        }
        return {"Message": "Success", "Data": response}, 200


@film.route('/film', methods=['POST'])
@auth
def handler_post_film():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if request.is_json:
            json = request.get_json()
            add_film = ModelFilm(
                film_name=json['film_name'],
                film_duration=json['film_duration'],
                film_price=json['film_price']
            )
            if ModelFilm.query.filter_by(film_name=add_film.film_name).first():
                return {"Error": "Film already exists"}, 400
            db_session.add(add_film)
            db_session.commit()
            return {"Message": "Film added succesfully", "Data": f"{add_film.film_name}"}, 200
        else:
            return {"Message": "Invalid Request"}, 400
    else:
        return {"Message": "Unauthorized"}, 403


@film.route('/film/<id_film>', methods=['PUT'])
@auth
def handler_put_film(id_film):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if request.is_json:
            json = request.get_json()
            update_film = ModelFilm.query.filter_by(id_film=id_film).first()
            if not update_film:
                return {"Error": "Film not found"}, 404
            else:
                update_film.film_name = json['film_name']
                update_film.film_duration = json['film_duration']
                update_film.film_price = json['film_price']
                db_session.add(update_film)
                db_session.commit()
                return {"Message": "Film updated succesfully", "Data": f"{update_film.film_name}"}, 200
        else:
            return {"Message": "Invalid Request"}, 400
    else:
        return {"Message": "Unauthorized"}, 403


@film.route('/film/<id_film>', methods=['DELETE'])
@auth
def handler_delete_film(id_film):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        query = ModelFilm.query.filter_by(id_film=id_film).first()
        if not query:
            return {"Error": "Film not found"}, 404
        db_session.delete(query)
        db_session.commit()
        return {"Message": "Film deleted succesfully"}, 200
    else:
        return {"Message": "Unauthorized"}, 403


@film.route('/category/<id_category>', methods=['GET'])
def handler_get_category(id_category):
    if id_category == 'all':
        query = ModelCategory.query.all()
        response = [{
            'id_category': row.id_category,
            'category_name': row.category_name,
        } for row in query]
        return {"Message": "Success", "Count": len(response), "Data": response}, 200
    query = ModelCategory.query.filter_by(id_category=id_category).first()
    if not query:
        return {"Error": "Category not found"}, 404
    else:
        response = {
            'id_category': query.id_category,
            'category_name': query.category_name,
        }
        return {"Message": "Success", "Data": response}, 200


@film.route('/category', methods=['POST'])
@auth
def handler_post_category():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if request.is_json:
            json = request.get_json()
            add_category = ModelCategory(
                category_name=json['category_name']
            )
            if ModelCategory.query.filter_by(category_name=add_category.category_name).first():
                return {"Error": "Category already exists"}, 400
            db_session.add(add_category)
            db_session.commit()
            return {"Message": "Category added succesfully", "Data": f"{add_category.category_name}"}, 200
        else:
            return {"Message": "Invalid Request"}, 400
    else:
        return {"Message": "Unauthorized"}, 403


@film.route('/category/<id_category>', methods=['DELETE'])
@auth
def handler_delete_category(id_category):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        query = ModelCategory.query.filter_by(id_category=id_category).first()
        if not query:
            return {"Error": "Category not found"}, 404
        db_session.delete(query)
        db_session.commit()
        return {"Message": "Category deleted succesfully"}, 200
    else:
        return {"Message": "Unauthorized"}, 403


@film.route('/film_category/<id_film>', methods=['POST'])
@auth
def handler_post_film_category(id_film):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if request.is_json:
            json = request.get_json()
            add_film_category = ModelFilmCategory(
                id_film=id_film,
                id_category=json['id_category']
            )
            if ModelFilmCategory.query.filter_by(id_film=id_film, id_category=json['id_category']).first():
                return {"Error": "Film category already exists"}, 400
            db_session.add(add_film_category)
            db_session.commit()
            return {"Message": "Film category added succesfully", "Data": f"{add_film_category.id_category}"}, 200
        else:
            return {"Message": "Invalid Request"}, 400
    else:
        return {"Message": "Unauthorized"}, 403