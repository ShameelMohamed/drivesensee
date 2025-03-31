import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import folium
from streamlit_folium import st_folium
from datetime import datetime
import requests
import cloudinary
import cloudinary.uploader
from io import BytesIO
import base64
from PIL import Image, ImageDraw
from inference_sdk import InferenceHTTPClient

# Streamlit Page Config
st.set_page_config(page_title="Road Hazard", page_icon="🚧", layout="wide", initial_sidebar_state="collapsed")

# Background CSS
st.markdown(
    """
    <style>
        .stApp {
            background-image: url('https://i.pinimg.com/originals/6d/46/f9/6d46f977733e6f9a9fa8f356e2b3e0fa.gif');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        header {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True
)

# Firebase Setup
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Cloudinary Setup
cloudinary.config(
    cloud_name="djj1sw8rh",
    api_key="894844811498647",
    api_secret="NdjntP2ahsNwzF39YH734dI8msM",
)

# Roboflow API Setup
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="6XrY7XG9vQ4bun00PHVw"
)
CONFIDENCE_THRESHOLD = 0.25  # 25% Confidence

# Function to detect potholes and draw bounding boxes
def detect_potholes_and_draw(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    result = CLIENT.infer(img_base64, model_id="pothole-detection-yolov12/7")

    if "predictions" in result and len(result["predictions"]) > 0:
        draw = ImageDraw.Draw(image)
        detected = False

        for obj in result["predictions"]:
            confidence = obj["confidence"]
            if confidence >= CONFIDENCE_THRESHOLD:
                detected = True
                x, y, width, height = obj["x"], obj["y"], obj["width"], obj["height"]
                x1, y1, x2, y2 = x - width / 2, y - height / 2, x + width / 2, y + height / 2
                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                draw.text((x1, y1 - 10), f"{confidence:.2f}", fill="red")

        return detected, image, result
    
    return False, image, None

# Initialize Session State for Selected Location
if "selected_location" not in st.session_state:
    st.session_state["selected_location"] = None

# File Upload Section
st.markdown("### Upload a Hazard Report")
uploaded_file = st.file_uploader("📸 Upload an image of the hazard", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    detected, processed_image, result = detect_potholes_and_draw(image)

    if detected:
        st.image(processed_image, caption="🛡️ Pothole Detected!", use_column_width=True)
        st.success("✅ Potholes detected and marked in red.")
        
    else:
        st.image(image, caption="🚫 No potholes detected.", use_column_width=True)
        st.error("🚫 No potholes detected above 25% confidence.")

    # Location Input Method
    option = st.radio("Select Location Input Method:", ["Live Location", "Choose on Map"])

    gps_location = None
    if option == "Live Location":
        gps_response = requests.get("https://ipinfo.io/json")
        gps_location = gps_response.json().get("loc", "Unknown Location") if gps_response.status_code == 200 else "Unknown Location"
        st.write(f"📍 **Live Location:** {gps_location}")
    else:
        st.markdown("### Select a Location on the Map")
        map_location = [20, 78]
        if st.session_state["selected_location"]:
            lat, lon = map(float, st.session_state["selected_location"].split(","))
            map_location = [lat, lon]
        
        m = folium.Map(location=map_location, zoom_start=5)
        if st.session_state["selected_location"]:
            folium.Marker([lat, lon], icon=folium.Icon(color="blue", icon="map-marker")).add_to(m)
        
        map_data = st_folium(m, height=500, width="100%")
        if map_data and map_data.get("last_clicked"):
            lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
            st.session_state["selected_location"] = f"{lat},{lon}"
            st.rerun()
        
        if st.button("Reset Marker"):
            st.session_state["selected_location"] = None
            st.rerun()
        
        if st.session_state["selected_location"]:
            st.write(f"📍 **Selected Location:** {st.session_state['selected_location']}")

    # Upload Button
    if (option == "Live Location" and gps_location) or (option == "Choose on Map" and st.session_state["selected_location"]):
        if st.button("Upload"):
            try:
                uploaded_file.seek(0)
                response = cloudinary.uploader.upload(uploaded_file, folder="hazard_images")
                image_url = response.get("secure_url")
                db.collection("uploads").add({
                    "gps_location": gps_location if option == "Live Location" else st.session_state["selected_location"],
                    "image_url": image_url,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                st.success("✅ Image and GPS location uploaded successfully!")
                st.session_state["selected_location"] = None
            except Exception as e:
                st.error(f"Failed to upload image: {e}")
