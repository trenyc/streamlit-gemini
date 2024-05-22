import os
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
    page_title="Comment Buckets",
    page_icon="",
    layout="wide"
)

# Sidebar for API key inputs
with st.sidebar:
    st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png", width=64)
    st.title("API Keys")


    # Try to retrieve API keys from environment variables (if available)
    yt_api_key = os.getenv(YOUTUBE_API_KEY, None)
    openai_api_key = os.getenv(OPENAI_API_KEY, None)

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
st.title("Comment Buckets")
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
search_query = st.text_input("Search YouTube Videos", "Marques Brownlee")
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

# Set selected video ID from search

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
def fetch_youtube_comments(video_id):
    try:
        if debug_mode:
            st.write("Initializing YouTube API client...")
        youtube = build('youtube', 'v3', developerKey=yt_api_key)
        if debug_mode:
            st.write("Creating request to fetch comments...")
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100
        )
        if debug_mode:
            st.write("Executing request to YouTube API...")
        response = request.execute()
        if debug_mode:
            st.write("Processing response from YouTube API...")
        comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response['items']]
        if debug_mode:
            st.write(f"Fetched {len(comments)} comments.")
        return comments
    except HttpError as e:
        st.error(f"An error occurred while fetching comments: {e}")
        return []

# Input for additional categories
categories = st_tags.st_tags(
    label='Add custom categories:',
    text='Press enter to add more',
    value=['funny', 'interesting', 'positive', 'negative', 'serious'],
    suggestions=['funny', 'interesting', 'positive', 'negative', 'serious'],
    maxtags=10,
)

# Fetch and categorize comments
def fetch_and_categorize_comments():
    comments = fetch_youtube_comments(video_id)
    if comments:
        st.success("Comments fetched successfully!")
        st.session_state.comments = comments
        prompt = f"Categorize the following comments into categories: {', '.join(categories)}. Comments: {' '.join(comments)}"
        st.write("Starting to categorize comments...")
        try:
            if debug_mode:
                st.write("Prompt being sent to OpenAI API:")
                st.code(prompt)
                st.write(f"Using OpenAI API Key: ...{openai_api_key[-4:]}")
                st.write("Sending request to OpenAI API...")
            with st.spinner("Categorizing comments using OpenAI..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ]
                )
                if debug_mode:
                    st.write("Processing response from OpenAI API...")
                if response.choices:
                    response_text = response.choices[0].message.content.strip()
                    st.success("Comments categorized successfully!")
                    st.subheader("Categorized Comments")
                    st.write(response_text)
                else:
                    st.error("No response from the model.")
        except APIError as e:
            st.error(f"An API error occurred: {e}")
            st.error(f"Error code: {e.status_code} - {e.message}")
            st.error(f"Full response: {e.response}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("No comments found or failed to fetch comments.")

# Fetch and display YouTube comments
if video_id and yt_api_key and openai_api_key:
    if 'auto_fetch' in st.session_state and st.session_state.auto_fetch:
        fetch_and_categorize_comments()
        st.session_state.auto_fetch = False

# Show "Fetch Comments" and "Show/Hide Comments" in debug mode
if debug_mode:
    if st.button("Fetch Comments"):
        fetch_youtube_comments(video_id)
    show_comments = st.checkbox("Show/Hide Comments")
    if show_comments and 'comments' in st.session_state:
        st.write("Displaying fetched comments...")
        st.write("💬 Fetched YouTube Comments")
        for comment in st.session_state.comments:
            st.write(comment)

# Always show the "Categorize Comments" button
if st.button("Categorize Comments"):
    fetch_and_categorize_comments()
