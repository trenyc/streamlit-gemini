import os
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openai import OpenAI, APIError

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
    
    if yt_api_key and openai_api_key:
        st.success('API keys provided!', icon='✅')
    else:
        st.warning('Please enter both API keys!', icon='⚠️')

# Set up the default comments for the default view
default_comments = [
    "a billion dollars idea for Apple: give iPad the 'MacPad' OS",
    "I'm still using my iPad Pro 3rd gen with the a12x Bionic chip I bought new like 6 or 7 years ago. I'm still getting all the updates and it runs just as well as the day I got it with zero lag or stuttering doing anything. Hoping I can get another 5 years out of it.",
    "Apple is the brand ambassador of innovation for the sake of innovation.",
    "Don’t say ‘5.3mm thin’ and accept Apples marketing corruption of language. It’s ‘5.3mm THICK!’",
    "Watching on my iPad Pro 13 inch. This screen is heat",
    "To me, the big thing is that it seems they managed to make those ipads vastly more energy efficient. So the point of the M4 is exactly that, like Marques indicated in between. I think this is a big thing but none that would or should trigger a buy of course. In the PC world things go in the wildly wrong direction with every generation of graphics card being vastly more wasteful than the previous one. It is great to see that at least in some mobile application we see that it doesn't have to be that way.",
    "Yes I know, the performance of an 4090 isn't possible today without drowning it in electricity but the thing is that this peak performance is pushed way beyond diminishing returns.",
    "sony xperia 1 mark vi IMMA BOOO HARD CAUSE APPLE SUX and then Secreatly want one Cause .. Apple aka iproducts seems to have reached its peak!",
    "I feel like over the last 5 years the tech industry has started regressing and profit hunting.",
    "I think they’re trying to get people to buy iPads over Macs for some reason",
    "The day FileMaker comes out with a fully functioning version of FileMaker Pro that will run on an iPad, I'll be more than happy to ditch my laptop and get an OLED iPad. Unfortunately, that day will probably never come.",
    "Hey man it’s been too long, I need another MKBHD video",
    "Hey. I have just gotten the iPad pro 11 inch m4 and Got the magic keyboard as Well. Then i decided to get the Logitech Mx master 3s mouse. But the mouse scroll on the mouse isnt smooth and runs like shit. Maybe you could make a video about this problem. I Think its bad They only have smooth scrolling for there own deviceses.",
    "It’s cool how only your YouTube videos allow me to play background without a subscription",
    "We do need a full review!! When is it coming?",
    "Galaxy tab snorts ipad easly",
    "Watching this video on my iPad rn",
    "We are so spoiled by Apple. How do we deserve any of those incredible devices? And for just a few lousy bucks… Amazing. Awesome. Beyond awesome. Does any normal mortal even understand the technology? And the manufacturing wizardy behind it? Eight trillion operations per second. It’s a wonder that a device like that doesn’t cost a million dollars… Well…",
    "Having worked for Apple…. WWDC is just around the corner.  Will we see a major update to iPadOS?  I hope so…need to harness all that new grunt somehow",
    "I love the EU regulations against Apple. They are tackling this right now and make it illegal for OS (Especially iPadOS in this case) to throttle down a otherwise powerful product.",
    "indeed awkward.",
    "When the M-series gonna end? i think all the same lmao, well the difference between 1st generation and the lastes might be noticeable... but not that much",
    "Thanks! \"even if you feel like you could snap it in half the whole time\" XD",
    "I bet Apple is going to announce soon the introduction of macos apps in iPads just as the iphone and ipads apps in macos",
    "<a href=\"https://www.youtube.com/watch?v=-T0MGehwWvE&amp;t=167\">2:47</a> was hilarious 😂",
    "Adam test apple. why mkbhd is the only YouTuber to have PIP available?",
    "🤣 Why are your hands yellow",
    "800 for the iPad Air? the regular 15 is 840",
    "My heart skipped a beat I thought he was boutta say starts out at 128 dollars he said gigs ...128 gigs",
    "I want to start digital drawing and I’ve always wanted to buy and iPad so with the release of the new pro and air I think i finally buy the last gen air",
    "They did add Final Cut Pro to the iPads though, right?",
    "As an artist who just bought an m2 ipad, being locked out of the Apple Pencil Pro is a huge bummer. Beyond disappointed.",
    "Make it more powerful than a MacBook and give it macOS than we’ll start talkin",
    "Hey dude, see anything new from Top Gear, lately?  Oh wait, I’ll pay you a buck to read it.  Send me a routine number.",
    "Is the new iPad actually sneaky way better than we thought?",
    "What’s taking so long with the review? Is there gonna be one? Still making my purchasing decision here… but nearly decided.",
    "The new air is always fresher than the old air. But it doesn't matter... its just an air.",
    "Never heard anyone complaining so much about getting more power and new features. If you don‘t need don‘t buy it. For those users the iPad Air is made and powerful enough.",
    "They’re playing their customers at this point. Where’s the innovation? What’s new or special? I used to look forward to Apple events but now they’re underwhelming.",
    "Ipad pro m1 not detecting usb drive after ios 17 update. Useless piece of junk.",
    "hello hello I don't want thinner. Lighter is fine though (there's a reason I prefer the iPad mini). They need to bring Xcode so I can develop software on it; only then could I ever use it in a professional capacity.",
    "Kindly help me understand certain thing about apple pencil pro, There’s no difference between iPad Pro 4th Gen and iPad Air 2024 , M2 chip is same cpu and gpu cores and all, even iPad pro 4th gen is better than iPad Air 2024 and have same display but iPad pro 4th Gen can’t support Apple pencil pro . LOL Some regulations need to be there regarding is seller market and their control over customer rights",
    "This iPad release was so boring. Maybe Apple has already developed macOS for the iPad and is waiting to release it if the sales of the M4 iPad are poor.",
    "It's ironic that we used to support companies we preferred by buying their products, but now we need to make them better by refusing to buy their subpar products.",
    "so every time apple make their devices thinner and sell it like they are doing you a favor, what they are actually doing is removing battery?",
    "It finally happened! Apple silenced Marques 😂",
    "Where's your iPad Pro review? Been waiting and looking for it for days!",
    "Apple hater keep it going",
    "is the 10th Generation Ipad now the best value? how many ppl really need to have the ipad pencil. What should I get for note taking/multiple tab chrome browsing/ excel? Have a good desktop so doesn’t need to be super powerful",
    "Wish I had been rich to buy an iPad Pro… I have always wanted a big one for procreate and a lot of storage to download stuff…I have a Samsung tab but the iPad seems different when it comes to tablets :/ I think ill just wait for the s10",
    "While I didn't ask for a thinner ipad pro;  I love that its lighter to put in my purse. I can't wait to buy one. All The Best ✨",
    "Who is the manufacturer of the display? I haven't had a new ipad since the original Mini came out, it's insane how far ipads have come in all these years.  I've just never really had any use for one.  For me personally, ipad improvements are just a preview of what might be possible for the next iphone.  Will be really interesting to see if they try to make those thinner like these ipads, if they will be able to make them strong enough to not bend",
    "They didn’t move the pencil to the other side because then they couldn’t sell you the same accessory you already own again. <a href=\"https://www.youtube.com/watch?v=-T0MGehwWvE&amp;t=22\">0:22</a>",
    "I could not disagree more. Having a more powerful processor for apps like Clip Studio Paint is a major benefit for me - more RAM and better graphics performance goes a long long way.",
    "How is it with DaVinci Resolve for iPad Pro compared to the6th gen iPad Pro for example?  Worth. Upgrading?",
    "It is not thinner than my MagSafe charger.",
    "Apple should take a break for a year or two. Refresh their minds and then come back with something better.",
    "It's ok, we are all cavemen at heart. Mediocre tech is not the end of the world.",
    "why havent you posted a review yet??",
    "Apple seems to be out of touch… no one wanted a thinner and weaker iPad.",
    "Yikes. They really do need to work on the OS more than anything, and get rid of the camera bump, please? So annoying when on a table.",
    "Not impressed. Same BS from apple. Who other than children still use tablets too? Apple is in serious trouble. They're out of ideas.",
    "ASUS? I am currently pissed that the new Apple Pencil pro can only be used on these guys 🙄 I have the air 4 and as an artist I am trying my best to make the switch and get use to digital art (which is why I got the air 4 in the first place and not the pro,, until I start making $ on my art then I will do the upgrade). Not being able to use the new pencil that has awesome features for procreate really sucks🙄",
    "The thinness of these iPad Pros is a huge negative for me",
    "I had the 2020 11 inch iPad Pro, with magic keyboard and everything... I switched to the iPad mini. The new Pros and Airs are amazing but as you said, its still just an iPad...",
    "Just a quick one i can't hide my joy I am Jackson from Minnesota I have had bad breath for 12 years I had regular doctor visit to check my stomach acid but the rotten egg smell just keep getting worst, My 4 year old son told me my breath stink that day I started to swallow mouthwash just to help the situation but it made it even worse until my aunty gave me a link to Thrive Thirst B.V. a cousin of mine have used their product for his own bad breath he is an older man after three days of using this product I got normal just so normal I can't believe this if anyone in the Minnesota area wants to try the rest of what's left of the one I bought please let me know.",
    "All this for Netflix and uni notes",
    "i was looing for a new phone with great video. which only apple and s24 gives but if this can do that and be a compact video editor+drawing tablet+screen where i can read music lyrics. its a fucking steal",
    "“What could possibly go wrong?”",
    "Pls help me so I currently have the iPad Pro m1 11 inch So I’m planning on upgrading to a bigger model should I go for the iPad Air 12.9, iPad Pro m2 12.9 or iPad Pro m4 11 inch I’m mainly using it to take notes as a medical student",
    "Pista de audio",
    "I am curious why didnt you release an actual review of iPad Pro 2024 (M4) video yet. Is it not as important for you, given that \"its just an ipad\"?",
    "Still can’t use it as a monitor for a Mac mini without paying for an app… smh",
    "Still just ipadOs",
    "“Still ungodly expensive” lol",
    "11 or 13?",
    "When you realize they changed all the sizes from 12.9 inch to 13 inch or 10.9 to 11inch to \"be more clean\" when in reality you old magic keyboards are now obsolete and you need to buy some more❤",
    "Dude thank you for saying what needs to be said. We don't need a spec bump, we need a huge redisgn to Ipad OS. The day they will able a jailbreak mode or an os that is more open for specific users (us ) and an npc like iPad os to,use for everyone; they did it for a an more easy to use os for older people etc .",
    "iPad Pro is one update away to be one of the best apple products imo :)",
    "Doesn't matter how thin you make a device - and this applies to the Chinese / Korean / Taiwanese brands too - if you have that camera bump on the back. Means you can never put the damn thing flat on a desk and type without it rocking on the stupid thing. Super annoying. Plus of course only most of the device is 5.1 mm thin, but a part of it is still 7 mm thick so where's the real advantage?",
    "Why not 60 fps?",
    "The world is moving towards software enhancement with AI while Apple is still obsessed with hardware.",
    "I can live with the older Ipad body, just upgrade the os duh!",
    "I would dig an Ipad with macOS, or a Macbook Air with touch functionality (is that a hardware change or software? Ok whatever)",
    "Should we expect a full review video?",
    "Maybe it’s catering to people who only have an iPad but no laptop (they do exist)",
    "After seeing the internals of my old gen 4. It was clear apple could make a far far thinner iPad back then. But why make one that thin when they can slowly reduce their thickness over many generations. At <a href=\"https://www.youtube.com/watch?v=-T0MGehwWvE&amp;t=615\">10:15</a> u can see the ipad being bent lol",
    "I'M HERE BECAUSE OF YAHIMICE",
    "iPad Pro m4(11 and 13 )is the only way to enjoy watching content on OLED displays in entire Apple ecosystem.. M4 is just an overkill for an iPad with its limitations.. if they put oleds in basic iPads.. no one would buy a pro.. I have bought one for oled panel",
    "With the iPads Apple miss so much potential. We need real iPad software not better hardware…",
    "It’s ridiculous and impressive to even see the price of 11 inch iPad Pro more expensive than a MacBook Air😂",
    "if you are legitimate artist, creating multiple layers and doing real design like my staff is doing...the power is welcomed, the nano texture is welcomed (we normally add a matte screen protector)...but that 2G price...we might have to wait for M5. But we are jealous. It's just an amazing piece of machinery."
]

