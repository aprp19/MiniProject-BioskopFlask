from flask import Flask
from flask_cors import CORS
from virtualcinema.db.database import db
from virtualcinema.accounts.accounts import account
from virtualcinema.films.films import film
from virtualcinema.schedules.schedules import film_schedule
from virtualcinema.orders.orders import orders
from virtualcinema.seats.seats import seats
from virtualcinema.payments.payments import payments
from virtualcinema.tickets.tickets import tickets

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/VirtualCinema'
db.init_app(app)

app.register_blueprint(account)
app.register_blueprint(film)
app.register_blueprint(film_schedule)
app.register_blueprint(seats)
app.register_blueprint(orders)
app.register_blueprint(payments)
app.register_blueprint(tickets)

if __name__ == '__main__':
    app.run()
