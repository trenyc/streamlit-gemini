# Function to categorize comments
def categorize_comments():
    prompt = create_prompt(st.session_state.comments)
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
                if debug_mode:
                    st.write("Response from OpenAI API:")
                    st.code(response_text)
                # Strip introductory line and ignore example comment
                response_lines = response_text.split('\n')
                if response_lines[0].count(':') > 0:
                    response_lines = response_lines[1:]
                
                # Ensure top_voted_comments are not None
                valid_top_voted_comments = [st.session_state.top_voted_comments[cat] for cat in categories if st.session_state.top_voted_comments[cat] is not None]
                if debug_mode:
                    st.write("Valid top voted comments:")
                    st.write(valid_top_voted_comments)
                
                response_lines = [line for line in response_lines if all(tv_comment not in line for tv_comment in valid_top_voted_comments)]
                
                for line in response_lines:
                    if ':' in line:
                        continue
                    for category in categories:
                        if category in line and line.strip() not in [c['text'] for c in st.session_state.categorized_comments[category]]:
                            st.session_state.categorized_comments[category].append({"id": line.strip(), "text": line.strip()})
                            break
                if debug_mode:
                    st.write("Categorized comments:")
                    st.write(st.session_state.categorized_comments)
            else:
                st.error("No response from the model.")
    except APIError as e:
        st.error(f"An API error occurred: {e}")
        st.error(f"Error code: {e.status_code} - {e.message}")
        st.error(f"Full response: {e.response}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# Function to display categorized comments and voting buttons
def display_categorized_comments():
    if isinstance(st.session_state.categorized_comments, dict):
        for current_category in st.session_state.categorized_comments.keys():  # Use current_category
            if len(st.session_state.categorized_comments[current_category]) > 0:  # Check if the list is not empty
                st.write(f"### {current_category.capitalize()}")
                st.write(f"Vote for the comments that are {current_category}.")
                for idx, comment in enumerate(st.session_state.categorized_comments[current_category][:5]):
                    if comment['text'].strip():  # Ensure no blank comments are displayed
                        st.write(comment['text'])
                        votes = fetch_votes(video_id, comment['id'], current_category)  # Use current_category
                        if st.button(f"👍 ({votes['up']})", key=f"{current_category}_up_{comment['id']}_{idx}"):  # Ensure unique key
                            update_votes(video_id, comment['id'], current_category, "up")  # Use current_category
                            # Force a rerun to update vote count
                            st.experimental_rerun()
            else:
                st.write(f"No comments found for {current_category}.")

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
if 'categorized_comments' in st.session_state and any(st.session_state.categorized_comments.values()):
    st.subheader("Vote on Comments")
    display_categorized_comments()

# Display vote summary
if 'votes' in st.session_state:
    display_vote_summary()

# Load more comments button
if st.session_state.next_page_token:
    if st.button("Load More Comments"):
        fetch_and_categorize_comments()
