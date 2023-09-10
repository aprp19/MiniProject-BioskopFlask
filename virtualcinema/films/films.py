from flask import Blueprint, request

from virtualcinema.auth import auth
from virtualcinema.db import db_session
from virtualcinema.models.models import ModelAccount, ModelFilm, ModelFilmCategory, ModelCategory

film = Blueprint('film', __name__)


@film.route('/film/<id_film>', methods=['GET'])
def handler_get_film(id_film):
    if id_film == 'all':
        query = ModelFilm.query.all()
        response = [{
            'id_film': row.id_film,
            'film_name': row.film_name,
            'film_duration': row.film_duration,
            'category': [cat.category_name for cat in
                         ModelCategory.query.filter(ModelFilmCategory.id_film == row.id_film,
                                                    ModelCategory.id_category == ModelFilmCategory.id_category).all()],
            'film_price': row.film_price,
            'film_selling': row.film_selling,
            'film_poster': row.film_poster,
            'film_desc': row.film_desc
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
            'category': [cat.category_name for cat in
                         ModelCategory.query.filter(ModelFilmCategory.id_film == query.id_film,
                                                    ModelCategory.id_category == ModelFilmCategory.id_category).all()],
            'film_price': query.film_price,
            'film_selling': query.film_selling,
            'film_poster': query.film_poster,
            'film_desc': query.film_desc
        }
        return {"Message": "Success", "Data": response}, 200


@film.route('/film/search', methods=['GET'])
def handler_search_film():
    args = request.args
    query = ModelFilm.query.all()
    if 'film_name' in args:
        query = ModelFilm.query.filter(ModelFilm.film_name.contains(args['film_name'])).all()
    if 'category' in args:
        query = ModelFilm.query.join(ModelFilmCategory).filter(ModelFilm.film_name.contains(args['film_name'])).all()
    if 'date' in args:
        query = ModelFilm.query.filter(ModelFilm.film_name.contains(args['film_name'])).all()
    if not query:
        return {"Error": "Film not found"}, 404

    response = [{
        'id_film': row.id_film,
        'film_name': row.film_name,
        'film_duration': row.film_duration,
        'category': [cat.category_name for cat in
                     ModelCategory.query.filter(ModelFilmCategory.id_film == row.id_film,
                                                ModelCategory.id_category == ModelFilmCategory.id_category).all()],
        'film_price': row.film_price,
        'film_selling': row.film_selling,
        'film_poster': row.film_poster,
        'film_desc': row.film_desc
    } for row in query]
    return {"Message": "Success", "Count": len(response), "Data": response}, 200


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
                film_price=json['film_price'],
                film_desc=json['film_desc'],
                film_selling=json['film_selling']
            )
            if ModelFilm.query.filter_by(film_name=add_film.film_name).first():
                return {"Error": "Film already exists"}, 400
            db_session.add(add_film)
            db_session.commit()

            for cat in json['id_category']:
                add_film_category = ModelFilmCategory(
                    id_film=ModelFilm.query.filter_by(film_name=add_film.film_name).first().id_film,
                    id_category=cat
                )
                db_session.add(add_film_category)
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
                update_film.film_desc = json['film_desc']
                db_session.add(update_film)
                db_session.commit()
                return {"Message": "Film updated succesfully", "Data": f"{update_film.film_name}"}, 200
        else:
            return {"Message": "Invalid Request"}, 400
    else:
        return {"Message": "Unauthorized"}, 403


@film.route('/film_poster/<id_film>', methods=['PUT'])
@auth
def handler_put_film_poster(id_film):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if request.is_json:
            json = request.get_json()
            update_film = ModelFilm.query.filter_by(id_film=id_film).first()
            if not update_film:
                return {"Error": "Film not found"}, 404
            else:
                update_film.film_poster = json['film_poster']
                db_session.add(update_film)
                db_session.commit()
                return {"Message": "Film Poster updated succesfully", "Data": f"{update_film.film_name}"}, 200
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
        film_category = ModelFilmCategory.query.filter_by(id_film=id_film).all()

        for cat in film_category:
            db_session.delete(cat)
            db_session.commit()
            
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


@film.route('/category/<id_category>', methods=['PUT'])
@auth
def handler_put_category(id_category):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if request.is_json:
            json = request.get_json()
            update_category = ModelCategory.query.filter_by(id_category=id_category).first()
            if ModelCategory.query.filter_by(category_name=json['category_name']).first():
                return {"Error": "Category already exists"}, 400
            update_category.category_name = json['category_name']
            db_session.add(update_category)
            db_session.commit()
            return {"Message": "Category edited succesfully", "Data": f"{update_category.category_name}"}, 200
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

            for duplicate_category in range(0, len(json['id_category'])):
                for data in range(duplicate_category + 1, len(json['id_category'])):
                    if json['id_category'][data] == json['id_category'][duplicate_category]:
                        return {"Error": "Duplicate Film Category"}, 400

            for category in json['id_category']:

                if ModelFilmCategory.query.filter_by(id_film=id_film, id_category=category).first():
                    return {"Error": "Film category already exists"}, 400

            for cat in json['id_category']:
                add_film_category = ModelFilmCategory(
                    id_film=id_film,
                    id_category=cat
                )
                db_session.add(add_film_category)
                db_session.commit()

            return {
                "Message": f"{[ModelCategory.query.filter_by(id_category=cat).first().category_name for cat in json['id_category']]} added to {ModelFilm.query.filter_by(id_film=id_film).first().film_name} succesfully",
                "Data": f"{add_film_category.id_category}"}, 200
        else:
            return {"Message": "Invalid Request"}, 400
    else:
        return {"Message": "Unauthorized"}, 403


@film.route('/film_category/<id_film>', methods=['PUT'])
@auth
def handler_put_film_category(id_film):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if request.is_json:
            json = request.get_json()
            update_cat = ModelFilmCategory.query.filter_by(id_film=id_film).all()

            for each in update_cat:
                db_session.delete(each)
                db_session.commit()

            for cat in json['id_category']:
                add_film_category = ModelFilmCategory(
                    id_film=id_film,
                    id_category=cat
                )
                db_session.add(add_film_category)
                db_session.commit()
            return {
                "Message": f"{[ModelCategory.query.filter_by(id_category=cat).first().category_name for cat in json['id_category']]} added to {ModelFilm.query.filter_by(id_film=id_film).first().film_name} succesfully","Data": f"{len(json['id_category'])}"}, 200
        else:
            return {"Message": "Invalid Request"}, 400
    else:
        return {"Message": "Unauthorized"}, 403


@film.route('/film_category/<id_film>/<id_category>', methods=['DELETE'])
@auth
def handler_delete_film_category(id_film, id_category):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        query = ModelFilmCategory.query.filter_by(id_film=id_film, id_category=id_category).first()
        if not query:
            return {"Error": "Film category not found"}, 404
        db_session.delete(query)
        db_session.commit()
        return {"Message": "Film category deleted succesfully"}, 200
    else:
        return {"Message": "Unauthorized"}, 403


@film.route('/film/report', methods=['GET'])
@auth
def handler_get_report():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        query = ModelFilm.query.order_by(ModelFilm.film_selling.desc()).limit(5).all()
        response = [{
            'id_film': row.id_film,
            'film_name': row.film_name,
            'film_selling': row.film_selling,
            'film_poster': row.film_poster,
        } for row in query]
        return {"Message": "Success", "Count": len(response), "Data": response}, 200
    else:
        return {"Message": "Unauthorized"}, 403