if yt_api_key and openai_api_key:
    # Configure the OpenAI API with the API key
    client = OpenAI(api_key=openai_api_key)
    st.write(f"Using OpenAI API Key: ...{openai_api_key[-4:]}")

    # Main app content
    st.title("🎉 Comment Buckets")
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
    else:
        st.write("💬 Default YouTube Comments")
        for comment in default_comments:
            st.write(comment)

    # Categorize and display comments using OpenAI
    if 'comments' in st.session_state and st.session_state.comments:
        comment_categories = st.multiselect(
            'Select categories for comments:',
            ['funny', 'interesting', 'positive', 'negative', 'serious'],
            default=['funny', 'interesting', 'positive', 'negative', 'serious']
        )
        prompt = f"Categorize the following comments into categories: {', '.join(comment_categories)}. Comments: {' '.join(st.session_state.comments)}"

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
    st.title("🎉 Comment Buckets")
    st.caption("🚀 Unleash the fun in YouTube comments with OpenAI")
    st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f31f.png", width=64)
    st.write("💬 Default YouTube Comments")
    for comment in default_comments:
        st.write(comment)

    comment_categories = st.multiselect(
        'Select categories for comments:',
        ['funny', 'interesting', 'positive', 'negative', 'serious'],
        default=['funny', 'interesting', 'positive', 'negative', 'serious']
    )

    if st.button("Categorize Default Comments"):
        st.write("Starting to categorize comments...")
        prompt = f"Categorize the following comments into categories: {', '.join(comment_categories)}. Comments: {' '.join(default_comments)}"
        st.write("Prompt being sent to OpenAI API:")
        st.code(prompt)
        st.write("Using OpenAI API Key: ...XYra")
        st.write("Sending request to OpenAI API...")
        try:
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
