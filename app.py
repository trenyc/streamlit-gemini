# Streamlit App Code - Version 3.6

import os
import uuid
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openai import OpenAI, APIError
import streamlit_tags as st_tags

# Define API key environment variable names
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY_ENV"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY_ENV"]

# Set the page configuration for the Streamlit app
st.set_page_config(
    page_title="Comments Categorized",
    page_icon="",
    layout="wide"
)

# Sidebar for API key inputs
with st.sidebar:
    st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png", width=64)
    st.title("API Keys")

    # Try to retrieve API keys from environment variables (if available)
    yt_api_key = os.environ.get("YOUTUBE_API_KEY_ENV")
    openai_api_key = os.environ.get("OPENAI_API_KEY_ENV")

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
st.title("Comments Categorized")
st.caption("Unleash the fun in YouTube comments with OpenAI")
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
search_query = st.text_input("Search YouTube Videos", "Marques Brownlee tech reviews")
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
                del st.session_state.search_results
                st.experimental_rerun()  # Force a rerun to update state

# Set selected video ID from search results
if 'selected_video_id' in st.session_state:
    video_id = st.session_state.selected_video_id

# Input field for YouTube video URL
video_url = st.text_input("📺 Paste YouTube Video URL here:", st.session_state.get('video_url', "https://www.youtube.com/watch?v=-T0MGehwWvE"))
if video_url:
    try:
        # Check if 'v=' is present in the URL to extract video_id
        if 'v=' in video_url:
            video_id = video_url.split('v=')[-1]
        st.video(f"https://www.youtube.com/watch?v={video_id}", start_time=0)
    except Exception as e:
        st.error(f"Failed to display video: {e}")

# Function to fetch YouTube comments
def fetch_youtube_comments(video_id, page_token=None):
    try:
        if debug_mode:
            st.write("Initializing YouTube API client...")
        youtube = build('youtube', 'v3', developerKey=yt_api_key)
        if debug_mode:
            st.write("Creating request to fetch comments...")
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=page_token
        )
        if debug_mode:
            st.write("Executing request to YouTube API...")
        response = request.execute()
        if debug_mode:
            st.write("Processing response from YouTube API...")
        comments = [{"id": item['snippet']['topLevelComment']['id'],
                     "text": item['snippet']['topLevelComment']['snippet']['textDisplay']} for item in response['items']]
        if debug_mode:
            st.write(f"Fetched {len(comments)} comments.")
        next_page_token = response.get('nextPageToken', None)
        return comments, next_page_token
    except HttpError as e:
        st.error(f"An error occurred while fetching comments: {e}")
        return [], None

# Initialize session state for comments and pagination
if 'comments' not in st.session_state:
    st.session_state.comments = []
if 'next_page_token' not in st.session_state:
    st.session_state.next_page_token = None
if 'categorized_comments' not in st.session_state:
    st.session_state.categorized_comments = {category: [] for category in ['funny', 'interesting', 'positive', 'negative', 'serious']}
if 'top_voted_comments' not in st.session_state:
    st.session_state.top_voted_comments = {category: None for category in ['funny', 'interesting', 'positive', 'negative', 'serious']}

# Initialize votes in session state
if 'votes' not in st.session_state:
    st.session_state.votes = {}

# Function to update votes in session state
def update_votes(video_id, comment_id, category, vote):
    if video_id not in st.session_state.votes:
        st.session_state.votes[video_id] = {}
    if comment_id not in st.session_state.votes[video_id]:
        st.session_state.votes[video_id][comment_id] = {category: {"up": 0} for category in st.session_state.categorized_comments.keys()}
    if category not in st.session_state.votes[video_id][comment_id]:
        st.session_state.votes[video_id][comment_id][category] = {"up": 0}
    st.session_state.votes[video_id][comment_id][category][vote] += 1

    # Update top voted comments
    if vote == "up":
        current_top_comment = st.session_state.top_voted_comments[category]
        if current_top_comment is None or st.session_state.votes[video_id][comment_id][category]["up"] > st.session_state.votes[video_id][current_top_comment][category]["up"]:
            st.session_state.top_voted_comments[category] = comment_id

# Function to fetch votes from session state
def fetch_votes(video_id, comment_id, category):
    if video_id in st.session_state.votes and comment_id in st.session_state.votes[video_id]:
        return st.session_state.votes[video_id][comment_id].get(category, {"up": 0})
    else:
        return {"up": 0}

# Input for additional categories
categories = st_tags.st_tags(
    label='Add custom categories:',
    text='Press enter to add more',
    value=['funny', 'interesting', 'positive', 'negative', 'serious'],
    suggestions=['funny', 'interesting', 'positive', 'negative', 'serious'],
    maxtags=10,
)

# Function to create a prompt for categorization with token limits
def create_prompt_for_category(comments, category):
    top_voted_comment_id = st.session_state.top_voted_comments[category]
    example_comment = ""
    if top_voted_comment_id:
        top_voted_comment = next((comment for comment in st.session_state.comments if comment['id'] == top_voted_comment_id), None)
        if top_voted_comment:
            example_comment = top_voted_comment['text']
        else:
            if debug_mode:
                st.write(f"Top voted comment ID for {category} has no corresponding comment.")
            example_comment = f"Comment with ID: {top_voted_comment_id}"
    if debug_mode:
        st.write(f"Top voted comment ID for {category}: {top_voted_comment_id}")
        st.write(f"Top voted comment text for {category}: {example_comment}")

    if not example_comment:
        example_comment = category
        if debug_mode:
            st.write(f"No votes for category {category}. Using keyword '{category}' as example.")

