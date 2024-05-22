import os
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import openai

# Set the page configuration for the Streamlit app
st.set_page_config(
    page_title="YouTube Comment Fun Generator",
    page_icon="🎉",
    layout="wide"
)

# Load environment variables from .env file
load_dotenv()

# Get the API keys from the environment variables
yt_api_key = os.getenv("YOUTUBE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Configure the OpenAI API with the API key
if openai_api_key:
    openai.api_key = openai_api_key
    st.write(f"Using OpenAI API Key: ...{openai_api_key[-4:]}")
else:
    st.error("OpenAI API Key is missing.")

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
    if 'OPENAI_API_KEY' in st.secrets:
        st.success('OpenAI API key provided!', icon='✅')
        openai_api_key = st.secrets['OPENAI_API_KEY']
    else:
        openai_api_key = st.text_input('Enter OpenAI API Key:', type='password')
        if not openai_api_key:
            st.warning('Please enter your OpenAI API Key!', icon='⚠️')

    if 'YOUTUBE_API_KEY' in st.secrets:
        st.success('YouTube API key provided!', icon='✅')
        yt_api_key = st.secrets['YOUTUBE_API_KEY']
    else:
        yt_api_key = st.text_input('Enter YouTube API Key:', type='password')
        if not yt_api_key:
            st.warning('Please enter your YouTube API Key!', icon='⚠️')

# Main app content
st.title("🎉 YouTube Comment Fun Generator")
st.caption("🚀 Unleash the fun in YouTube comments with OpenAI")
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
        st.session_state.comments = comments
    else:
        st.warning("No comments found or failed to fetch comments.")

# Toggle display of comments
if 'comments' in st.session_state:
    show_comments = st.checkbox("Show/Hide Comments")
    if show_comments:
        st.write("Displaying fetched comments...")
        st.write("💬 Fetched YouTube Comments")
        for comment in st.session_state.comments:
            st.write(comment)

# Categorize and display comments using OpenAI
if 'comments' in st.session_state and st.session_state.comments:
    prompt = f"""Categorize the following comments into categories: funny, interesting, positive, negative, and serious. Comments: {" ".join(st.session_state.comments)}"""

    if st.button("Categorize Comments"):
        st.write("Starting to categorize comments...")
        try:
            st.write("Prompt being sent to OpenAI API:")
            st.code(prompt)
            st.write(f"Using OpenAI API Key: ...{openai_api_key[-4:]}")
            st.write("Sending request to OpenAI API...")
            with st.spinner("Categorizing comments using OpenAI..."):
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=2048,
                    temperature=0.8
                )
                st.write("Processing response from OpenAI API...")
                categorized_comments = response.choices[0].text.strip()
                if categorized_comments:
                    st.subheader("Categorized Comments")
                    st.write(categorized_comments)
                    st.success("Comments categorized successfully!")
                else:
                    st.error("Received an empty response from OpenAI API.")
        except openai.error.OpenAIError as e:
            st.error(f"An OpenAI error occurred while categorizing comments: {e}")
        except AttributeError as e:
            st.error(f"An error occurred: {e}")
        except Exception as e:
            st.error(f"An error occurred while categorizing comments: {e}")
