from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from bson import ObjectId
from dotenv import load_dotenv
import cloudinary
from cloudinary.uploader import upload
from db import mongo
from werkzeug.utils import secure_filename
from models import store_user_data
from Aimodel import predict_numeric_severity
load_dotenv()
upload_bp = Blueprint('upload', __name__)
history_bp = Blueprint('get_history', __name__)
print("Hlo upload")
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True
)
@upload_bp.route('', methods=['POST'])
@jwt_required()
def upload_image():
    print("hlo path")
    if 'file' not in request.files:
        # print("hlo")
        return jsonify({"message": "No file uploaded"}), 200
    # print("cloud")
    file = request.files['file']
    # print(file)
    result = cloudinary.uploader.upload(
        file,
        folder="user"
    )
    # file = request.files['file']
    file_bytes = file.read() 
    # print("aftercloud")
    filepath=result['secure_url']
    patient_name = request.form.get('name')
    patient_age = request.form.get('age')
    current_user=get_jwt_identity()
    # print(current_user)
    if not patient_name or not patient_age:
        return jsonify({"message": "Name and age are required"}), 200
    # filename = secure_filename(file.filename)
    answer=predict_numeric_severity(filepath)
    # print(answer.confidence)
    predicted_class = answer['prediction']       # → 'benign'
    confidence_score = answer['confidence']      # → '94.98%'
    severity_text = answer['severity']           # → 'Low severity'
    severity_level = 0
    if(predicted_class=='malignant'):
        severity_level=2
    elif(predicted_class=='benign'):
        severity_level=1
    store_user_data(patient_name,patient_age,predicted_class,confidence_score,severity_text,severity_level,filepath,current_user)
    response = {
        "message": "File uploaded successfully",
        "prediction": answer['prediction'],
        "confidence": answer['confidence'],
        "severity": answer['severity'],
        "severity_level": severity_level,
        "image_url": filepath
    }
    return jsonify(response)                   

@history_bp.route('', methods=['GET'])
@jwt_required()
def get_history():
    current_user=get_jwt_identity()
    # print(current_user)
    # history_data = list(mongo.db.user_data.find({}, {"_id": 0}))
    # print(history_data)
    user = mongo.db.users.find_one({"username": current_user})
    if not user or 'uploads' not in user:
        return jsonify([])

    upload_ids = user['uploads']  # this should be a list of ObjectIds
    # print("📦 Upload IDs:", upload_ids)

    # 2. Fetch all uploads from user_data that match those ObjectIds
    upload_docs = list(mongo.db.user_data.find(
        {"_id": {"$in": [ObjectId(uid) for uid in upload_ids]}},
        {"_id": 0}  # exclude _id if you want
    ))
    # print(upload_docs)
    # Exclude MongoDB ObjectId
    return jsonify(upload_docs)