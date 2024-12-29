from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
import requests
import os
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.models import Sequential

# Cài đặt địa chỉ ESP32-CAM
ESP32_IP = "http://192.168.17.11"  # Địa chỉ IP của ESP32-CAM

# Tạo lại cấu trúc mô hình
conv_base = DenseNet121(
    weights='imagenet',
    include_top=False,
    input_shape=(256, 256, 3),
    pooling='avg'
)

model = Sequential([
    conv_base,
    BatchNormalization(),
    Dense(256, activation='relu'),
    Dropout(0.35),
    BatchNormalization(),
    Dense(120, activation='relu'),
    Dense(10, activation='softmax')
])

# Tải trọng số đã lưu
model.load_weights("leaf_disease_model.keras")
labels = [
    "Tomato__BacteriaL_spot",
    "Tomato_Early_blight",
    "Tomato_Late_blight",
    "Tomato__Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato__Spider_mite",
    "Tomato_Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato__healthy"
]

# Tạo Flask app
app = Flask(__name__)
UPLOAD_FOLDER = 'static/'  # Thư mục chứa ảnh
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Đảm bảo thư mục tồn tại
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def check_esp32():
    try:
        response = requests.get(ESP32_IP, timeout=3)  # Thử gửi yêu cầu đến ESP32
        return response.status_code == 200
    except:
        return False

def turn_on_flash():
    if check_esp32():
        try:
            response = requests.get(f"{ESP32_IP}/led/on")  # Correctly send parameters
            if response.status_code == 200:
                print("Flash is ON")
            else:
                print("Failed to turn ON flash:", response.text)
        except Exception as e:
            print("Error while sending flash ON request:", e)
    else:
        print("ESP32 is offline. Cannot turn ON flash.")

def turn_off_flash():
    if check_esp32():
        try:
            response = requests.get(f"{ESP32_IP}/led/off")  # Correctly send parameters
            if response.status_code == 200:
                print("Flash is OFF")
            else:
                print("Failed to turn OFF flash:", response.text)
        except Exception as e:
            print("Error while sending flash OFF request:", e)
    else:
        print("ESP32 is offline. Cannot turn OFF flash.")


# Dự đoán tình trạng lá
def predict_leaf_health(image_path):
    image = cv2.imread(image_path)
    image_resized = cv2.resize(image, (256, 256))
    image_array = np.expand_dims(image_resized, axis=0) / 255.0
    predictions = model.predict(image_array)
    label_index = np.argmax(predictions)
    return labels[label_index], float(predictions[0][label_index])

# Endpoint để chụp ảnh từ ESP32
@app.route("/capture", methods=["GET"])
def capture_image():
    ESP32_URL = f"{ESP32_IP}/capture"
    response = requests.get(ESP32_URL)
    if response.status_code == 200:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], "leaf.jpg")
        with open(image_path, "wb") as f:
            f.write(response.content)
        label, confidence = predict_leaf_health(image_path)
        if label == "Tomato_Target_Spot" or label == "Tomato__healthy":
            turn_on_flash()
        else:
            turn_off_flash()
        return jsonify({
            "status": "success",
            "label": label,
            "confidence": round(confidence, 2)
        })
    return jsonify({"status": "error", "message": "Failed to capture image from ESP32."})

# Endpoint để tải ảnh từ máy tính
@app.route("/upload", methods=["POST"])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded."})

    file = request.files['image']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file."})

    if file:
        # Lưu file
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], "leaf.jpg")
        file.save(image_path)

        # Dự đoán
        label, confidence = predict_leaf_health(image_path)
        if label == "Tomato_Target_Spot" or label == "Tomato__healthy":
            turn_on_flash()  # Bật đèn flash
        else:
            turn_off_flash()

        return jsonify({
            "status": "success",
            "label": label,
            "confidence": round(confidence, 2)
        })

# Trang chủ giao diện web
@app.route("/")
def home():
    return render_template("main.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)


