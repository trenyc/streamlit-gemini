
import os
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openai import OpenAI, APIError
import streamlit_tags as st_tags

# Set the page configuration for the Streamlit app
st.set_page_config(
    page_title="Comment Buckets",
    page_icon="🧩",
    layout="wide"
)

# Sidebar for API key inputs
with st.sidebar:
    st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png", width=64)
    st.title("🔑 API Keys")
    
    yt_api_key = st.text_input('Enter YouTube API Key:', type='password', key="yt_key")
    openai_api_key = st.text_input('Enter OpenAI API Key:', type='password', key="openai_key")

# Set up the default YouTube video and comments for the default view
default_video_url = "https://www.youtube.com/watch?v=-T0MGehwWvE"
default_comments = {
    "funny": [
        "a billion dollars idea for Apple: give iPad the 'MacPad' OS",
        "Watching on my iPad Pro 13 inch. This screen is heat",
        "Hey man it’s been too long, I need another MKBHD video",
        "I bet Apple is going to announce soon the introduction of MacOS apps in iPads just as the iPhone and iPads apps in MacOS",
        "When you realize they changed all the sizes from 12.9 inches to 13 inches or 10.9 to 11 inches to 'be more clean' when in reality your old magic keyboards are now obsolete and you need to buy some more ❤"
    ],
    "interesting": [
        "Apple is the brand ambassador of innovation for the sake of innovation",
        "The tech industry has started regressing and profit hunting",
        "The point of the M4 is energy efficiency, unlike the wild direction in the PC world",
        "The power of an iPad Pro is impressive for professional applications",
        "iPads have come a long way since the original Mini"
    ],
    "positive": [
        "Still using my iPad Pro 3rd gen bought 6 or 7 years ago, running well",
        "Hope to get another 5 years out of iPad Pro",
        "We are spoiled by Apple's incredible devices at a reasonable price",
        "iPads show amazing technology and manufacturing wizardry",
        "Impressed by the power and features of the new iPads"
    ],
    "negative": [
        "Apple seems to have reached its peak",
        "Concerns about Apple's innovation and direction",
        "Disappointment with restrictions on using Apple Pencil Pro and other accessories",
        "Frustration with thinness of iPads and camera bump design",
        "Criticism of Apple not focusing on OS and software development"
    ],
    "serious": [
        "Discussion about devices becoming thinner and the impact on battery",
        "Consideration of purchasing decisions based on needs and budget",
        "Professional use cases for upgraded iPad models",
        "Debate on the importance of software development over hardware upgrades",
        "Analystic comparison of various iPad models and their features"
    ]
}

# Define OpenAI client
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
    st.write(f"Using OpenAI API Key: ...{openai_api_key[-4:]}")

# Main app content
st.title("🎉 Comment Buckets")
st.caption("🚀 Unleash the fun in YouTube comments with OpenAI")
st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f31f.png", width=64)

# Function to search YouTube videos
def search_youtube_videos(query):
    try:
        st.write("Searching for YouTube videos...")
        youtube = build('youtube', 'v3', developerKey=yt_api_key)
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=5
        )
        response = request.execute()
        st.write("Processing search results...")
        return response['items']
    except HttpError as e:
        st.error(f"An error occurred while searching for videos: {e}")
        return []

# YouTube search and display functionality
search_query = st.text_input("🔍 Search YouTube Videos")
if search_query and st.button("Search"):
    results = search_youtube_videos(search_query)
    if results:
        for result in results:
            video_title = result['snippet']['title']
            video_id = result['id']['videoId']
            thumbnail_url = result['snippet']['thumbnails']['default']['url']
            st.write(f"**{video_title}**")
            st.image(thumbnail_url, width=120)
            if st.button(f"Select {video_title}", key=video_id):
                st.session_state.selected_video_id = video_id
                st.experimental_rerun()

# Set selected video ID from search results
if 'selected_video_id' in st.session_state:
    video_id = st.session_state.selected_video_id

# Input field for YouTube video URL
video_url = st.text_input("📺 Paste YouTube Video URL here:", default_video_url)
if video_url:
    try:
        # Check if 'v=' is present in the URL to extract video_id
        if 'v=' in video_url:
            video_id = video_url.split('v=')[-1]
        st.video(f"https://www.youtube.com/watch?v={video_id}", start_time=0, height=300)
    except Exception as e:
        st.error(f"Failed to display video: {e}")

# Function to fetch YouTube comments
def fetch_youtube_comments(video_id, order):
    try:
        st.write("Initializing YouTube API client...")
        youtube = build('youtube', 'v3', developerKey=yt_api_key)
        st.write("Creating request to fetch comments...")
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            order=order
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

# Toggle for most recent or top comments
comment_order = st.radio("Sort comments by:", ("relevance", "time"))

# Input for additional categories
categories = st_tags.st_tags(
    label='Add custom categories:',
    text='Press enter to add more',
    value=['funny', 'interesting', 'positive', 'negative', 'serious'],
    suggestions=['funny', 'interesting', 'positive', 'negative', 'serious'],
    maxtags=10,
)

# Display default categorized comments under the categorize button
if not ('comments' in st.session_state and st.session_state.comments):
    st.write("💬 Default Categorized Comments")
    for category, comment_list in default_comments.items():
        st.subheader(f"{category.capitalize()} Comments")
        for comment in comment_list:
            st.write(comment)

# Fetch and display YouTube comments
if video_id and yt_api_key and openai_api_key and st.button("Fetch Comments"):
    st.write("Starting to fetch comments...")
    comments = fetch_youtube_comments(video_id, comment_order)
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
    prompt = f"Categorize the following comments into categories: {', '.join(categories)}. Comments: {' '.join(st.session_state.comments)}"

    if st.button("Categorize Comments"):
        st.write("Starting to categorize comments...")
        try:
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
                st.write("Processing response from OpenAI API...")
                if response.choices:
                    response_text = response.choices[0].message.content.strip()
                    st.subheader("Categorized Comments")
                    st.write(response_text)
                    st.success("Comments categorized successfully!")
                else:
                    st.error("No response from the model.")
        except APIError as e:
            st.error(f"An API error occurred: {e}")
            st.error(f"Error code: {e.status_code} - {e.message}")
            st.error(f"Full response: {e.response}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
