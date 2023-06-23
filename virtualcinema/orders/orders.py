from flask import Blueprint, request

from virtualcinema.auth import auth
from virtualcinema.db import db_session
from virtualcinema.models.models import ModelOrder, ModelAccount, ModelOrderSeat, ModelFilmSchedule, ModelFilm, \
    ModelSeat

orders = Blueprint('orders', __name__)


@orders.route('/orders', methods=['GET'])
@auth
def handler_get_orders():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    query = ModelOrder.query.filter(ModelOrder.id_user == session.id_user).all()

    if session.u_role == 'Admin':
        query = ModelOrder.query.all()
    if not query:
        return {"Error": "Orders not found"}, 404

    response = [{
        "id_order": row.id_order,
        "id_user": row.id_user,
        "id_schedule": row.id_schedule,
        "film_name": row.schedule.film.film_name,
        "schedule_studio": row.schedule_studio,
        "schedule_date": row.schedule_date,
        "schedule_time": row.schedule_time,
    } for row in query]
    return {"Message": "Success", "Count": len(response), "Data": response}, 200


@orders.route('/orders', methods=['POST'])
@auth
def handler_post_orders():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if request.is_json:
            json = request.get_json()
            add_order = ModelOrder(
                id_user=session.id_user,
                id_schedule=json['id_schedule'],
                # order_seat=json['order_seat'],
                order_studio=ModelFilmSchedule.query.filter_by(id_schedule=json['id_schedule']).first().schedule_studio,
                order_date=ModelFilmSchedule.query.filter_by(id_schedule=json['id_schedule']).first().schedule_date,
                order_time=ModelFilmSchedule.query.filter_by(id_schedule=json['id_schedule']).first().schedule_time,
                order_qty=len(json['order_seat']),
                order_total=ModelFilmSchedule.query.filter_by(id_schedule=json['id_schedule']).first().schedule_price * len(json['order_seat'])
            )

            # query_seat = ModelOrderSeat.query.all()
            # if not query_seat.id_seat == ModelSeat.query.filter_by(id_seat=json['order_seat']).first().id_seat and query_seat.film_name == add_order.film_name and query_seat.schedule_studio == add_order.schedule_studio and query_seat.schedule_date == add_order.schedule_date and query_seat.schedule_time == add_order.schedule_time:
            #     return {"Error": "Seat already taken"}, 400

            for seat in json['order_seat']:
                add_order.orderseat.append(
                    ModelOrderSeat(
                        id_order=add_order.id_order,
                        id_seat=ModelSeat.query.filter_by(seat_number=seat).first().id_seat,
                        film_name=ModelFilmSchedule.query.filter_by(id_schedule=add_order.id_schedule).first().film.film_name,
                        schedule_studio=ModelFilmSchedule.query.filter_by(id_schedule=add_order.id_schedule).first().schedule_studio,
                        schedule_date=ModelFilmSchedule.query.filter_by(id_schedule=add_order.id_schedule).first().schedule_date,
                        schedule_time=ModelFilmSchedule.query.filter_by(id_schedule=add_order.id_schedule).first().schedule_time,
                    )
                )
            db_session.add(add_order)
            db_session.commit()
            return {"Message": "Success"}, 200
    else:
        return {"Message": "Unauthorized"}, 403

#
# @orders.route('/orders/<id_order>', methods=['DELETE'])
# @auth