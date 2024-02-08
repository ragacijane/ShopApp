import re

from flask import Flask, request, Response, jsonify
from sqlalchemy import and_

from configuration import Configuration
from model import database, User
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, get_jwt

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

@application.route("/",methods=["GET"])
def index():
    return "Hello World"

@application.route("/register_<inputRole>", methods=["POST"])
def registerAcc(inputRole):
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    #.replace(" ","")
    emptyEmail = len(email) == 0
    emptyPassword = len(password) == 0
    emptyForename = len(forename) == 0
    emptySurname = len(surname) == 0


    userExists = User.query.filter(User.email==email).first()


    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    wrongEmail = re.fullmatch(regex,email)

    # fieldname = lambda a, b, c, d: a if emptyForename else b if emptySurname else \
    #     c if emptyEmail else d
    # if (emptyEmail or emptyPassword or emptyForename or emptySurname):
    #     return jsonify(message=f"Field {fieldname('forename','surname','email','password')} is missing."),400
    if emptyForename:
        return jsonify(message="Field forename is missing."), 400
    elif emptySurname:
        return jsonify(message="Field surname is missing."), 400
    elif emptyEmail:
        return jsonify(message="Field email is missing."), 400
    elif emptyPassword:
        return jsonify(message="Field password is missing."), 400
    elif (wrongEmail == None):
        return jsonify(message="Invalid email."),400
    elif (len(password) < 8):
        return jsonify(message="Invalid password."),400
    elif (userExists != None):
         return jsonify(message="Email already exists."),400

    user = User(email = email, password = password, forename = forename, surname = surname, role=inputRole)
    database.session.add(user)
    database.session.commit()

    return Response(status=200)

@application.route("/login", methods=["POST"])
def loginAcc():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emptyEmail = len(email) == 0
    emptyPasswor = len(password) == 0

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    wrongEmail = re.fullmatch(regex, email)

    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if(emptyEmail):
        return jsonify(message = "Field email is missing."),400
    elif(emptyPasswor):
        return jsonify(message = "Field password is missing."),400
    elif(wrongEmail == None):
        return jsonify(message = "Invalid email."),400
    elif(user == None):
        return jsonify(message = "Invalid credentials."),400

    additionalClaims = {
        "email": user.email,
        "password": user.password,
        "forename": user.forename,
        "surname": user.surname,
        "role": user.role
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    return jsonify(accessToken=accessToken),200

#TODO

@application.route("/delete", methods=["POST"])
@jwt_required()
def deleteAcc():
    identity = get_jwt_identity()
    userExist = User.query.filter(User.email == identity).first()
    if(userExist == None):
        return jsonify(message = "Unknown user."), 400
    else:
        User.query.filter(User.email == identity).delete()
        database.session.commit()
        return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host = "0.0.0.0", port = 5002)