from datetime import datetime, timedelta

from flask import Blueprint, request, json

from virtualcinema.auth import auth
from virtualcinema.db import db_session
from virtualcinema.models.models import ModelOrder, ModelAccount, ModelOrderSeat, ModelFilmSchedule, ModelSeat, \
    ModelPayment

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

    expiration_check()

    response = [{
        "id_order": row.id_order,
        "id_user": row.id_user,
        "id_schedule": row.id_schedule,
        "order_username": ModelAccount.query.filter_by(id_user=row.id_user).first().u_username,
        "film_name": row.schedules.film.film_name,
        "order_seat": [ModelSeat.query.filter_by(id_seat=seat.id_seat).first().seat_number for seat in row.orderseat],
        "order_studio": row.order_studio,
        "order_date": row.order_date,
        "order_time": json.dumps(row.order_time, default=str),
        "order_price": row.order_total,
        "order_expiration": json.dumps(row.expiration, default=str),
        "order_status": ModelPayment.query.filter_by(id_order=row.id_order).first().payment_status
    } for row in query]
    return {"Message": "Success", "Count": len(response), "Data": response}, 200


@orders.route('/orders', methods=['POST'])
@auth
def handler_post_orders():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if request.is_json:
        json = request.get_json()
        get_FilmSchedule = ModelFilmSchedule.query.filter_by(id_schedule=json['id_schedule']).first()
        expiration = datetime.now() + timedelta(minutes=5)
        add_order = ModelOrder(
            id_user=session.id_user,
            id_schedule=json['id_schedule'],
            order_seat=json['order_seat'],
            order_studio=get_FilmSchedule.schedule_studio,
            order_date=get_FilmSchedule.schedule_date,
            order_time=get_FilmSchedule.schedule_time,
            order_qty=len(json['order_seat']),
            expiration=expiration.strftime("%H:%M"),
            order_total=get_FilmSchedule.schedule_price * len(json['order_seat'])
        )

        for duplicate_seat in range(0, len(json['order_seat'])):
            for data in range(duplicate_seat + 1, len(json['order_seat'])):
                if json['order_seat'][data] == json['order_seat'][duplicate_seat]:
                    return {"Error": "Cannot add duplicate seat"}, 400

        for seat in json['order_seat']:
            add_order.orderseat.append(
                ModelOrderSeat(
                    id_order=add_order.id_order,
                    id_seat=seat,
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
                ModelSeat.id_seat == each_seat
            ).first():
                return {"Error": "Seat already exists"}, 400
        db_session.add(add_order)
        db_session.commit()

        add_payment = ModelPayment(
            id_order=add_order.id_order,
            order_total=add_order.order_total,
            payment_status="Not Paid"
        )

        db_session.add(add_payment)
        db_session.commit()
        return {"Message": "Order added succesfully"}, 200


def expiration_check():
    query_orders = ModelOrder.query.join(ModelPayment).filter(ModelOrder.id_order == ModelPayment.id_order,
                                                              ModelPayment.payment_status == "Not Paid").all()
    current_time = datetime.now()
    for row in query_orders:
        query_payment = ModelPayment.query.filter_by(id_order=row.id_order).first()
        expiration = row.expiration.strftime("%H:%M")
        if current_time.strftime("%H:%M") > expiration:
            query_payment.payment_status = "Expired"
            db_session.add(query_payment)
            db_session.commit()
            query_order_seat = ModelOrderSeat.query.filter_by(id_order=row.id_order).all()
            for each in query_order_seat:
                db_session.delete(each)
                db_session.commit()
