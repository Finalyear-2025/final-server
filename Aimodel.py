import numpy as np
import cv2
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
import requests

MODEL_PATH = "breast_ultrasound_model_final.h5"
model = tf.keras.models.load_model(MODEL_PATH)
model.save("new_model.keras")
# Label encoder setup
label_encoder = LabelEncoder()
label_encoder.classes_ = np.array(['benign', 'malignant', 'normal'])

# Severity mappings
severity_text_map = {
    "normal": "No severity",
    "benign": "Low severity",
    "malignant": "High severity"
}
severity_numeric_map = {
    "normal": 0,
    "benign": 1,
    "malignant": 2
}

def predict_numeric_severity(image_path, img_size=(128, 128)):
    """Processes an image and predicts its class using the trained model."""

    print("model")
    try:
        response = requests.get(image_path)
        if response.status_code != 200:
            return {"error": f"Failed to fetch image: {response.status_code}"}

        image_data = np.frombuffer(response.content, np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_GRAYSCALE)
    except Exception as e:
        return {"error": f"Error decoding image: {str(e)}"}

    if image is None:
        return {"error": "Error loading image from URL"}
    image_resized = cv2.resize(image, img_size)
    image_resized = np.expand_dims(image_resized, axis=-1)
    image_resized = image_resized / 255.0
    image_resized = np.expand_dims(image_resized, axis=0)

    prediction = model.predict(image_resized)
    predicted_idx = np.argmax(prediction)
    predicted_label = label_encoder.inverse_transform([predicted_idx])[0]
    confidence = prediction[0][predicted_idx] * 100

    return {
        "prediction": predicted_label,
        "confidence": f"{confidence:.2f}%",
        "severity": severity_text_map[predicted_label],
        "severity_level": severity_numeric_map[predicted_label]
    }