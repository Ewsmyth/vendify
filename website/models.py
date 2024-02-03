from flask_login import UserMixin
from . import db
from datetime import datetime
from flask_bcrypt import Bcrypt
import os
import uuid
from sqlalchemy.orm import relationship
from flask import current_app
from .utils import generate_unique_filename

bcrypt = Bcrypt()

ALLOWED_EXTENSIONS = {'png', 'PNG', 'jpg', 'jpeg', 'gif', 'mp4'}

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    authority = db.Column(db.String(20), default='user')
    theme = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy=True)
    cart = db.relationship('Cart', backref='user', lazy=True)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def calculate_cart_total(self):
        cart_items = Cart.query.filter_by(user_id=self.id).all()
        total_price = sum(cart_item.post.price * cart_item.quantity for cart_item in cart_items)
        return total_price

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    cover_photo_url = db.Column(db.String(255), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    media = db.relationship('Media', backref='post', lazy=True)
    cart = db.relationship('Cart', backref='post', lazy=True)

    def is_allowed_extension(self, file_extension):
        return file_extension.lower() in ALLOWED_EXTENSIONS

    def generate_unique_filename(self, file_extension):
        if self.is_allowed_extension(file_extension):
            return generate_unique_filename(self.author.username, file_extension)
        else:
            raise ValueError("File extension not allowed")

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_url = db.Column(db.String(255), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class LogEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_description = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchaser_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)
    shipping_city = db.Column(db.String(255), nullable=False)
    shipping_state = db.Column(db.String(255), nullable=False)
    shipping_country = db.Column(db.String(255), nullable=False)
    shipping_zipcode = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    card_number = db.Column(db.Integer, nullable=False)
    card_holder = db.Column(db.String(255), nullable=False)
    card_expiry_date = db.Column(db.String(5), nullable=False)
    card_cvv = db.Column(db.Integer, nullable=False)
    order_status = db.Column(db.String(255), nullable=False, default='pending')
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_items = db.relationship('OrderItem', backref='order', lazy=True)
    purchaser = db.relationship('User', foreign_keys=[purchaser_id], backref='purchased_orders', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendor = db.relationship('User', foreign_keys=[vendor_id], backref='sold_orders', lazy=True)