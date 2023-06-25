from flask import Blueprint, request

from virtualcinema.auth import auth
from virtualcinema.db import db_session
from virtualcinema.models.models import ModelSeat, ModelAccount

seats = Blueprint('seats', __name__)


@seats.route('/seats', methods=['GET'])
def handler_get_seats():
    query = ModelSeat.query.all()
    response = [{
        "id_seat": row.id_seat,
        "seat_number": row.seat_number,
    } for row in query]
    return {"Message": "Success", "Count": len(response), "Data": response}, 200


@seats.route('/seats', methods=['POST'])
@auth
def handler_post_seats():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if request.is_json:
            json = request.get_json()
            add_seat = ModelSeat(
                seat_number=json['seat_number'],
            )
            db_session.add(add_seat)
            db_session.commit()
            return {"Message": "Seat added succesfully", "Data": f"{add_seat.id_seat}"}, 200
        else:
            return {"Message": "Invalid Request"}, 400
    else:
        return {"Message": "Unauthorized"}, 403


@seats.route('/seats/<id_seat>', methods=['PUT'])
@auth
def handler_put_seats(id_seat):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        query = ModelSeat.query.filter_by(id_seat=id_seat).first()
        if not query:
            return {"Error": "Seat not found"}, 404
        if request.is_json:
            json = request.get_json()
            query.seat_number = json['seat_number']
            db_session.add(query)
            db_session.commit()
            return {"Message": "Seat updated succesfully"}, 200
        else:
            return {"Message": "Invalid Request"}, 400
    else:
        return {"Message": "Unauthorized"}, 403


@seats.route('/seats/<id_seat>', methods=['DELETE'])
@auth
def handler_delete_seats(id_seat):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        query = ModelSeat.query.filter_by(id_seat=id_seat).first()
        if not query:
            return {"Error": "Seat not found"}, 404
        db_session.delete(query)
        db_session.commit()
        return {"Message": "Seat deleted succesfully"}, 200
    else:
        return {"Message": "Unauthorized"}, 403
