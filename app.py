import os
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openai import OpenAI, APIError
import streamlit_tags as st_tags

# Define API key environment variable names
YOUTUBE_API_KEY_ENV = "YOUTUBE_API_KEY"
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"

# Set the page configuration for the Streamlit app
st.set_page_config(
  page_title="Comment Buckets",
  page_icon="",
  layout="wide"
)

# Sidebar for API key inputs
with st.sidebar:
  st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png", width=64)
  st.title(" API Keys")
  
  # Try to retrieve API keys from environment variables (if available)
  yt_api_key = os.getenv(YOUTUBE_API_KEY_ENV, None)
  openai_api_key = os.getenv(OPENAI_API_KEY_ENV, None)

  # Optional input fields if environment variables are not set
  if not yt_api_key:
      yt_api_key = st.text_input('Enter YouTube API Key:', type='password', key="yt_key")
  if not openai_api_key:
      openai_api_key = st.text_input('Enter OpenAI API Key:', type='password', key="openai_key")

  debug_mode = st.checkbox("Debug Mode", value=False)

# Define OpenAI client (if API key available)
if openai_api_key:
  client = OpenAI(api_key=openai_api_key)
  if debug_mode:
    st.write(f"Using OpenAI API Key: ...{openai_api_key[-4:]}")

# Main app content
st.title(" Comment Buckets")
st.caption(" Unleash the fun in YouTube comments with OpenAI")
st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f31f.png", width=64)

# Function to search YouTube videos
def search_youtube_videos(query):
  try:
    if debug_mode:
      st.write("Searching for YouTube videos...")
    youtube = build('youtube', 'v3', developerKey=yt_api_key)
    request = youtube.search().list(
      part="snippet",
      q=query,
      type="video",
      maxResults=5
    )
    response = request.execute()
    if debug_mode:
      st.write("Processing search results...")
    return response['items']
  except HttpError as e:
    st.error(f"An error occurred while searching for videos: {e}")
    return []

# YouTube search and display functionality
search_query = st.text_input(" Search YouTube Videos", "Marques Brownlee")
if search_query and st.button("Search"):
  results = search_youtube_videos(search_query)
  if results:
    st.session_state.search_results = results

if 'search_results' in st.session_state:
  results = st.session_state.search_results
  cols = st.columns(3)
  for idx, result in enumerate(results):
    video_title = result['snippet']['title']
    video_id = result['id']['videoId']
    thumbnail_url = result['snippet']['thumbnails']['default']['url']
    with cols[idx % 3]:
      st.write(f"**{video_title}**")
      st.image(thumbnail_url, width=120)
      if st.button("Select", key=video_id):
        st.session_state.selected_video_id = video_id
        st.session_state.video_url = f"https://www.youtube.com/watch?v={video_id}"
        st.session_state.auto_fetch = True
        del st.session_state.search_

