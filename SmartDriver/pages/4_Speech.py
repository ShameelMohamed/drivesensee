import streamlit as st
import assemblyai as aai
import google.generativeai as gen_ai
import requests
import pyaudio
import wave
import os


st.set_page_config(page_title="AI Voice Assistant", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

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
 </style>
"""

# # Inject the CSS into the page
st.markdown(background_css, unsafe_allow_html=True)

# Configure APIs
aai.settings.api_key = "11c6274223b9472fa206d42b02f1de1f"
gen_ai.configure(api_key="AIzaSyByJzlUoKiO1y1xytWczcnQvda9SAwYReo")
model = gen_ai.GenerativeModel('gemini-1.5-flash')

ELEVENLABS_API_KEY = "sk_0cd655e3b51e9f00a46ccf3e4ff023583ac12cf612b33e21"
ELEVENLABS_VOICE_ID_MALE = "pNInz6obpgDQGcFmaJgB"
ELEVENLABS_VOICE_ID_FEMALE = "21m00Tcm4TlvDq8ikWAM"


st.title("🤖 Ask Pookie - Your AI Assistant")

# Sidebar settings
st.sidebar.header("Settings")
voice_selection = st.sidebar.radio("Select Voice", ["Male", "Female"])
ELEVENLABS_VOICE_ID = ELEVENLABS_VOICE_ID_FEMALE if voice_selection == "Female" else ELEVENLABS_VOICE_ID_MALE
ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

# Function to record live audio
def record_audio(filename="temp_audio.wav", duration=5, rate=44100, channels=1, chunk=1024):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

    frames = []
    
    for _ in range(0, int(rate / chunk * duration)):
        frames.append(stream.read(chunk))
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    
    st.success("Recording finished!")
    return filename

# Function to transcribe audio using AssemblyAI
def transcribe_audio(filename):
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(filename)
    return transcript.text if transcript else ""

# Function to get AI response
def gemini_chat(query):
    try:
        response = model.generate_content(f'''for the query '{query}' generate content in 10-25 words, and answer by what you understand and in response do not ask questions back ''')
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Function to convert text to speech
def text_to_speech_elevenlabs(text):
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }
    
    response = requests.post(ELEVENLABS_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        audio_content = response.content
        audio_path = "response_audio.mp3"
        with open(audio_path, "wb") as f:
            f.write(audio_content)
        return audio_path
    else:
        st.error(f"⚠ ElevenLabs API Error: {response.text}")
        return None

# Function to handle live voice input
def handle_live_voice_input():
    audio_path = record_audio()
    user_text = transcribe_audio(audio_path)
    
    if user_text.strip():
        st.success(f"Recognized: {user_text}")
        response = gemini_chat(user_text)
        st.subheader("AI Response")
        st.write(response)

        audio_path = text_to_speech_elevenlabs(response)
        if audio_path:
            st.audio(audio_path, format="audio/mp3")
        else:
            st.error("⚠ Failed to generate speech.")
    else:
        st.warning("❌ No speech detected, please try again.")

# Live Voice Input Button
if st.button("🎤 Speak Now"):
    handle_live_voice_input()