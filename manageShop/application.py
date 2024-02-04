import datetime
import io
import csv
from flask import Flask, request, Response, jsonify

from configuration import Configuration
from roleDecorator import roleCheck
from model import database, Products, Orders
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route('/update',methods=['POST'])
@jwt_required()
@roleCheck(role='owner')
def updateProduct():
    file=request.files
    content = file.stream.read().decode('utf-8')
    stream = io.StringIO(content)
    reader = csv.reader(stream)
    if(len(reader) == 0):
        return jsonify(message="Field file missing."), 400
    products = []
    counter = 0
    for row in reader:
        productExist = Products.query.filter(Products.product == row[1]).first()
        if(len(row[0]) == 0 or len(row[1]) == 0 or len(row[2]) == 0):
            return jsonify(message = f"Incorrect number of values on line {counter}."), 400
        elif(float(row[2]) < 0):
            return jsonify(message=f"Incorrect price on line {counter}."), 400
        elif(productExist == None):
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
    orders = Orders.query.all()
    products=[]
    sold=[]
    waiting=[]
    statistics=[]
    for order in orders:
        listOfProducts=[int(x) for x in order.products_id.split("|")]
        listofQuantities=[int (x) for x in order.products_quantity.split("|")]
        for (product, quantity) in (listOfProducts, listofQuantities):
            if(order.status == "COMPLETE"):
                if product not in products:
                    products.append(product)
                    sold.append(quantity)
                    waiting.append(0)
                else:
                    sold[products.index(product)]+=quantity
            else:
                if product not in products:
                    products.append(product)
                    sold.append(0)
                    waiting.append(quantity)
                else:
                    waiting[products.index(product)]+=quantity
    for product in products:
        i=products.index(product)
        productName=Products.query.filter(Products.id == product).first()
        statistics.append({"name":productName.product,"sold":sold[i],"waiting":waiting[i]})
    return jsonify(statistics=statistics),200

@application.route('/category_statistics',methods=['GET'])
@jwt_required()
@roleCheck(role='owner')
def getCategoryStatistics():
    orders = Orders.query.all()
    sold = []
    statistics = []
    for order in orders:
        if (order.status == "COMPLETE"):
            listOfProducts = [int(x) for x in order.products_id.split("|")]
            listofQuantities = [int(x) for x in order.products_quantity.split("|")]
            for (product, quantity) in (listOfProducts, listofQuantities):
                tempProd=Products.query.filter(Products.id == product).first()
                categories= tempProd.category.split("|")
                for category in categories:
                    if category not in statistics:
                        statistics.append(category)
                        sold.append(quantity)
                    else:
                        sold[statistics.index(category)]+=quantity
    stats=dict(zip(statistics,sold))
    sortedStats=dict(sorted(stats.items(),key=lambda item: (-item[1], item[0])))
    statistics=list(sortedStats.keys())
    return jsonify(statistics=statistics),200


@application.route('/order',methods=["POST"])
@jwt_required()
@roleCheck(role = "customer")
def orderProduct():
    requests=request.json.get("request")
    productsIds=[]
    productQuantities=[]
    prices=[]
    if(requests is None):
        return jsonify(message="Field request is missing")
    for temp in requests:
        productExist = Products.query.filter(Products.id == temp['id']).first()
        if(temp['id'] == ''):
            return jsonify(message=f"Product id is missing for request number {requests.index(temp)}."),400
        elif(temp['quantity'] == ''):
            return jsonify(message=f"Product quantity is missing for request number {requests.index(temp)}."),400
        elif(not isinstance(temp['id'], int) or temp['id'] < 0):
            return jsonify(message=f"Invalid id for request number {requests.index(temp)}."),400
        elif (not isinstance(temp['quantity'], int) or temp['quantity'] < 0):
            return jsonify(message=f"Invalid quantity for request number {requests.index(temp)}."),400
        elif(not productExist):
            return jsonify(message=f"Invalid product for request number {requests.index(temp)}."),400
        else:
            productsIds.append(temp['id'])
            productQuantities.append(temp['quantity'])
            product=Products.query.filter(Products.id == temp['id']).first()
            prices.append(product.price*temp['quantity'])
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
    if request.args.get("name")is not None:
        name = request.args.get("name")
    else:
        name = ""
    if request.args.get("category") is not None:
        category = request.args.get("category")
    else:
        category = ""

    listOfCategories = []
    listOfProducts = []
    for line in Products.query.all():
        jsonProd = {
            "categories": [],
            "id": id,
            "name": "",
            "price": float()
        }
        categoriesSplit = line.category.split('|')
        for cat in categoriesSplit:
            if cat not in listOfCategories and category in cat.lower():
                if name in line.product.lower():
                    listOfCategories.append(cat)
                    jsonProd["categories"].append(cat)
        if name in line.product.lower() and jsonProd["categories"] != []:
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
        for (product,quantity) in (listOfProducts,listofQuantities):
            jsonProd = {
                "categories": [],
                "name": "",
                "price": float(),
                "quantity": int()
            }
            tempProduct=Products.query.filter(Products.id == product).first()
            jsonProd["categories"].append(tempProduct.category.split("|"))
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
    orderEmpty = Orders.query.filter(Orders.id == tempId).first()
    if(tempId==None):
        return jsonify(message="Missing order id."),400
    elif((not isinstance(tempId,int)) or tempId < 0 or orderEmpty==None):
        return jsonify(message="Invalid order id.”"),400
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
    orderEmpty = Orders.query.filter(Orders.id == tempId).first()
    if (tempId == None):
        return jsonify(message="Missing order id."), 400
    elif ((not isinstance(tempId, int)) or tempId < 0 or orderEmpty.status != "CREATED"):
        return jsonify(message="Invalid order id.”"), 400
    Orders.query.filter(Orders.id == tempId).update({"status": "PENDING"})
    database.session.commit()
    return Response(status=200)

@application.route("/",methods=["GET"])
def index():
    return "Hello World"

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host = "0.0.0.0", port = 5001)