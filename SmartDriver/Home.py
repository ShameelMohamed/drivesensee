import streamlit as st

# Set page configuration
st.set_page_config(page_title="Drive Sense", page_icon="🚗", layout="wide", initial_sidebar_state="collapsed")

# Define custom CSS for card styling and background image
background_css = """
<style>
    /* Background Image */
    .stApp {
        background-image: url('https://i.pinimg.com/originals/6d/46/f9/6d46f977733e6f9a9fa8f356e2b3e0fa.gif');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Hide default Streamlit header */
    header {
        visibility: hidden;
    }

    /* Card Styles */
    .card {
        background-color: rgba(0, 0, 0, 0.65);
        width: 100%;
        border-radius: 20px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        transition: transform 0.1s, box-shadow 0.2s;
        cursor: pointer;
        text-align: center;
    }
    .card:hover {
        transform: translateY(-30px);
        box-shadow: 0px 6px 10px rgba(0, 0, 0, 0.15);
    }
    .card img {
        width: 100%;
        height: 150px;
        object-fit: cover;
    }
    .card-title {
        font-size: 20px;
        font-weight: bold;
        margin: 10px 0;
        color: white;
    }
    .card-text {
        font-size: 14px;
        margin: 0 10px 10px;
        color: white;
    }
    .card-button {
        background-color: purple;
        color: white;
        text-decoration: none;
        padding: 10px 15px;
        border-radius: 5px;
        display: inline-block;
        margin-bottom: 15px;
        transition: background-color 0.1s;
    }
    .card-button:hover {
        background-color: purple;
    }
    
</style>
"""

# Inject the CSS into the page
st.markdown(background_css, unsafe_allow_html=True)

# Page title
st.subheader("")
st.title("Welcome to DriveSense !")
st.subheader("Your All-in-One Road Safety App")
st.subheader("")
# Create columns for horizontal layout
col1, col2, col3, col4 = st.columns(4)

# Card 1: Road Hazards
with col1:
    st.markdown(
        """
        <div class="card" onclick="window.location.href='RoadHazards'">
            <img src="https://media.istockphoto.com/id/538686713/photo/cracked-asphalt-after-earthquake.jpg?s=612x612&w=0&k=20&c=SbzwfmL_xf0rgZ4spkJPZ6wD6tR4AzkYEeA5iyg-_u4=" alt="Road Hazards">
            <div class="card-title">Road Hazards</div>
            <div class="card-text">Identify potential risks on your route and drive safer.</div>
            <a class="card-button" href="RoadHazards" onclick="window.location.href='RoadHazards'; return false;">Explore</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Card 2: Route Planner
with col2:
    st.markdown(
        """
        <div class="card" onclick="window.location.href='Router'">
            <img src="https://media.istockphoto.com/id/182150881/photo/mountain-highway-towards-the-clouds-haleakala-maui-hawaii.jpg?s=612x612&w=0&k=20&c=ZNAD3N_dqjPHO34ziErnMkqYfiebHDUyaP8226knUtg=" alt="Route Planner">
            <div class="card-title">Route Planner</div>
            <div class="card-text">Plan short and safe routes with advanced route planner.</div>
            <a class="card-button" href="Router" onclick="window.location.href='Router'; return false;">Explore</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Card 3: Fatigue Detection
with col3:
    st.markdown(
        """
        <div class="card" onclick="window.location.href='FatigueDetection'">
            <img src="https://img.freepik.com/premium-photo/dashboard-car-shows-dashboard-with-controls-dashboard_916191-384838.jpg" alt="Fatigue Detection">
            <div class="card-title">Fatigue Detection</div>
            <div class="card-text">Stay alert while driving with fatigue monitoring.</div>
            <a class="card-button" href="FatigueDetection" onclick="window.location.href='FatigueDetection'; return false;">Explore</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Card 4: AI Speech Bot
with col4:
    st.markdown(
        """
        <div class="card" onclick="window.location.href='Speech'">
            <img src="https://ichef.bbci.co.uk/ace/standard/1024/cpsprodpb/14202/production/_108243428_gettyimages-871148930.jpg" alt="AI Speech Bot">
            <div class="card-title">AI Speech Bot</div>
            <div class="card-text">Get real-time road safety advice from our speech bot.</div>
            <a class="card-button" href="Speech" onclick="window.location.href='Speech'; return false;">Explore</a>
        </div>
        """,
        unsafe_allow_html=True,
    )