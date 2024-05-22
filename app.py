
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
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("Google API Key is missing.")

# Set the page configuration for the Streamlit app
st.set_page_config(
    page_title="YouTube Comment Fun Generator",
    page_icon="🎉",
    layout="wide"
)

# Function to fetch YouTube comments
def fetch_youtube_comments(video_id):
    try:
        st.write("Initializing YouTube API client...")
        youtube = build('youtube', 'v3', developerKey=yt_api_key)
        st.write("Creating request to fetch comments...")
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100
        )
        st.write("Executing request to YouTube API...")
        response = request.execute()
        st.write("Processing response from YouTube API...")
        comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response['items']]
        st.write(f"Fetched {len(comments)} comments.")
        return comments
    except HttpError as e:
        st.error(f"An error occurred while fetching comments: {e}")
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
if video_id and st.button("Fetch Comments"):
    st.write("Starting to fetch comments...")
    comments = fetch_youtube_comments(video_id)
    if comments:
        st.success("Comments fetched successfully!")
        st.write(f"Comments: {comments}")
    else:
        st.warning("No comments found or failed to fetch comments.")

# Toggle display of comments
show_comments = st.checkbox("Show/Hide Comments")
if show_comments:
    if comments:
        st.write("Displaying fetched comments...")
        st.write("💬 Fetched YouTube Comments")
        for comment in comments:
            st.write(comment)
    else:
        st.write("No comments to display.")

# Categorize and display comments using Gemini
if comments:
    prompt = f"""List 5 comments categorizing them as funny, interesting, positive, negative, and serious from these comments: {" ".join(comments)}"""
    
    config = {
        "temperature": 0.8,
        "max_output_tokens": 2048,
    }

    if st.button("Categorize Comments"):
        st.write("Starting to categorize comments...")
        try:
            st.write("Initializing Google Gemini LLM client...")
            model = genai.GenerativeModel("gemini-pro", generation_config=config)
            st.write("Prompt being sent to Gemini LLM:")
            st.code(prompt)
            st.write("Sending request to Google Gemini LLM...")
            with st.spinner("Categorizing comments using Gemini..."):
                response = model.generate_content(prompt)
                st.write("Processing response from Google Gemini LLM...")
                if response:
                    categorized_comments = response.text
                    st.subheader("Categorized Comments")
                    st.write(categorized_comments)
                    st.success("Comments categorized successfully!")
                else:
                    st.error("Received an empty response from Gemini LLM.")
        except HttpError as e:
            st.error(f"An HTTP error occurred while categorizing comments: {e}")
        except Exception as e:
            st.error(f"An error occurred while categorizing comments: {e}")
