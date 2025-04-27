# from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from db import mongo
import jwt
from flask_jwt_extended import create_access_token
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
# Reference to MongoDB collections
user_collection = mongo.db.users
user_data_collection = mongo.db.user_data

# User Details Schema (Authentication)
def create_user(username, password):
    hashed_password = generate_password_hash(password)
    existing_user = user_collection.find_one({"username": username})
    if existing_user:
        return {"message": "User already exists", "status": 400}
    user = {
        "username": username,
        "password": hashed_password,
    }
    user_collection.insert_one(user)
    return "User created successfully."

def verify_user(username, password):
    user = user_collection.find_one({"username": username})
    
    if user and check_password_hash(user["password"], password):
        access_token = create_access_token(identity=username, expires_delta=timedelta(hours=1))  # ✅ Fixed timedelta
        return {"token": access_token}
    return "User does not exist"
# User Data Schema (Storage)
def store_user_data(username, age, prediction, confidence, severity,severity_level, photo,current_user):
    system_time = datetime.now()
    # print(photo)
    user_data = {
        "username": username,
        "age": age,
        "prediction":prediction,
        "confidence": confidence,
        "severity": severity,
        "severity_level":severity_level,
        "photo": photo,
        "date": system_time.strftime('%d-%m-%Y'),
        "time": system_time.strftime('%H:%M:%S')
    }
    # inserted_doc = mongo.db.user_details.insert_one(user_data)
    inserted_doc=user_data_collection.insert_one(user_data)
    new_entry_id = str(inserted_doc.inserted_id)
    user_collection.update_one(
        {"username": current_user},
        {"$push": {"uploads": new_entry_id}}
    )
    # print(new_entry_id)
    return "User data stored successfully."
