# Import necessary libraries
import os
import streamlit as st
import googleapiclient 
from googleapiclient import discovery
from googleapiclient import errors
import google.generativeai as genai 
from dotenv import load_dotenv
from PIL import Image


yttext = ''
# Load environment variables from .env file
load_dotenv()

# Get the Youtube API key from the environment variables
yt_api_key = os.getenv("YOUTUBE_API_KEY")

# Get the Google API key from the environment variables
api_key = os.getenv("GOOGLE_API_KEY")

# Configure the Google Generative AI with the API key
genai.configure(api_key=api_key)

# Set the page configuration for the Streamlit app
st.set_page_config(
    page_title="Google Gemini Comments",
    page_icon="🤖"
)

# Check if the Google API key is provided in the sidebar
with st.sidebar:
    if 'GOOGLE_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        api_key = st.secrets['GOOGLE_API_KEY']
    else:
        api_key = st.text_input('Enter Google API Key:', type='password')
        if not (api_key.startswith('AI')):
            st.warning('Please enter your API Key!', icon='⚠️')
        else:
            st.success('Success!', icon='✅')
    os.environ['GOOGLE_API_KEY'] = api_key
    "[Get a Google Gemini API key](https://ai.google.dev/)"
    "[View the source code](https://github.com/wms31/streamlit-gemini/blob/main/app.py)"
    "[Check out the blog post!](https://letsaiml.com/creating-google-gemini-app-with-streamlit/)"

# Check if the YOUTUBE API key is provided in the sidebar
with st.sidebar:
    if 'YOUTUBE_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        yt_api_key = st.secrets['YOUTUBE_API_KEY']
        api_service_name = "youtube"
        api_version = "v3"
        DEVELOPER_KEY=yt_api_key
          
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=DEVELOPER_KEY)
          
        request = youtube.commentThreads().list(
            part="snippet",
            videoId="WNrB1Q9Rry0",
            maxResults=100
          )
        response = request.execute()
        for item in response['items']:
            st.write(item['snippet']['topLevelComment']['snippet']['textDisplay'])

            print(item['snippet']['topLevelComment']['snippet']['textDisplay'])

    else:
        yt_api_key = st.text_input('Enter Youtube API Key:', type='password')
        if not (yt_api_key.startswith('AI')):
            st.warning('Please enter your API Key!', icon='⚠️')
        else:
            st.success('Success!', icon='✅')
           
            api_service_name = "youtube"
            api_version = "v3"
            DEVELOPER_KEY=yt_api_key
              
            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey=DEVELOPER_KEY)
              
            request = youtube.commentThreads().list(
                part="snippet",
                videoId="WNrB1Q9Rry0",
                maxResults=100
              )
            response = request.execute()
            yttext = ''
            for item in response['items']:
                yttext = yttext + item['snippet']['topLevelComment']['snippet']['textDisplay']             
                print(item['snippet']['topLevelComment']['snippet']['textDisplay'])
            st.text_area('{yttext}')
            st.write('{yttext}')

          





# Set the title and caption for the Streamlit app
st.title("🤖 Google Gemini Comments")
st.caption("🚀 A streamlit app powered by Google Gemini")

# Create tabs for the Streamlit app
tab1, tab2 = st.tabs(["🌏 Generate Funny Comment - Gemini Pro", "  "])

# Code for Gemini Pro model
with tab1:
    st.write("💬 Using Gemini Pro - Text only model")
    st.subheader("🌏 Generate funniest comment")
    

    prompt = f"""Come up with a funny comment 
       """ 
    
    config = {
        "temperature": 0.8,
        "max_output_tokens": 2048,
        }
    
    generate_t2t = st.button("Generate funny comment", key="generate_t2t")
    model = genai.GenerativeModel("gemini-pro", generation_config=config)
    if generate_t2t and prompt:
        with st.spinner("Generating your funny comment using Gemini..."):
            plan_tab, prompt_tab = st.tabs(["Funny Comment", "Prompt"])
            with plan_tab: 
                response = model.generate_content(prompt)
                if response:
                    st.write("Your comment:")
                    st.write(response.text)
            with prompt_tab: 
                st.text(prompt)

