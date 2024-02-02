from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class Products(database.Model):
    __tablename__ = 'products'
    id = database.Column(database.Integer, primary_key=True)
    product = database.Column(database.String(256), nullable=False, unique = True)
    category = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Float, nullable=False)
