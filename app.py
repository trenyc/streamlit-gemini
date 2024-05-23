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
    st.session_state.next_page_token = {category: None for category in ['funny', 'interesting', 'positive', 'negative', 'serious']}
if 'categorized_comments' not in st.session_state:
    st.session_state.categorized_comments = {category: [] for category in ['funny', 'interesting', 'positive', 'negative', 'serious']}
if 'top_voted_comments' not in st.session_state:
    st.session_state.top_voted_comments = {category: None for category in ['funny', 'interesting', 'positive', 'negative', 'serious']}
if 'load_count' not in st.session_state:
    st.session_state.load_count = {category: 0 for category in ['funny', 'interesting', 'positive', 'negative', 'serious']}

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
def create_prompt(category, comments):
    top_voted_comment = st.session_state.top_voted_comments[category]
    example_comments = []
    if top_voted_comment:
        voted_comments = sorted(
            [comment for comment in st.session_state.comments if video_id in st.session_state.votes and comment['id'] in st.session_state.votes[video_id] and st.session_state.votes[video_id][comment['id']][category]["up"] > 0],
            key=lambda x: (-st.session_state.votes[video_id][x['id']][category]["up"], x['id'])
        )
        example_comments = [comment['text'] for comment in voted_comments[:5]]

    if not example_comments:
        if debug_mode:
            st.write(f"No votes for category {category}")
    else:
        if debug_mode:
            st.write(f"Top voted comments for {category}: {example_comments}")

    example_text = " | ".join(example_comments)
    base_prompt = f"Categorize the following comments into the category '{category}'. Example comments: '{example_text}'. Comments: "
    token_limit = 15000  # Adjust this limit as needed to avoid exceeding the model's context length
    prompt = base_prompt
    for comment in comments:
        comment_text = comment['text']
        if len(prompt) + len(comment_text) + 2 > token_limit:  # +2 for the ", " separator
            break
        prompt += comment_text + ", "
    return prompt.rstrip(', ')

# Function to categorize comments for a specific category
def categorize_comments_for_category(category):
    prompt = create_prompt(category, st.session_state.comments)
    st.write(f"Starting to categorize comments for category: {category}")
    try:
        if debug_mode:
            st.write(f"Prompt for {category} being sent to OpenAI API:")
            st.code(prompt)
            st.write(f"Using OpenAI API Key: ...{openai_api_key[-4:]}")
            st.write("Sending request to OpenAI API...")
        with st.spinner(f"Categorizing comments into {category} using OpenAI..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ]
            )
            if debug_mode:
                st.write(f"Processing response from OpenAI API for category: {category}")
            if response.choices:
                response_text = response.choices[0].message.content.strip()
                if debug_mode:
                    st.write(f"Response from OpenAI API for {category}:")
                    st.code(response_text)
                # Strip introductory line
                if response_text.startswith("Here are the comments that fall into the category"):
                    response_text = response_text.split('\n', 1)[1]
                categorized_comments = response_text.split('\n')
                st.session_state.categorized_comments[category] = []  # Clear existing comments before adding new ones
                for comment in categorized_comments:
                    comment_text = comment.strip()
                    if comment_text and category in st.session_state.categorized_comments:
                        if len(st.session_state.categorized_comments[category]) < 5:
                            st.session_state.categorized_comments[category].append({"id": comment_text, "text": comment_text})
                # Display categorized comments for the category
                display_categorized_comments(category)
            else:
                st.error(f"No response from the model for category: {category}")
    except APIError as e:
        st.error(f"An API error occurred: {e}")
        st.error(f"Error code: {e.status_code} - {e.message}")
        st.error(f"Full response: {e.response}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# Fetch and categorize comments
def fetch_and_categorize_comments(category=None):
    if category:
        page_token = st.session_state.next_page_token.get(category, None)
    else:
        page_token = None
    comments, next_page_token = fetch_youtube_comments(video_id, page_token)
    if comments:
        st.success("Comments fetched successfully!")
        st.session_state.comments = comments  # Replace comments with the new batch
        if category:
            st.session_state.next_page_token[category] = next_page_token
            st.session_state.load_count[category] += 1  # Increment load count
            categorize_comments_for_category(category)
        else:
            st.session_state.next_page_token = {cat: next_page_token for cat in st.session_state.next_page_token.keys()}
            # Categorize comments for each category
            for category in categories:
                st.session_state.load_count[category] += 1  # Increment load count
                categorize_comments_for_category(category)
    else:
        st.warning("No comments found or failed to fetch comments.")

# Function to display categorized comments and voting buttons
def display_categorized_comments(category=None):
    if category:
        categories_to_display = [category]
    else:
        categories_to_display = st.session_state.categorized_comments.keys()

    for category in categories_to_display:
        st.write(f"### {category.capitalize()}")
        st.write(f"Vote for the comments that are {category}.")
        for idx, comment in enumerate(st.session_state.categorized_comments[category]):
            if comment['text'].strip():  # Ensure no blank comments are displayed
                st.write(comment['text'])
                votes = fetch_votes(video_id, comment['id'], category)
                if st.button(f"👍 ({votes['up']})", key=f"{category}_up_{comment['id']}_{idx}_{st.session_state.load_count[category]}"):
                    update_votes(video_id, comment['id'], category, "up")
                    st.experimental_rerun()
        if st.session_state.next_page_token.get(category):
            if st.button(f"Load More Comments for {category.capitalize()}", key=f"load_more_{category}_{st.session_state.load_count[category]}"):
                st.session_state.categorized_comments[category] = []  # Clear existing comments before loading more
                fetch_and_categorize_comments(category)

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
            st.write(comment['text'])

# Always show the "Categorize Comments" button
if st.button("Categorize Comments"):
    fetch_and_categorize_comments()

# Display categorized comments and voting buttons
if 'categorized_comments' in st.session_state:
    st.subheader("Vote on Comments")
    for category in st.session_state.categorized_comments.keys():
        display_categorized_comments(category)
