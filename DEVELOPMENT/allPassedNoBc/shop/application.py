import datetime
import io
import csv
import os
import subprocess

from flask import Flask, request, Response, jsonify

from configuration import Configuration
from roleDecorator import roleCheck
from model import database, Products, Orders
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)
def isfloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

@application.route('/update',methods=['POST'])
@jwt_required()
@roleCheck(role='owner')
def updateProduct():
    fname=request.files.getlist('file')
    if ( len(fname) == 0):
        return jsonify(message="Field file is missing."), 400
    content = request.files['file'].stream.read().decode('utf-8')
    stream = io.StringIO(content)
    reader = csv.reader(stream)
    products = []
    counter = 0
    for row in reader:
        productExist = Products.query.filter(Products.product == row[1]).first()
        if(len(row) != 3):
            return jsonify(message=f"Incorrect number of values on line {counter}."), 400
        elif(len(row[0]) == 0 or len(row[1]) == 0 or len(row[2]) == 0):
            return jsonify(message = f"Incorrect number of values on line {counter}."), 400
        elif(isfloat(row[2]) == False):
            return jsonify(message=f"Incorrect price on line {counter}."), 400
        elif(float(row[2]) < 0):
            return jsonify(message=f"Incorrect price on line {counter}."), 400
        elif(productExist != None):
            return jsonify(message=f"Product {row[1]} already exists."), 400
        product = Products (product=row[1], category=row[0], price=float(row[2]))
        products.append(product)
        counter+=1
    database.session.add_all(products)
    database.session.commit()
    return Response(status=200)

