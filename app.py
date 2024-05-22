 import os
import streamlit as st
from openai import OpenAI, APIError

# Set the page configuration for the Streamlit app
st.set_page_config(
    page_title="OpenAI Test App",
    page_icon="🧠",
    layout="wide"
)

# Sidebar for API key input
with st.sidebar:
    st.title("🔑 OpenAI API Key")
    openai_api_key = st.text_input('Enter OpenAI API Key:', type='password')
    if openai_api_key:
        st.success('API key provided!', icon='✅')
    else:
        st.warning('Please enter the OpenAI API key!', icon='⚠️')

if openai_api_key:
    # Configure the OpenAI API with the API key
    client = OpenAI(api_key=openai_api_key)
    st.write(f"Using OpenAI API Key: ...{openai_api_key[-4:]}")

    # Main app content
    st.title("🧠 OpenAI Test App")
    st.caption("🚀 Testing OpenAI API call from Streamlit")

    # Input field for prompt
    user_prompt = st.text_input("💬 Enter a prompt for OpenAI:")

    if st.button("Send Prompt"):
        st.write("Sending prompt to OpenAI API...")
        st.write("Prompt being sent to OpenAI API:")
        st.code(user_prompt)
        st.write(f"Using OpenAI API Key: ...{openai_api_key[-4:]}")
        with st.spinner("Waiting for OpenAI response..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_prompt},
                    ]
                )
                st.write("Processing response from OpenAI API...")
                if response.choices:
                    response_text = response.choices[0].message['content'].strip()
                    st.subheader("Response from OpenAI (gpt-3.5-turbo)")
                    st.write(response_text)
                    st.success("OpenAI API call was successful!")
                else:
                    st.error("No response from the gpt-3.5-turbo model.")
            except APIError as e:
                st.error(f"An API error occurred: {e}")
                st.error(f"Error code: {e.code} - {e.message}")
                st.error(f"Full response: {e.response}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
else:
    st.warning("Please enter the required OpenAI API key to use the application.")
