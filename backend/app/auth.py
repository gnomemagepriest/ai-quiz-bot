from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import User

def create_token():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        response = jsonify(access_token=access_token)
        response.set_cookie('access_token_cookie', access_token, httponly=True)
        return response, 200
    return jsonify({"msg": "Bad username or password"}), 401

@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
