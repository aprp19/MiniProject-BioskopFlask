from virtualcinema.db import db


class ModelAccount(db.Model):
    __tablename__ = 'account'

    id_user = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    u_name = db.Column(db.String(25), nullable=False)
    u_username = db.Column(db.String(25), nullable=False)
    u_password = db.Column(db.String(25), nullable=False)
    u_role = db.Column(db.String(25), nullable=False)
    wallet = db.relationship('ModelWallet', backref='account', lazy=True)
    order = db.relationship('ModelOrder', backref='account', lazy=True)


class ModelWallet(db.Model):
    __tablename__ = 'wallet'

    id_wallet = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    id_user = db.Column(db.Integer, db.ForeignKey('account.id_user'), nullable=False)
    w_balance = db.Column(db.Integer, nullable=False)


class ModelFilm(db.Model):
    __tablename__ = 'film'

    id_film = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    film_name = db.Column(db.String(25), nullable=False)
    film_duration = db.Column(db.Integer, nullable=False)
    film_price = db.Column(db.Integer, nullable=False)
    film_selling = db.Column(db.Integer, nullable=False)
    film_category = db.relationship('ModelFilmCategory', backref='film', lazy=True)
    film_schedule = db.relationship('ModelFilmSchedule', backref='film', lazy=True)


class ModelCategory(db.Model):
    __tablename__ = 'category'

    id_category = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    category_name = db.Column(db.String(25), nullable=False)
    film_category = db.relationship('ModelFilmCategory', backref='category', lazy=True)


class ModelFilmCategory(db.Model):
    __tablename__ = 'filmcategory'

    id_film = db.Column(db.Integer, db.ForeignKey('film.id_film'), primary_key=True)
    id_category = db.Column(db.Integer, db.ForeignKey('category.id_category'), primary_key=True)


class ModelFilmSchedule(db.Model):
    __tablename__ = 'filmschedule'

    id_schedule = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    id_film = db.Column(db.Integer, db.ForeignKey('film.id_film'), nullable=False)
    schedule_studio = db.Column(db.String(25), nullable=False)
    schedule_date = db.Column(db.String(25), nullable=False)
    schedule_time = db.Column(db.String(25), nullable=False)
    schedule_price = db.Column(db.Integer, nullable=False)
    film_order = db.relationship('ModelOrder', backref='schedule', lazy=True)


class ModelSeat(db.Model):
    __tablename__ = 'seat'

    id_seat = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    seat_number = db.Column(db.String(25), nullable=False)
    orderseat = db.relationship('ModelOrderSeat', backref='seat', lazy=True)


class ModelOrder(db.Model):
    __tablename__ = 'orders'

    id_order = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    id_user = db.Column(db.Integer, db.ForeignKey('account.id_user'), nullable=False)
    id_schedule = db.Column(db.Integer, db.ForeignKey('filmschedule.id_schedule'), nullable=False)
    order_seat = db.Column(db.String(25), nullable=False)
    order_date = db.Column(db.String(25), nullable=False)
    order_qty = db.Column(db.Integer, nullable=False)
    order_total = db.Column(db.Integer, nullable=False)
    orderseat = db.relationship('ModelOrderSeat', backref='order', lazy=True)


class ModelOrderSeat(db.Model):
    __tablename__ = 'orderseat'

    id_order = db.Column(db.Integer, db.ForeignKey('orders.id_order'), primary_key=True)
    id_seat = db.Column(db.Integer, db.ForeignKey('seat.id_seat'), primary_key=True)
    film_name = db.Column(db.String(25), nullable=False)
    schedule_studio = db.Column(db.String(25), nullable=False)
    schedule_date = db.Column(db.String(25), nullable=False)
    schedule_time = db.Column(db.String(25), nullable=False)


class ModelPayment(db.Model):
    __tablename__ = 'payments'

    id_payment = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    id_order = db.Column(db.Integer, db.ForeignKey('order.id_order'), nullable=False)
    order_total = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.String(25), nullable=False)