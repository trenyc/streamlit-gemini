# Streamlit App Code - Version 3.29

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

# Custom CSS for wider scroll bar and comment box styling
# Custom CSS for wider scroll bar and comment box styling
st.markdown("""
    <style>
    ::-webkit-scrollbar {
        width: 20px;  /* Adjust the width as needed */
    }
    ::-webkit-scrollbar-thumb {
        background-color: darkgrey;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-track {
        background: white;
    }
    .comment-box {
        background-color: #f9f9f9;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .comment-text {
        flex-grow: 1;
        margin-right: 10px;
    }
    .vote-button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .vote-button:hover {
        background-color: #45a049;
    }
    .batch-label {
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .horizontal-bar {
        border-top: 2px solid darkgrey;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


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

# Define OpenAI client (if API key available)
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)

# Main app content
st.title("YouTube Comments Categorizer")
st.caption("Unleash fun in YouTube comments with OpenAI")

# Function to search YouTube videos
def search_youtube_videos(query):
    try:
        youtube = build('youtube', 'v3', developerKey=yt_api_key)
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=5
        )
        response = request.execute()
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
                st.session_state.batch_number = 1  # Initialize batch number
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
        youtube = build('youtube', 'v3', developerKey=yt_api_key)
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=page_token
        )
        response = request.execute()
        comments = [{"id": item['snippet']['topLevelComment']['id'],
                     "text": item['snippet']['topLevelComment']['snippet']['textDisplay']} for item in response['items']]
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
    st.session_state.categorized_comments = {category: [] for category in ['funny']}
if 'top_voted_comments' not in st.session_state:
    st.session_state.top_voted_comments = {category: None for category in ['funny']}
if 'previously_rendered_comments' not in st.session_state:
    st.session_state.previously_rendered_comments = {category: [] for category in ['funny']}
if 'batch_number' not in st.session_state:
    st.session_state.batch_number = 1
if 'load_more_clicked' not in st.session_state:
    st.session_state.load_more_clicked = False

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
    if video_id not in st.session_state.votes:
        st.session_state.votes[video_id] = {}
    if comment_id not in st.session_state.votes[video_id]:
        st.session_state.votes[video_id][comment_id] = {category: {"up": 0}}
    return st.session_state.votes[video_id][comment_id].get(category, {"up": 0})

# Input for additional categories
categories = st_tags.st_tags(
    label='Add custom categories:',
    text='Press enter to add more',
    value=['funny'],
    suggestions=['funny'],
    maxtags=10,
)

# Update session state for categories
for category in categories:
    if category not in st.session_state.categorized_comments:
        st.session_state.categorized_comments[category] = []
    if category not in st.session_state.top_voted_comments:
        st.session_state.top_voted_comments[category] = None
    if category not in st.session_state.previously_rendered_comments:
        st.session_state.previously_rendered_comments[category] = []

# Function to create a prompt for categorization with token limits
def create_prompt_for_category(comments, category):
    top_voted_comment_id = st.session_state.top_voted_comments[category]
    example_comment = ""
    if top_voted_comment_id:
        top_voted_comment = next((comment for comment in st.session_state.comments if comment['id'] == top_voted_comment_id), None)
        if top_voted_comment:
            example_comment = top_voted_comment['text']
        else:
            example_comment = f"Comment with ID: {top_voted_comment_id}"
    if not example_comment:
        example_comment = category

    base_prompt = f"Categorize the following comments into the category '{category}'. Example of a '{category}' comment: '{example_comment}'. Comments: "

    token_limit = 15000  # Adjust this limit as needed to avoid exceeding the model's context length
    prompt = base_prompt
    for comment in comments:
        comment_text = comment['text']
        if len(prompt) + len(comment_text) + 2 > token_limit:  # +2 for the ", " separator
            break
        prompt += comment_text + ", "
    return prompt.rstrip(', ')

# Function to categorize comments for a specific category
def categorize_comments_for_category(category, comments, batch=1):
    prompt = create_prompt_for_category(comments, category)
    try:
        with st.spinner(f"Categorizing comments into {category} using OpenAI..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ]
            )
            if response.choices:
                response_text = response.choices[0].message.content.strip()
                # Strip introductory line and ignore example comment
                response_lines = response_text.split('\n')
                if response_lines and response_lines[0].count(':') > 0:
                    response_lines = response_lines[1:]
                response_lines = [line for line in response_lines if line.strip() and all(st.session_state.top_voted_comments[cat] is None or st.session_state.top_voted_comments[cat] not in line for cat in categories)]
                for line in response_lines:
                    line_text = line.strip()
                    if line_text:
                        if line_text not in [c['text'] for c in st.session_state.categorized_comments[category]]:
                            st.session_state.categorized_comments[category].append({"id": line_text, "text": line_text, "batch": batch})
            else:
                st.error(f"No response from the model for category: {category}")
    except APIError as e:
        st.error(f"An API error occurred: {e}")
        st.error(f"Error code: {e.status_code} - {e.message}")
        st.error(f"Full response: {e.response}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# Function to load more comments
def load_more_comments():
    st.session_state.load_more_clicked = True
    comments, next_page_token = fetch_youtube_comments(video_id, st.session_state.next_page_token)
    if comments:
        st.session_state.batch_number += 1  # Increment batch number here
        st.session_state.comments.extend(comments)  # Append new comments to the existing list
        st.session_state.next_page_token = next_page_token
        for category in categories:
            categorize_comments_for_category(category, comments, st.session_state.batch_number)
        st.session_state.load_more_clicked = False
        display_loaded_comments(st.session_state.batch_number, comments)  # Pass comments to display_loaded_comments
    else:
        st.warning("No more comments available.")
        st.session_state.load_more_clicked = False

# Fetch and categorize comments for each category
def fetch_and_categorize_comments():
    comments, next_page_token = fetch_youtube_comments(video_id)
    if comments:
        st.success("Comments fetched successfully!")
        # Prepend new comments to existing comments
        st.session_state.comments = comments + st.session_state.comments
        st.session_state.next_page_token = next_page_token
        st.session_state.batch_number = 1  # Initialize batch number
        for category in categories:
            categorize_comments_for_category(category, comments)
        st.subheader("Vote on Comments")
        display_categorized_comments(prevent_votes=False)  # Display categorized comments after fetching and categorizing
    else:
        st.warning("No comments found or failed to fetch comments.")

# Function to create vote button
buttoncount = 1
def create_vote_button(video_id, comment_id, category, vote_type="up"):
    button_text = f"👍 ({fetch_votes(video_id, comment_id, category)['up']})"
    
    button_key = f"{category}_{vote_type}_{comment_id}_{buttoncount}"
     
    if st.button(button_text, key=button_key):
        st.write("test")
        update_votes(video_id, comment_id, category, vote_type)
        st.rerun()  # Force rerun to update vote count

# Function to display categorized comments
def display_categorized_comments(prevent_votes=False):
    st.write("Displaying categorized comments")
    if isinstance(st.session_state.categorized_comments, dict):
        for current_category in st.session_state.categorized_comments.keys():  # Use current_category
            if len(st.session_state.categorized_comments[current_category]) > 0:  # Check if the list is not empty
                st.write(f"### {current_category.capitalize()}")
                st.write(f"Comments that are {current_category}:")

                comments = st.session_state.categorized_comments[current_category][:5]
                for idx, comment in enumerate(comments):
                    if comment['text'].strip():  # Ensure no blank comments are displayed
                        st.markdown(f"<div class='comment-box'><span>{comment['text']}</span>", unsafe_allow_html=True)
                        if not st.session_state.load_more_clicked:
                            create_vote_button(video_id, comment['id'], current_category)

            else:
                st.write(f"No comments found for {current_category}.")

# Function to display loaded comments categorized without voting buttons
def display_loaded_comments(batch_number, comments):
    st.markdown(f"<div class='horizontal-bar'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='batch-label'>Batch {batch_number}</div>", unsafe_allow_html=True)
    st.write("Displaying loaded comments")
    if isinstance(st.session_state.categorized_comments, dict):
        for current_category in st.session_state.categorized_comments.keys():
            st.write(f"### More {current_category.capitalize()} Comments")
            for comment in comments:
                if comment['text'].strip():
                    st.markdown(f"<div class='comment-box'><span>{comment['text']}</span></div>", unsafe_allow_html=True)

# Fetch and display YouTube comments
if 'selected_video_id' in st.session_state and yt_api_key and openai_api_key:
    if 'auto_fetch' in st.session_state and st.session_state.auto_fetch:
        fetch_and_categorize_comments()
        st.session_state.auto_fetch = False

# Always show the "Categorize Comments" button
if st.button("Categorize Comments"):
    fetch_and_categorize_comments()
    
   
# Display categorized comments and voting buttons only once
try:
    if 'categorized_comments' in st.session_state and any(st.session_state.categorized_comments.values()) and not st.session_state.load_more_clicked:
        display_categorized_comments(prevent_votes=True)
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")


# Load more comments button
if st.session_state.next_page_token:
    if st.button("Load More Comments"):
        with st.spinner("Loading more comments..."):
            load_more_comments()

if st.session_state.load_more_clicked:
    display_loaded_comments(st.session_state.batch_number, st.session_state.comments[-100:])  # Pass the last batch of comments
    st.session_state.load_more_clicked = False
