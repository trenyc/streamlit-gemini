
import os
import streamlit as st
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get the API keys from the environment variables
yt_api_key = os.getenv("YOUTUBE_API_KEY")
api_key = os.getenv("GOOGLE_API_KEY")

# Configure the Google Generative AI with the API key
genai.configure(api_key=api_key)

# Set the page configuration for the Streamlit app
st.set_page_config(
    page_title="YouTube Comment Fun Generator",
    page_icon="🎉",
    layout="wide"
)

# Function to fetch YouTube comments
def fetch_youtube_comments(video_id):
    try:
        youtube = build('youtube', 'v3', developerKey=yt_api_key)
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100
        )
        response = request.execute()
        comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response['items']]
        return comments
    except HttpError as e:
        st.error(f"An error occurred: {e}")
        return []

# Sidebar for API key inputs
with st.sidebar:
    st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png", width=64)
    st.title("🔑 API Keys")
    if 'GOOGLE_API_KEY' in st.secrets:
        st.success('Google API key provided!', icon='✅')
        api_key = st.secrets['GOOGLE_API_KEY']
    else:
        api_key = st.text_input('Enter Google API Key:', type='password')
        if not api_key:
            st.warning('Please enter your Google API Key!', icon='⚠️')

    if 'YOUTUBE_API_KEY' in st.secrets:
        st.success('YouTube API key provided!', icon='✅')
        yt_api_key = st.secrets['YOUTUBE_API_KEY']
    else:
        yt_api_key = st.text_input('Enter YouTube API Key:', type='password')
        if not yt_api_key:
            st.warning('Please enter your YouTube API Key!', icon='⚠️')

# Main app content
st.title("🎉 YouTube Comment Fun Generator")
st.caption("🚀 Unleash the fun in YouTube comments with Google Gemini")
st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f31f.png", width=64)

# Input field for YouTube video URL
video_url = st.text_input("📺 Paste YouTube Video URL here:")
video_id = video_url.split('v=')[-1] if 'v=' in video_url else video_url

# Display YouTube video
if video_id:
    st.video(f"https://www.youtube.com/watch?v={video_id}")

# Fetch and display YouTube comments
comments = []
if video_id:
    if st.button("Fetch Comments"):
        comments = fetch_youtube_comments(video_id)

# Toggle display of comments
show_comments = st.button("Show/Hide Comments")
if show_comments and comments:
    st.write("💬 Fetched YouTube Comments")
    for comment in comments:
        st.write(comment)

# Categorize and display comments using Gemini
if comments:
    prompt = f"""List 5 comments categorizing them as funny, interesting, positive, negative, and serious from these comments: {" ".join(comments)}"""
    
    config = {
        "temperature": 0.8,
        "max_output_tokens": 2048,
    }

    if st.button("Categorize Comments"):
        try:
            model = genai.GenerativeModel("gemini-pro", generation_config=config)
            with st.spinner("Categorizing comments using Gemini..."):
                response = model.generate_content(prompt)
                if response:
                    categorized_comments = response.text
                    st.subheader("Categorized Comments")
                    st.write(categorized_comments)
        except Exception as e:
            st.error(f"An error occurred: {e}")
