from api_application import *

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
base=declarative_base()
class RolesUsers(db.Model,base):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer, db.ForeignKey('role.id'))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer,default=0)
    active = db.Column(db.Boolean,default=0)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship('Role', secondary='roles_users',
                         backref=db.backref('users', lazy='dynamic'))

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow().date())
    no_of_products = db.Column(db.Integer, default=0)  # Initialize to 0
    products = db.relationship('Product', backref='category', lazy='dynamic')

class Product(db.Model):
    __productname__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    manufacturer = db.Column(db.String(100))
    expiry = db.Column(db.DateTime)
    rate_per_unit = db.Column(db.Float,nullable=False)
    available_quantity = db.Column(db.Integer, nullable=False)
    units = db.Column(db.String(50), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow().date())

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,nullable=False)
    product_id = db.Column(db.Integer,nullable=False)
    Quantity = db.Column(db.Float,nullable=False)
    rate_per_unit = db.Column(db.Float,nullable=False)
    price_of_qty = db.Column(db.Float, nullable=False)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float,nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow())
    description = db.Column(db.String(100))
    items = db.relationship('OrderItem', backref='order', lazy='dynamic')
    
