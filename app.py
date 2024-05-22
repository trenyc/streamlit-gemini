import os
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openai import OpenAI, APIError

# Set the page configuration for the Streamlit app
st.set_page_config(
    page_title="YouTube Comment Fun Generator",
    page_icon="🎉",
    layout="wide"
)

# Sidebar for API key inputs
with st.sidebar:
    st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png", width=64)
    st.title("🔑 API Keys")
    
    yt_api_key = st.text_input('Enter YouTube API Key:', type='password')
    openai_api_key = st.text_input('Enter OpenAI API Key:', type='password')
    
    if yt_api_key and openai_api_key:
        st.success('API keys provided!', icon='✅')
    else:
        st.warning('Please enter both API keys!', icon='⚠️')

if yt_api_key and openai_api_key:
    # Configure the OpenAI API with the API key
    client = OpenAI(api_key=openai_api_key)
    st.write(f"Using OpenAI API Key: ...{openai_api_key[-4:]}")

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
else:
    st.warning("Please enter the required API keys to use the application.")
