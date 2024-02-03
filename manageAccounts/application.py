from email.utils import parseaddr

from flask import Flask, request, Response, jsonify
from sqlalchemy import and_

from configuration import Configuration
from model import database, User
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, get_jwt

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

@application.route('/test', methods=['GET'])
def test():
    return "Hello World!"

@application.route("/register_<inputRole>", methods=["POST"])
def registerAcc(inputRole):
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emptyEmail = len(email) == 0
    emptyPassword = len(password) == 0
    emptyForename = len(forename) == 0
    emptySurname = len(surname) == 0

    fieldname = lambda a, b, c, d: a if emptyEmail else b if emptyPassword else\
                c if emptyForename else d
    result = parseaddr(email)
    wrongEmail = len(result[1]) == 0

    userExists = User.query.filter(User.email==email).first()

    if (emptyEmail or emptyPassword or emptyForename or emptySurname):
        return jsonify(message=f"Field {fieldname('email','password','forename','surname')} is missing."),400
    elif (len(password) < 8):
        return jsonify(message="Invalid password."),400
    elif wrongEmail:
        return jsonify(message = "Invalid email."),400
    elif(userExists):
         return jsonify(message = "Email already exists."),400

    user = User(email = email, password = password, forename = forename, surname = surname, role=inputRole)
    database.session.add(user)
    database.session.commit()

    # role=Role.query.filter(Role.name==inputRole).first()
    #
    # userRole = UserRole(userId=user.id, roleId=role.id)
    # database.session.add(userRole)
    # database.session.commit()

    return Response(status=200)

@application.route("/",methods=["GET"])
def index():
    return "Hello World"

@application.route("/login", methods=["POST"])
def loginAcc():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emptyEmail = len(email) == 0
    emptyPasswor = len(password) == 0

    if(emptyEmail):
        return jsonify(message = "Field email is missing"),400
    elif(emptyPasswor):
        return jsonify(message = "Field password is missing"),400
    elif(parseaddr(email)[1] == 0):
        return jsonify(message = "Invalid email."),400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if(not user):
        return jsonify(message = "Invalid credentials."),400

    additionalClaims = {
        "email": user.email,
        "password": user.password,
        "forename": user.forename,
        "surname": user.surname,
        "roles": user.role
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    return jsonify(accessToken=accessToken),200

#TODO

@application.route("/delete", methods=["POST"])
@jwt_required()
def deleteAcc():
    identity = get_jwt_identity()
    userExist = User.query.filter(User.email == identity).first()
    if(userExist):
        User.query.filter(User.email == identity).delete()
        database.session.commit()
        return Response(status=200)
    else:
        return jsonify(message = "Unknown user."), 400


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host = "0.0.0.0", port = 5002)