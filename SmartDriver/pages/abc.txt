import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import folium
from streamlit_folium import st_folium
from datetime import datetime
import requests
import cloudinary
import cloudinary.uploader
import torch
import numpy as np
from PIL import Image
from transformers import SegformerFeatureExtractor, SegformerForSemanticSegmentation

# Set Page Config
st.set_page_config(page_title="Road Hazard", page_icon="🚧", layout="wide", initial_sidebar_state="collapsed")

# Background CSS
background_css = """
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
"""
st.markdown(background_css, unsafe_allow_html=True)

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

# Load SegFormer Model
@st.cache_resource
def load_segformer():
    model_name = "nvidia/segformer-b2-finetuned-cityscapes-1024-1024"
    feature_extractor = SegformerFeatureExtractor.from_pretrained(model_name)
    model = SegformerForSemanticSegmentation.from_pretrained(model_name)
    return feature_extractor, model

feature_extractor, model = load_segformer()

# Function to check if the image contains a road
def is_road_present(image):
    inputs = feature_extractor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    segmentation_map = outputs.logits.argmax(dim=1).squeeze().cpu().numpy()
    road_pixel_count = np.sum(segmentation_map == 0)
    road_percentage = (road_pixel_count / segmentation_map.size) * 100
    return road_percentage > 10

# Initialize Session State for Selected Location
if "selected_location" not in st.session_state:
    st.session_state["selected_location"] = None

# File Upload Section
st.markdown("### Upload a Hazard Report")
uploaded_file = st.file_uploader("📸 Upload an image of the hazard", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    
    if is_road_present(image):
        st.image(image, caption="✅ Road detected! Proceeding with upload...")
        option = st.radio("Select Location Input Method:", ["Live Location", "Choose on Map"])

        gps_location = None

        if option == "Live Location":
            gps_response = requests.get("https://ipinfo.io/json")
            gps_location = gps_response.json().get("loc", "Unknown Location") if gps_response.status_code == 200 else "Unknown Location"
            st.write(f"📍 **Live Location:** {gps_location}")

        else:  # Choose on Map
            st.markdown("### Select a Location on the Map")
            
            # Default map
            map_location = [20, 78]  # Default to India's center
            
            # Use selected location if available
            if st.session_state["selected_location"]:
                lat, lon = map(float, st.session_state["selected_location"].split(","))
                map_location = [lat, lon]
            
            m = folium.Map(location=map_location, zoom_start=5)
            
            # Add marker if location is selected
            if st.session_state["selected_location"]:
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.Icon(color="blue", icon="map-marker")
                ).add_to(m)

            map_data = st_folium(m, height=500, width="100%")  # Single interactive map

            # Capture click events and update session state
            if map_data and map_data["last_clicked"]:
                lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
                st.session_state["selected_location"] = f"{lat},{lon}"
                st.rerun()  # Refresh the app to update the marker

            # Reset Marker Button
            if st.button("Reset Marker"):
                st.session_state["selected_location"] = None
                st.rerun()

            # Show selected location
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
                    st.session_state["selected_location"] = None  # Reset location after upload
                except Exception as e:
                    st.error(f"Failed to upload image: {e}")

    else:
        st.image(image, caption="🚫 No road detected! Please upload a valid road hazard image.")
        st.error("🚨 **Road not detected! Upload a proper road hazard image.**")
