from flask import Blueprint, request
from virtualcinema.auth import auth
from virtualcinema.db import db_session
from virtualcinema.models.models import ModelAccount, ModelPayment, ModelOrder, ModelWallet, ModelFilm, ModelTickets, \
    ModelOrderSeat

payments = Blueprint('payments', __name__)


@payments.route('/payments', methods=['GET'])
@auth
def handler_get_payments():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    query = ModelPayment.query.filter_by(
        id_order=ModelOrder.query.filter_by(id_user=session.id_user).first().id_order).all()

    if session.u_role == 'Admin':
        query = ModelPayment.query.all()
    if not query:
        return {"Error": "Payments not found"}, 404

    response = [{
        "id_payment": row.id_payment,
        "id_order": row.id_order,
        "order_total": row.order_total,
        "payment_status": row.payment_status,
    } for row in query]
    return {"Message": "Success", "Count": len(response), "Data": response}, 200


@payments.route('/payments/<id_payment>/<action>', methods=['PUT'])
@auth
def handler_put_payments(id_payment, action):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    query = ModelPayment.query.filter_by(id_payment=id_payment).first()
    movie_selling = ModelFilm.query.filter_by(id_film=query.orders.schedules.film.id_film).first()

    if action == 'pay':
        # Check saldo pengguna
        query_balance = ModelWallet.query.filter_by(id_user=session.id_user).first()
        if query_balance.w_balance < query.order_total:
            return {"Error": "Insufficient balance"}, 400

        # If Success, saldo akan berkurang
        query_balance.w_balance = query_balance.w_balance - query.order_total

        # Penjualan film bertambah
        movie_selling.film_selling += query.orders.order_qty

        add_ticket = ModelTickets(
            id_user=session.id_user,
            id_order=query.orders.id_order,
            id_payment=query.id_payment,
        )
        query.payment_status = 'Paid'

        db_session.add(query_balance)
        db_session.add(movie_selling)
        db_session.add(add_ticket)
        db_session.add(query)
        db_session.commit()
        return {"Message": "Success", "Current balance": query_balance.w_balance}, 200

    if action == 'cancel':
        query.payment_status = 'Canceled'
        query_order_seat = ModelOrderSeat.query.filter_by(id_order=query.id_order).all()
        for row in query_order_seat:
            db_session.delete(row)
            db_session.commit()
    else:
        return {"Error": "Invalid action"}, 400
