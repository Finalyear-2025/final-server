# from flask import Flask, Response, render_template
import base64
from bson import ObjectId
import matplotlib
matplotlib.use('Agg')  # <== Add this
import matplotlib.pyplot as plt
import numpy as np
import io
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import mongo
graph_bp=Blueprint('graph',__name__)

# Risk Report Generator
def generate_risk_report(confidence, severity):
    if severity == 2:  # Malignant
        if confidence >= 80:
            return "High Risk (Malignant)"
        elif confidence >= 60:
            return "Moderate Risk (Malignant)"
        else:
            return "Uncertain Risk (Malignant)"
    elif severity == 1:  # Benign
        if confidence >= 80:
            return "Low Risk (Benign)"
        elif confidence >= 60:
            return "Watchful (Benign)"
        else:
            return "Uncertain (Benign)"
    else:  # Normal
        if confidence >= 80:
            return "Normal (Confident)"
        else:
            return "Normal (Low Confidence)"


@graph_bp.route('', methods=['GET'])
@jwt_required()
def plot_png():
    confidence_list = []
    severity_list = []
    date_list = []

    current_user=get_jwt_identity()
    user = mongo.db.users.find_one({"username": current_user})
    # print(user)
    if not user or 'uploads' not in user:
        return jsonify([])
    upload_ids = user['uploads']
    upload_docs = list(mongo.db.user_data.find(
        {"_id": {"$in": [ObjectId(uid) for uid in upload_ids]}},
        {"_id": 0, "severity_level": 1, "date": 1,"confidence":1}  # exclude _id if you want
    ))
    
    # print(upload_docs)
    for doc in upload_docs:
        if "severity_level" in doc and "date" in doc:
            severity_list.append(int(doc["severity_level"]))  # Convert to int just in case
            date_list.append(doc["date"])
        confidence_str = doc["confidence"]
        if isinstance(confidence_str, str) and confidence_str.endswith('%'):
            confidence_value = float(confidence_str.strip('%'))
            confidence_list.append(confidence_value)    

    # print(confidence_list)
    # print(severity_list)


    risk_labels = [generate_risk_report(conf, sev) for conf, sev in zip(confidence_list, severity_list)]
    # print(risk_labels)
    plt.figure(figsize=(12, 6))
    x_vals = date_list

    plt.plot(x_vals, confidence_list, marker='o', linestyle='-', color='blue', label='Confidence Score')

    for i, (x, conf, label) in enumerate(zip(x_vals, confidence_list, risk_labels)):
        plt.text(x, conf + 2, label, ha='center', fontsize=9, rotation=45)

    plt.axhline(y=80, color='red', linestyle='--', label='80% Threshold')

    # plt.title("Confidence Scores with Risk Assessment")
    plt.xlabel("Date")
    plt.ylabel("Confidence (%)")
    plt.ylim(0, 110)
    plt.grid(True)
    plt.legend()

    # Save plot to BytesIO stream
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches="tight")
    img.seek(0)
    plt.close()
    encoded = base64.b64encode(img.getvalue()).decode('utf-8')
    # confidence_scores.clear()
    date_list.clear()
    severity_list.clear()
    risk_labels.clear()
    return jsonify({
    'image': encoded,
    'format': 'png',
    'status': 'success'
    })
