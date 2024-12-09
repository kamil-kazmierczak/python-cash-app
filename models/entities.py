from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    portfolios = db.relationship('UserPortfolio', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)


def find_user(username: str) -> User:
    return User.query.filter_by(username=username).first()


class Price(db.Model):
    __tablename__ = 'prices'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

    asset = db.relationship('Asset')

    __table_args__ = (
        db.UniqueConstraint('asset_id', 'date', name='asset_price_constraint'),
    )


class CurrencyRate(db.Model):
    __tablename__ = 'currency_rates'

    id = db.Column(db.Integer, primary_key=True)
    base_currency = db.Column(db.String(3), nullable=False)
    target_currency = db.Column(db.String(3), nullable=False)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('base_currency', 'target_currency', 'date', name='currency_rate_constraint'),
    )


def find_last_price(asset_name: str) -> Price:
    asset = Asset.query.filter_by(name=asset_name).first()
    return Price.query.filter_by(asset_id=asset.id).order_by(Price.date.desc()).first()


class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    unit = db.Column(db.String(80), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('name',  name='asset_name_constraint'),
    )

    def __repr__(self):
        return f'<Asset {self.id, self.name, self.unit}>'


class UserPortfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)

    user = db.relationship('User', back_populates='portfolios')
    asset = db.relationship('Asset')

    @property
    def current_value(self):
        return find_last_price(self.asset.name).value * self.quantity


def init_entities(app):
    with app.app_context():
        db.create_all()
