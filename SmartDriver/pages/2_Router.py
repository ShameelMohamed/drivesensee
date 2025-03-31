import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import folium
from streamlit_folium import st_folium
import requests

st.set_page_config(page_title="Route Planner", page_icon="🗺️", layout="wide", initial_sidebar_state="collapsed")

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

# OpenRouteService API Key
ORS_API_KEY = "5b3ce3597851110001cf6248e6cfd54b45cc4191bcde2aa3dc9e4a67"

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")  # Replace with your Firebase credentials JSON file
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("🚗 SmartDriver - Route Planner with Hazard Warnings")

# Initialize session state
if "locations" not in st.session_state:
    st.session_state.locations = []
if "route_coords" not in st.session_state:
    st.session_state.route_coords = None

# Reset markers button
if st.button("Reset Markers"):
    st.session_state.locations = []
    st.session_state.route_coords = None

# Initialize map (Consistent Zoom)
map_center = [20.5937, 78.9629]  # Default center: India
m = folium.Map(location=map_center, zoom_start=5)

# Add existing markers
for idx, loc in enumerate(st.session_state.locations):
    label = "Start" if idx == 0 else "Destination"
    folium.Marker(location=loc, popup=label, icon=folium.Icon(color="blue")).add_to(m)

# Display the first map (Fixed height)
map_data = st_folium(m, height=600, width="100%")  

# Capture clicked points
if map_data and map_data.get("last_clicked"):
    lat, lng = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
    if len(st.session_state.locations) < 2:
        st.session_state.locations.append((lat, lng))

# Display selected locations
if len(st.session_state.locations) == 2:
    st.write(f"🔹 *Start:* {st.session_state.locations[0]}")
    st.write(f"🔹 *Destination:* {st.session_state.locations[1]}")
else:
    st.write("Click two points on the map to set the Start and Destination.")

# Route type selection
route_type = st.radio("Select Route Type", ["Shortest Route", "Safest Route"])

# Function to fetch hazard locations from Firebase
def fetch_hazard_locations():
    hazard_docs = db.collection("uploads").stream()
    hazards = []
    for doc in hazard_docs:
        data = doc.to_dict()
        if "gps_location" in data:
            lat, lon = map(float, data["gps_location"].split(","))
            img_url = data.get("image_url", "")
            hazards.append((lat, lon, img_url))
    return hazards

# Function to fetch the route
def get_route(start, end, avoid_hazards=False):
    if not start or not end:
        return None, "Select both start and destination points."

    ors_url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}

    payload = {
        "coordinates": [[start[1], start[0]], [end[1], end[0]]],
        "radiuses": [500, 500],
    }

    if avoid_hazards:
        hazards = fetch_hazard_locations()
        if hazards:
            avoid_polygons = {
                "type": "MultiPolygon",
                "coordinates": []
            }

            for hazard in hazards:
                lat, lon = hazard[0], hazard[1]
                
                # Small square buffer around each hazard
                buffer_size = 0.001  # ~500m
                polygon = [[
                    [lon - buffer_size, lat - buffer_size],
                    [lon + buffer_size, lat - buffer_size],
                    [lon + buffer_size, lat + buffer_size],
                    [lon - buffer_size, lat + buffer_size],
                    [lon - buffer_size, lat - buffer_size]  # Close the polygon
                ]]
                
                avoid_polygons["coordinates"].append(polygon)
            
            payload["options"] = {"avoid_polygons": avoid_polygons}

    response = requests.post(ors_url, headers=headers, json=payload)

    if response.status_code == 200:
        response_json = response.json()
        if "features" in response_json and response_json["features"]:
            route_data = response_json["features"][0]["geometry"]["coordinates"]
            route_coords = [(lat, lng) for lng, lat in route_data]
            return route_coords, None

    return None, f"Route not found. Error: {response.text}"

# Button to calculate and show route
if st.button("Get Route"):
    if len(st.session_state.locations) == 2:
        start, end = st.session_state.locations

        # Fetch route based on selected type
        avoid_hazards = route_type == "Safest Route"
        route_coords, error_msg = get_route(start, end, avoid_hazards)

        if route_coords:
            st.session_state.route_coords = route_coords
        else:
            st.error(error_msg)

# Render updated map with route (Fixed zoom)
route_map = folium.Map(
    location=st.session_state.locations[0] if st.session_state.locations else map_center,
    zoom_start=5  # FIXED: Same zoom as the first map
)

# Add markers
for idx, loc in enumerate(st.session_state.locations):
    label = "Start" if idx == 0 else "Destination"
    folium.Marker(location=loc, popup=label, icon=folium.Icon(color="blue")).add_to(route_map)

# Add hazard markers
hazard_locations = fetch_hazard_locations()
for hazard in hazard_locations:
    lat, lon, img_url = hazard
    popup_html = f"""
    <div style="text-align: center;">
        <img src="{img_url}" width="200px"><br>
        <b>🚧 Hazard Location</b><br>
        {lat}, {lon}
    </div>
    """
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color="red", icon="exclamation-triangle", prefix="fa")
    ).add_to(route_map)

# Add route if available
if st.session_state.route_coords:
    folium.PolyLine(st.session_state.route_coords, color="blue", weight=5, opacity=0.7).add_to(route_map)

# Display the final map (Fixed height)
st_folium(route_map, height=600, width="100%")  # FIXED: Ensures consistent height