@application.route('/product_statistics',methods=['GET'])
@jwt_required()
@roleCheck(role='owner')
def getProductStatistics():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/productsStatistics.py"
    os.environ[
        "SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"

    result = subprocess.check_output(["/template.sh"])
    return result.decode(),200

@application.route('/category_statistics',methods=['GET'])
@jwt_required()
@roleCheck(role='owner')
def getCategoryStatistics():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/caregoryStatistics.py"
    os.environ[
        "SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"

    result = subprocess.check_output(["/template.sh"])
    return result.decode(),200

@application.route('/order',methods=["POST"])
@jwt_required()
@roleCheck(role = "customer")
def orderProduct():
    listOfRequests=request.json.get("requests")
    print(listOfRequests)
    productsIds=[]
    productQuantities=[]
    prices=[]
    if(listOfRequests == None):
        return jsonify(message="Field requests is missing."),400
    for tempRequest in listOfRequests:

        if('id' not in tempRequest or tempRequest['id'] == ''):
            return jsonify(message=f"Product id is missing for request number {listOfRequests.index(tempRequest)}."),400
        elif('quantity' not in tempRequest or tempRequest['quantity'] == ''):
            return jsonify(message=f"Product quantity is missing for request number {listOfRequests.index(tempRequest)}."),400
        elif(not isinstance(tempRequest['id'], int) or tempRequest['id'] < 0):
            return jsonify(message=f"Invalid product id for request number {listOfRequests.index(tempRequest)}."),400
        elif (not isinstance(tempRequest['quantity'], int) or tempRequest['quantity'] < 0):
            return jsonify(message=f"Invalid product quantity for request number {listOfRequests.index(tempRequest)}."),400
        productExist = Products.query.filter(Products.id == tempRequest['id']).first()
        if(productExist == None):
            return jsonify(message=f"Invalid product for request number {listOfRequests.index(tempRequest)}."),400
        else:
            productsIds.append(tempRequest['id'])
            productQuantities.append(tempRequest['quantity'])
            product=Products.query.filter(Products.id == tempRequest['id']).first()
            prices.append(product.price*tempRequest['quantity'])
    time=datetime.datetime.now().replace(microsecond=0).isoformat()
    totalPrice=sum(prices)
    order= Orders(user_email = get_jwt_identity(),\
                  products_id="|".join(str(x) for x in productsIds),\
                  products_quantity="|".join(str(x) for x in productQuantities),\
                  total_price=totalPrice, timestamp=time, status="CREATED")
    database.session.add(order)
    database.session.commit()
    ord=Orders.query.order_by(Orders.id.desc()).first()
    return jsonify(id=ord.id), 200

@application.route('/search', methods=["GET"])
@jwt_required()
@roleCheck(role = "customer")
def searchProduct():
    if request.args.get("name") is not None:
        nameStr = request.args.get("name")
    else:
        nameStr = ""
    if request.args.get("category") is not None:
        categoryStr = request.args.get("category")
    else:
        categoryStr = ""

    listOfCategories = []
    listOfProducts = []
    for line in Products.query.all():
        jsonProd = {
            "categories": [],
            "id": int(),
            "name": "",
            "price": float()
        }
        categoriesSplit = line.category.split('|')
        for category in categoriesSplit:
            if nameStr in line.product.lower():
                if categoryStr in category.lower():
                    if category not in listOfCategories:
                        listOfCategories.append(category)
                    jsonProd["categories"].append(category)
        if nameStr in line.product.lower() and jsonProd["categories"] != []:
            jsonProd["id"] = line.id
            jsonProd["name"] = line.product
            jsonProd["price"] = float(line.price)
            listOfProducts.append(jsonProd)

    return jsonify(categories=listOfCategories, products=listOfProducts)

@application.route('/status',methods=["GET"])
@jwt_required()
@roleCheck(role="customer")
def statusOfOrder():
    listOfOrders=Orders.query.filter(Orders.user_email == get_jwt_identity()).all()
    orders=[]
    listOfProducts=[]
    listofQuantities=[]
    for order in listOfOrders:
        listOfProducts=[int(x) for x in order.products_id.split("|")]
        listofQuantities=[int (x) for x in order.products_quantity.split("|")]
        jsonOrder={
            "products": [],
            "price":float(),
            "status":order.status,
            "timestamp":order.timestamp.isoformat()
        }
        for (product,quantity) in zip(listOfProducts,listofQuantities):
            jsonProd = {
                "categories": [],
                "name": "",
                "price": float(),
                "quantity": int()
            }
            tempProduct=Products.query.filter(Products.id == product).first()
            for cat in tempProduct.category.split("|"):
                jsonProd["categories"].append(cat)
            jsonProd["name"] = tempProduct.product
            jsonProd["price"] = tempProduct.price
            jsonProd["quantity"] =quantity
            jsonOrder["products"].append(jsonProd)
            jsonOrder["price"] = order.total_price
        orders.append(jsonOrder)
    return jsonify(orders=orders)

@application.route('/delivered',methods=["POST"])
@jwt_required()
@roleCheck(role="customer")
def deliveredOrders():
    tempId=request.json.get("id")
    if(tempId==None):
        return jsonify(message="Missing order id."),400
    orderEmpty = Orders.query.filter(Orders.id == tempId).first()
    if((not isinstance(tempId,int)) or tempId < 0 or orderEmpty==None):
        return jsonify(message="Invalid order id."),400
    if(orderEmpty.status!="PENDING"):
        return jsonify(message="Invalid order id."), 400
    Orders.query.filter(Orders.id == tempId).update({"status":"COMPLETE"})
    database.session.commit()
    return Response(status=200)

@application.route('/orders_to_deliver',methods=["GET"])
@jwt_required()
@roleCheck(role="courier")
def orders_to_deliver():
    orderList = Orders.query.filter(Orders.status == "CREATED").all()
    orders=[]
    for order in orderList:
        orders.append({"id":order.id,"email":order.user_email})
    return jsonify({"orders":orders}),200

@application.route('/pick_up_order',methods=["POST"])
@jwt_required()
@roleCheck(role="courier")
def pick_up_order():
    tempId= request.json.get("id")
    if (tempId == None):
        return jsonify(message="Missing order id."), 400
    orderEmpty = Orders.query.filter(Orders.id == tempId).first()
    if ((not isinstance(tempId, int)) or tempId < 0 or orderEmpty==None):
        return jsonify(message="Invalid order id."), 400
    if orderEmpty.status != "CREATED":
        return jsonify(message="Invalid order id."), 400
    Orders.query.filter(Orders.id == tempId).update({"status": "PENDING"})
    database.session.commit()
    return Response(status=200)

@application.route("/",methods=["GET"])
def index():
    return "Hello World"

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host = "0.0.0.0", port = 5001)