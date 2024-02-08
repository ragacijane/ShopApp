from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class Products(database.Model):
    __tablename__ = 'products'
    id = database.Column(database.Integer, primary_key=True)
    product = database.Column(database.String(256), nullable=False, unique = True)
    category = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Float, nullable=False)

class Orders(database.Model):
    __tablename__ = 'orders'
    id = database.Column(database.Integer, primary_key=True)
    user_email = database.Column(database.String(256),nullable=False)
    products_id = database.Column(database.String(256), nullable=False)
    products_quantity = database.Column(database.String(256), nullable=False)
    total_price = database.Column(database.Float, nullable=False)
    timestamp = database.Column(database.DateTime,nullable=False)
    status = database.Column(database.String(256),nullable=False)