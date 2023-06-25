from flask import Blueprint, request
from virtualcinema.auth import auth
from virtualcinema.models.models import ModelAccount, ModelTickets

tickets = Blueprint('tickets', __name__)


@tickets.route('/tickets', methods=['GET'])
@auth
def handler_get_ticket():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    query = ModelTickets.query.filter_by(id_user=session.id_user).all()

    if session.u_role == 'Admin':
        query = ModelTickets.query.all()
    if not query:
        return {"Error": "Tickets not found"}, 404

    response = [{
        "id_ticket": row.id_ticket,
        "film_name": row.orders.schedules.film.film_name,
        "order_seat": row.orders.order_seat,
        "order_studio": row.orders.order_studio,
        "order_date": row.orders.order_date,
        "order_time": row.orders.order_time,
    } for row in query]
    return {"Message": "Success", "Count": len(response), "Data": response}, 200
