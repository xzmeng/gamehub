from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin

from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

user_games = db.Table(
    'user_games',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    gender = db.Column(db.String(1))
    bill_address = db.Column(db.String(200))
    personal_introduction = db.Column(db.Text)
    phone_no = db.Column(db.String(50))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    photo_path = db.Column(db.String(256), default='/static/img/bg-img/ela.jpg')

    is_admin = db.Column(db.Boolean, default=False)

    orders = db.relationship('Order', backref='user', lazy='dynamic')

    refunds = db.relationship('Refund', backref='user', lazy='dynamic')

    games = db.relationship('Game', secondary=user_games, lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256:10')

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def is_administrator(self):
        return self.is_admin


class AnonymousUser(AnonymousUserMixin):
    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


game_genres = db.Table(
    'game_genres',
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), index=True, nullable=False)
    issued_date = db.Column(db.Date, nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    developer = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float)
    brief_introduction = db.Column(db.Text)

    rating_total = db.Column(db.Integer, default=0)
    rating_count = db.Column(db.Integer, default=0)

    version = db.Column(db.String(100))
    cover_path = db.Column(db.String(256))

    enabled = db.Column(db.Boolean, default=True, index=True)
    is_recommended = db.Column(db.Boolean, default=False, index=True)
    is_editor_picked = db.Column(db.Boolean, default=False, index=True)

    photos = db.relationship('GamePhoto', backref='game', lazy='dynamic')

    genres = db.relationship('Genre', secondary=game_genres, lazy='dynamic',
                             backref=db.backref('games', lazy='dynamic'))
    comments = db.relationship('Comment', backref='game', lazy='dynamic')

    @property
    def rating(self):
        if self.rating_count == 0:
            return 0
        return round(self.rating_total / self.rating_count, 1)

    def get_star_num(self):
        return round(self.rating / 2)


class GameRating(db.Model):
    __tablename__ = 'game_ratings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer)
    game = db.relationship('Game', backref=db.backref('game_ratings', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('game_ratings', lazy='dynamic'))


class GamePhoto(db.Model):
    __tablename__ = 'game_images'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    photo_path = db.Column(db.String(256))


class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    body = db.Column(db.Text)
    user = db.relationship('User', backref='comments')


cart_games = db.Table(
    'cart_games',
    db.Column('cart_id', db.Integer, db.ForeignKey('carts.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'), primary_key=True)
)


class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('cart', uselist=False))

    games = db.relationship('Game', secondary=cart_games, lazy='dynamic')


wishlist_games = db.Table(
    'wishlist_games',
    db.Column('wishlist_id', db.Integer, db.ForeignKey('wishlists.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'), primary_key=True)
)


class WishList(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('wishlist', uselist=False))

    games = db.relationship('Game', secondary=wishlist_games, lazy='dynamic')


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_cost = db.Column(db.Float())
    bill_address = db.Column(db.String(200))
    date = db.Column(db.Date())

    order_items = db.relationship('OrderItem', backref='order', lazy='dynamic')


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    game = db.relationship('Game')

    # available, refunding, refunded
    status = db.Column(db.String(30), default='available')


class Refund(db.Model):
    __tablename__ = 'refunds'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.Date)
    # pending, accepted, rejected
    status = db.Column(db.String(30), default='pending')
    msg = db.Column(db.String(200))
    refund_items = db.relationship('RefundItem', backref='refund', lazy='dynamic')


class RefundItem(db.Model):
    __tablename__ = 'refund_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    refund_id = db.Column(db.Integer, db.ForeignKey('refunds.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'))

    order_item = db.relationship('OrderItem')
