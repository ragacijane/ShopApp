from email.utils import parseaddr
import io
import csv
from flask import Flask, request, Response, jsonify
from sqlalchemy import and_

from configuration import Configuration
from manageShop.roleDecorator import roleCheck
from model import database, Products
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, get_jwt

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

@application.route('/update',methods=['POST'])
@jwt_required()
@roleCheck(role='owner')
def updateProduct():
    content = request.files[""].stream.read().decode('utf-8')
    stream = io.StringIO(content)
    reader = csv.reader(stream)
    products = []
    counter = 0
    for row in reader:
        productExist = Products.query.filter(Products.product == row[1]).first()
        if(len(row[0]) == 0 or len(row[1]) == 0 or len(row[2]) == 0):
            return jsonify(message = f"Incorrect number of values on line {counter}."), 400
        elif(float(row[2]) < 0):
            return jsonify(message=f"Incorrect price on line {counter}."), 400
        elif(productExist):
            return jsonify(message=f"Product {row[1]} allready exists."), 400
        product = Products (product=row[1], category=row[0], price=float(row[2]))
        products.append(product)
        counter+=1
    database.session.add_all(products)
    database.session.commit()
    return Response(status=200)


@application.route('search?name=<PRODUCT_NAME>&category=<CATEGORY_NAME>', methods=["GET"])
@jwt_required()
@roleCheck(role = "customer")
def searchProduct(productName, categoryName):


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, port = 5001)