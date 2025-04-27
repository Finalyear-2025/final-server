from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import user_collection,create_user,verify_user
auth_bp = Blueprint('auth', __name__)

  # Temporary user storage

@auth_bp.route('/signup', methods=['POST'])
def signup():
    print("hlo signup")
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    res=create_user(username,password)
    return jsonify({"message": res})
    
@auth_bp.route('/login', methods=['POST'])
def login():
    print("hlo login")
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    res=verify_user(username,password)
    return res
