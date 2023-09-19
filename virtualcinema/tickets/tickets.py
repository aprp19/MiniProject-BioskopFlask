from datetime import datetime

from flask import Blueprint, request, json
from virtualcinema.auth import auth
from virtualcinema.models.models import ModelAccount, ModelTickets, ModelSeat

tickets = Blueprint('tickets', __name__)


@tickets.route('/tickets', methods=['GET'])
@auth
def handler_get_allticket():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    query = ModelTickets.query.filter_by(id_user=session.id_user).all()

    if session.u_role == 'Admin':
        query = ModelTickets.query.all()
    if not query:
        return {"Error": "Tickets not found"}, 404

    currentdate = datetime.now().date()

    response = [{
        "id_ticket": row.id_ticket,
        "film_name": row.orders.schedules.film.film_name,
        "order_seat": [ModelSeat.query.filter_by(id_seat=seat.id_seat).first().seat_number for seat in row.orders.orderseat],
        "order_studio": row.orders.order_studio,
        "order_date": row.orders.order_date,
        "order_time": json.dumps(row.orders.order_time, default=str),
        "ticket_status": "Active" if currentdate == row.orders.order_date and currentdate <= row.orders.order_time or currentdate < row.orders.order_date else "Expired",
    } for row in query]
    return {"Message": "Success", "Count": len(response), "Data": response}, 200


@tickets.route('/tickets/<id_ticket>', methods=['GET'])
@auth
def handler_get_ticket(id_ticket):
    query = ModelTickets.query.filter_by(id_ticket=id_ticket).first()

    if not query:
        return {"Error": "Tickets not found"}, 404

    currentdate = datetime.now().date()

    response = {
        "id_ticket": query.id_ticket,
        "film_name": query.orders.schedules.film.film_name,
        "order_seat": [ModelSeat.query.filter_by(id_seat=seat.id_seat).first().seat_number for seat in query.orders.orderseat],
        "order_studio": query.orders.order_studio,
        "order_date": query.orders.order_date,
        "order_time": json.dumps(query.orders.order_time, default=str),
        "ticket_status": "Active" if currentdate == query.orders.order_date and currentdate <= query.orders.order_time or currentdate < query.orders.order_date else "Expired",
    }
    return {"Message": "Success", "Data": response}, 200
