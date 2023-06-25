from flask import Blueprint, request
from virtualcinema.auth import auth
from virtualcinema.models.models import ModelAccount, ModelPayment, ModelOrder

payments = Blueprint('payments', __name__)


@payments.route('/payments', methods=['GET'])
@auth
def handler_get_payments():
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    query = ModelPayment.query.filter_by(id_order=ModelOrder.query.filter_by(id_user=session.id_user).first().id_order).all()

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
