from flask import Blueprint, request
from virtualcinema.auth import auth
from virtualcinema.model.models import ModelAccount, ModelWallet
from virtualcinema.db.database import db_session

account = Blueprint('account', __name__)


@account.route('/account/<id_user>', methods=['GET'])
@auth
def handler_get_account(id_user):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if id_user == 'all':
            query = ModelAccount.query.join(ModelWallet).all()
            response = [{
                'id_user': row.id_user,
                'u_name': row.u_name,
                'u_username': row.u_username,
                'u_role': row.u_role,
                'wallet': ModelWallet.query.filter_by(id_user=row.id_user).first().w_balance
            } for row in query]
            return {"Message": "Success", "Count": len(response), "Data": response}, 200

        query = ModelAccount.query.filter_by(id_user=id_user).first()
        if not query:
            return {"Error": "Account not found"}, 404
        else:
            response = {
                'id_user': query.id_user,
                'u_name': query.u_name,
                'u_username': query.u_username,
                'u_role': query.u_role,
                'wallet': ModelWallet.query.filter_by(id_user=query.id_user).first().w_balance
            }
            return {"Message": "Success", "Data": response}, 200
    if session.u_role == 'User' and id_user == 'self':
        response = {
            'id_user': session.id_user,
            'u_name': session.u_name,
            'u_username': session.u_username,
            'u_role': session.u_role,
            'wallet': ModelWallet.query.filter_by(id_user=session.id_user).first().w_balance
        }
        return {"Message": "Success", "Data": response}, 200
    else:
        return {"Error": "Unauthorized"}, 401


@account.route('/account', methods=['POST'])
def handler_post_account():
    if request.is_json:
        json = request.get_json()
        add_account = ModelAccount(
            u_name=json['u_name'],
            u_username=json['u_username'],
            u_password=json['u_password'],
            u_role='User' if request.authorization is None else 'Admin' if ModelAccount.query.filter_by(
                u_username=request.authorization.username).first().u_role == 'Admin' else 'User')

        if ModelAccount.query.filter_by(u_username=add_account.u_username).first():
            return {"Error": "Username already exists"}, 400
        db_session.add(add_account)
        db_session.commit()

        add_wallet = ModelWallet(
            id_user=ModelAccount.query.filter_by(u_username=add_account.u_username).first().id_user,
            w_balance=0
        )
        db_session.add(add_wallet)
        db_session.commit()
        return {
            "Message": f"New {'User' if request.authorization is None else 'Admin' if ModelAccount.query.filter_by(u_username=request.authorization.username).first().u_role == 'Admin' else 'User'} added"}, 200
    else:
        return {"Message": "Invalid Request"}, 400


@account.route('/account/<id_user>', methods=['PUT'])
@auth
def handler_put_account(id_user):
    if request.is_json:
        session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
        json = request.get_json()
        if session.u_role == 'Admin':
            query = ModelAccount.query.filter_by(id_user=id_user).first()
            if not query:
                return {"Error": "Account not found"}, 404
            if 'u_name' in json:
                query.u_name = json['u_name']
            if 'u_username' in json:
                query.u_username = json['u_username']
            if 'u_password' in json:
                query.u_password = json['u_password']
            if 'u_role' in json:
                query.u_role = json['u_role']
            db_session.add(query)
            db_session.commit()
            return {"Message": "Account updated"}, 200
        else:
            query = ModelAccount.query.filter_by(
                id_user=ModelAccount.query.filter_by(u_username=request.authorization.username).first().id_user).first()
            if 'u_name' in json:
                query.u_name = json['u_name']
            if 'u_username' in json:
                query.u_username = json['u_username']
            if 'u_password' in json:
                query.u_password = json['u_password']
            if 'u_role' in json:
                return {"Error": "Can't change role"}, 401
            db_session.add(query)
            db_session.commit()
            return {"Message": "Account updated"}, 200
    else:
        return {"Message": "Invalid Request"}, 400


@account.route('/account/<id_user>', methods=['DELETE'])
@auth
def handler_delete_account(id_user):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        query_user = ModelAccount.query.filter_by(id_user=id_user).first()
        if not query_user:
            return {"Error": "Account not found"}, 404
        query_wallet = ModelWallet.query.filter_by(id_user=session.id_user).first()
        db_session.delete(query_wallet)
        db_session.commit()
        db_session.delete(query_user)
        db_session.commit()
        return {"Message": "Account deleted"}, 200
    else:
        query_user = ModelAccount.query.filter_by(
            id_user=ModelAccount.query.filter_by(u_username=request.authorization.username).first().id_user).first()
        query_wallet = ModelWallet.query.filter_by(id_user=query_user.id_user).first()
        db_session.delete(query_wallet)
        db_session.commit()
        db_session.delete(query_user)
        db_session.commit()
        return {"Message": "Account deleted"}, 200


@account.route('/wallet/<id_user>', methods=['GET'])
@auth
def handler_get_wallet(id_user):
    session = ModelAccount.query.filter_by(u_username=request.authorization.username).first()
    if session.u_role == 'Admin':
        if id_user == 'all':
            query = ModelWallet.query.all()
            response = [{
                'id_user': row.id_user,
                'w_balance': row.w_balance
            } for row in query]
            return {"Message": "Success", "Count": len(response), "Data": response}, 200

        query = ModelWallet.query.filter_by(id_user=id_user).first()
        if not query:
            return {"Error": "Wallet not found"}, 404
        else:
            response = {
                'id_user': query.id_user,
                'w_balance': query.w_balance
            }
            return {"Message": "Success", "Data": response}, 200
    if session.u_role == 'User' and id_user == 'self':
        response = {
            'id_user': session.id_user,
            'w_balance': ModelWallet.query.filter_by(id_user=session.id_user).first().w_balance
        }
        return {"Message": "Success", "Data": response}, 200
    else:
        return {"Error": "Unauthorized"}, 401