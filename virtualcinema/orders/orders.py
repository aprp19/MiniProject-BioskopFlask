from flask import Blueprint, request

from virtualcinema.auth import auth
from virtualcinema.db import db_session
from virtualcinema.models.models import ModelOrder, ModelAccount, ModelOrderSeat, ModelFilmSchedule, ModelFilm, \
    ModelSeat, ModelPayment, ModelWallet

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
        "film_name": row.schedules.film.film_name,
        "order_seat": row.order_seat,
        "order_studio": row.order_studio,
        "order_date": row.order_date,
        "order_time": row.order_time,
    } for row in query]
    return {"Message": "Success", "Count": len(response), "Data": response}, 200


@orders.route('/orders', methods=['POST'])
@auth
def handler_post_orders():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if request.is_json:
        json = request.get_json()
        get_FilmSchedule = ModelFilmSchedule.query.filter_by(id_schedule=json['id_schedule']).first()
        add_order = ModelOrder(
            id_user=session.id_user,
            id_schedule=json['id_schedule'],
            order_seat=json['order_seat'],
            order_studio=get_FilmSchedule.schedule_studio,
            order_date=get_FilmSchedule.schedule_date,
            order_time=get_FilmSchedule.schedule_time,
            order_qty=len(json['order_seat']),
            order_total=get_FilmSchedule.schedule_price * len(json['order_seat'])
        )

        for dulplicate_seat in range(0, len(json['order_seat'])):
            for data in range(dulplicate_seat + 1, len(json['order_seat'])):
                if json['order_seat'][data] == json['order_seat'][dulplicate_seat]:
                    return {"Error": "Cannot add duplicate seat"}, 400

        for seat in json['order_seat']:
            add_order.orderseat.append(
                ModelOrderSeat(
                    id_order=add_order.id_order,
                    id_seat=ModelSeat.query.filter_by(seat_number=seat).first().id_seat,
                    film_name=get_FilmSchedule.film.film_name,
                    schedule_studio=get_FilmSchedule.schedule_studio,
                    schedule_date=get_FilmSchedule.schedule_date,
                    schedule_time=get_FilmSchedule.schedule_time,
                )
            )

        for each_seat in json['order_seat']:
            if ModelOrderSeat.query.filter_by(schedule_studio=add_order.order_studio,
                                              schedule_date=add_order.order_date,
                                              schedule_time=add_order.order_time).join(
                ModelSeat).filter(
                ModelSeat.seat_number == each_seat
            ).first():
                return {"Error": "Seat already exists"}, 400

        db_session.add(add_order)
        db_session.commit()

        query_balance = ModelWallet.query.filter_by(id_user=session.id_user).first()
        if query_balance.w_balance < add_order.order_total:
            return {"Error": "Insufficient balance"}, 400
        else:
            query_balance.w_balance = query_balance.w_balance - add_order.order_total
            add_payment = ModelPayment(
                id_order=ModelOrder.query.filter_by(id_user=session.id_user).first().id_order,
                order_total=add_order.order_total,
                payment_status="Paid"
            )
        db_session.add(add_payment)
        db_session.commit()
        return {"Message": "Order added succesfully"}, 200
