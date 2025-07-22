import streamlit as st
import re
import pandas as pd
import emoji
import urllib.parse as urlparse
import matplotlib.pyplot as plt
import seaborn as sns
from googleapiclient.discovery import build

# Custom CSS for ultra-futuristic style with animated title
st.markdown("""
    <style>
    /* Main body styling - Cyberpunk theme */
    .stApp {
        background: radial-gradient(circle at center, #0a0e17 0%, #000000 100%);
        color: #e0f7ff;
        font-family: 'Rajdhani', 'Orbitron', sans-serif;
    }
    
    /* Animated Title styling - Pink with glowing and dimming effect */
    .animated-title {
        color: #ff69b4; /* Hot pink */
        text-shadow: 0 0 10px #ff69b4, 0 0 20px #ff1493, 0 0 30px #c71585;
        font-size: 3.5em;
        text-align: center;
        letter-spacing: 2px;
        margin-bottom: 0.5em;
        font-weight: 700;
        animation: glow 2s ease-in-out infinite;
    }
    
    @keyframes glow {
        0% { text-shadow: 0 0 5px #ff69b4, 0 0 10px #ff1493, 0 0 15px #c71585; }
        50% { text-shadow: 0 0 15px #ff69b4, 0 0 25px #ff1493, 0 0 35px #c71585; }
        100% { text-shadow: 0 0 5px #ff69b4, 0 0 10px #ff1493, 0 0 15px #c71585; }
    }
    
    /* Section headers */
    h2, h3 {
        color: #00f2ff;
        text-shadow: 0 0 5px #00f2ff;
        border-bottom: 1px solid #0084ff;
        padding-bottom: 0.3em;
    }
    
    /* Input fields - HUD style */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: rgba(10, 14, 23, 0.8) !important;
        color: #00f2ff !important;
        border: 1px solid #0084ff !important;
        border-radius: 5px !important;
        padding: 12px !important;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.3) !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    .stTextInput > label, .stNumberInput > label {
        color: #00f2ff !important;
        font-weight: 500 !important;
        text-shadow: 0 0 3px #00f2ff;
    }
    
    /* Buttons - Cyberpunk style */
    .stButton > button {
        background: linear-gradient(135deg, #00f2ff 0%, #0084ff 100%) !important;
        color: #0a0e17 !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 12px 24px !important;
        font-size: 1.1em !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.5) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 25px rgba(0, 242, 255, 0.8) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Alerts and info boxes */
    .stAlert {
        background-color: rgba(10, 14, 23, 0.8) !important;
        border-left: 4px solid #0084ff !important;
        border-radius: 0 5px 5px 0 !important;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.3) !important;
    }
    
    /* Spinner - Cyber style */
    .stSpinner > div {
        border-color: #00f2ff transparent #00f2ff transparent !important;
    }
    
    /* Text output */
    .stMarkdown, .stWrite {
        color: #e0f7ff !important;
        font-size: 1.1em !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: rgba(10, 14, 23, 0.8) !important;
        border: 1px solid #0084ff !important;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.3) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(10, 14, 23, 0.8) !important;
        color: #e0f7ff !important;
        border: 1px solid #0084ff !important;
        border-radius: 5px 5px 0 0 !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00f2ff 0%, #0084ff 100%) !important;
        color: #0a0e17 !important;
        font-weight: 700 !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0e17;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #0084ff;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #00f2ff;
    }
    
    /* Terminal-like output */
    .terminal {
        background-color: rgba(10, 14, 23, 0.9);
        border: 1px solid #0084ff;
        border-radius: 5px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        color: #00f2ff;
        box-shadow: inset 0 0 10px rgba(0, 242, 255, 0.2);
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Load futuristic fonts from Google Fonts
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;500;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ----- Platform Detection -----
def extract_platform(link):
    link = link.lower()
    if "youtube.com" in link or "youtu.be" in link:
        return "youtube"
    else:
        return None

# ----- YouTube Comments Scraper -----
def get_youtube_comments(link, max_results, api_key):
    if not api_key:
        return []
    
    try:
        parsed_url = urlparse.urlparse(link)

        if "youtu.be" in link:
            video_id = parsed_url.path.lstrip("/")
        elif "youtube.com" in link:
            query_params = urlparse.parse_qs(parsed_url.query)
            video_id = query_params.get("v", [None])[0]
        else:
            return []

        if not video_id:
            return []

        youtube = build('youtube', 'v3', developerKey=api_key)
        comments = []

        request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=100, textFormat="plainText")

        while request and len(comments) < max_results:
            response = request.execute()
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)
                if len(comments) >= max_results:
                    break
            request = youtube.commentThreads().list_next(request, response)

        return comments
    
    except Exception as e:
        # Return empty list with error info for the main function to handle
        return []

# ----- Text Cleaning -----
def clean_text(text):
    if not text:
        return ""
    text = emoji.demojize(text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^A-Za-z0-9\s:_]+', '', text)
    return text.lower().strip()

# ----- Save Data to CSV -----
def save_to_csv(data, filename="comments_data.csv"):
    df = pd.DataFrame(data, columns=["Platform", "Text"])
    df.to_csv(filename, index=False)

# ----- Sentiment Analysis -----
def classify_sentiment(comment, positive_keywords_set, negative_keywords_set):
    if not isinstance(comment, str):
        return 'neutral'
    comment_lower = comment.lower()
    words = re.findall(r'\b[\w-]+\b', comment_lower)
    positive_count = sum(1 for word in words if word in positive_keywords_set)
    negative_count = sum(1 for word in words if word in negative_keywords_set)
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'

# ----- Streamlit App -----
def main():
    # Main header with animated glowing title
    st.markdown("""
    <div style="text-align: center;">
        <h1 class="animated-title">SENTIMENT ANALYTICS</h1>
        <p style="color: #00f2ff; font-size: 1.2em; text-shadow: 0 0 5px #00f2ff;">
            REAL-TIME YOUTUBE COMMENT SENTIMENT ANALYZER
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Input section with futuristic styling
    with st.container():
        st.markdown("### INPUT PARAMETERS")
        
        # API Key input section
        st.markdown("#### 🔑 API CONFIGURATION")
        api_key = st.text_input(
            "YOUTUBE API KEY:", 
            type="password",
            placeholder="Enter your YouTube Data API v3 key...",
            help="Get your free API key from Google Cloud Console"
        )
        
        if st.button("ℹ️ How to get YouTube API Key", key="api_help"):
            st.info("""
            **Steps to get YouTube Data API v3 Key:**
            1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
            2. Create a new project or select existing one
            3. Enable "YouTube Data API v3"
            4. Go to "Credentials" and create "API Key"
            5. Copy the API key and paste it above
            """)
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            link = st.text_input("ENTER YOUTUBE URL:", placeholder="https://youtube.com/watch?v=... or https://youtu.be/...")
        with col2:
            max_comments = st.number_input("MAX COMMENTS:", min_value=1, max_value=5000, value=100)
    
    if st.button("⚡ INITIATE ANALYSIS", key="analyze"):
        if not link:
            st.error("⚠️ NO INPUT DETECTED. PLEASE PROVIDE A VALID YOUTUBE URL.")
            return

        platform = extract_platform(link)
        if not platform:
            st.error("⚠️ INVALID URL FORMAT. PLEASE PROVIDE A VALID YOUTUBE URL.")
            return
        
        # Validate API key for YouTube
        if not api_key:
            st.error("⚠️ YOUTUBE API KEY REQUIRED. PLEASE ENTER YOUR API KEY TO ANALYZE YOUTUBE COMMENTS.")
            return

        with st.status("🛠️ CONNECTING TO YOUTUBE...", expanded=True) as status:
            st.write("🔍 VALIDATING YOUTUBE URL...")
            st.success(f"✅ YOUTUBE URL VALIDATED")
            
            st.write("📡 FETCHING COMMENTS...")
            comments = get_youtube_comments(link, max_results=max_comments, api_key=api_key)
            if not comments:
                status.update(label="⚠️ YOUTUBE API ERROR", state="error", expanded=False)
                st.error("❌ FAILED TO FETCH YOUTUBE COMMENTS. PLEASE CHECK:\n- Your API key is valid\n- The video exists and has comments enabled\n- You haven't exceeded API quotas")
                return
            
            if comments:
                st.write("🧹 CLEANING DATA STREAM...")
                data = [("youtube", clean_text(comment)) for comment in comments]
                save_to_csv(data)
                status.update(label="✅ ANALYSIS COMPLETE", state="complete", expanded=False)
                st.balloons()
            else:
                status.update(label="⚠️ NO DATA RECEIVED", state="error", expanded=False)
                return

        # Load keywords
        try:
            positive_keywords = pd.read_csv('positive_keywords.csv', header=None)[0].tolist()
            negative_keywords = pd.read_csv('negative_keywords.csv', header=None)[0].tolist()
        except FileNotFoundError:
            st.error("CRITICAL ERROR: KEYWORD DATABASES NOT FOUND. PLEASE ENSURE 'positive_keywords.csv' AND 'negative_keywords.csv' ARE IN THE WORKING DIRECTORY.")
            return

        positive_keywords_set = set(keyword.lower() for keyword in positive_keywords)
        negative_keywords_set = set(keyword.lower() for keyword in negative_keywords)

        # Load comments data
        comments_df = pd.read_csv('comments_data.csv')
        comments_df['sentiment'] = comments_df['Text'].apply(
            lambda x: classify_sentiment(x, positive_keywords_set, negative_keywords_set)
        )

        # Sentiment counts
        sentiment_counts = comments_df['sentiment'].value_counts()
        positive_count = sentiment_counts.get('positive', 0)
        negative_count = sentiment_counts.get('negative', 0)
        neutral_count = sentiment_counts.get('neutral', 0)

        overall_sentiment = 'positive' if positive_count >= negative_count else 'negative'
        
        # Display results in futuristic terminal style
        st.markdown("### 📊 SENTIMENT ANALYSIS RESULTS")
        with st.container():
            st.markdown("""
            <div class="terminal">
                <p>> SYSTEM STATUS: ANALYSIS COMPLETE</p>
                <p>> DATA POINTS PROCESSED: {}</p>
                <p>> POSITIVE SIGNALS: <span style="color: #00ff88;">{}</span></p>
                <p>> NEGATIVE SIGNALS: <span style="color: #ff0066;">{}</span></p>
                <p>> NEUTRAL SIGNALS: {}</p>
                <p>> DOMINANT VIBE: <span style="color: {}; text-shadow: 0 0 5px {};">{}</span></p>
            </div>
            """.format(
                len(comments_df),
                positive_count,
                negative_count,
                neutral_count,
                '#00ff88' if overall_sentiment == 'positive' else '#ff0066',
                '#00ff88' if overall_sentiment == 'positive' else '#ff0066',
                overall_sentiment.upper()
            ), unsafe_allow_html=True)

        # Visualizations with futuristic styling
        st.markdown("### 📈 SENTIMENT VISUALIZATION")
        
        tab1, tab2 = st.tabs(["POLARITY MATRIX", "SIGNAL STRENGTH"])
        
        with tab1:
            # Pie Chart (only Positive and Negative)
            fig1, ax1 = plt.subplots(facecolor='none', figsize=(8, 8))
            ax1.pie(
                [positive_count, negative_count],
                labels=['POSITIVE', 'NEGATIVE'],
                autopct='%1.1f%%',
                colors=['#00ff88', '#ff0066'],
                startangle=90,
                wedgeprops={'edgecolor': '#0a0e17', 'linewidth': 2},
                textprops={'color': '#e0f7ff', 'fontsize': 12, 'fontweight': 'bold'},
                explode=(0.05, 0.05),
                shadow=True
            )
            ax1.set_title("POLARITY MATRIX", color='#00f2ff', pad=20, fontsize=14, fontweight='bold')
            plt.gca().set_facecolor('none')
            st.pyplot(fig1)
        
        with tab2:
            # Bar Chart
            fig2, ax2 = plt.subplots(facecolor='none', figsize=(10, 6))
            bars = sns.barplot(
                x=['POSITIVE', 'NEGATIVE'], 
                y=[positive_count, negative_count], 
                ax=ax2, 
                palette=['#00ff88', '#ff0066'],
                edgecolor=['#00f2ff', '#ff00ff'],
                linewidth=2
            )
            
            # Add value labels on top of bars
            for p in bars.patches:
                height = p.get_height()
                ax2.text(p.get_x() + p.get_width()/2., height + 0.5,
                         f'{int(height)}',
                         ha="center", color='#e0f7ff', fontsize=12, fontweight='bold')
            
            ax2.set_xlabel("SENTIMENT", color='#00f2ff', fontsize=12, fontweight='bold')
            ax2.set_ylabel("COUNT", color='#00f2ff', fontsize=12, fontweight='bold')
            ax2.set_title("SIGNAL STRENGTH ANALYSIS", color='#00f2ff', pad=20, fontsize=14, fontweight='bold')
            ax2.grid(axis='y', linestyle='--', alpha=0.3, color='#0084ff')
            ax2.set_facecolor('none')
            ax2.tick_params(colors='#e0f7ff')
            
            # Add glow effect to bars
            for bar in bars.patches:
                bar.set_edgecolor('#00f2ff')
                bar.set_linestyle('-')
                bar.set_linewidth(1)
                bar.set_alpha(0.9)
            
            st.pyplot(fig2)
        
        # Raw data display
        st.markdown("### 📁 RAW DATA PREVIEW")
        st.dataframe(comments_df.head(10).style
                    .applymap(lambda x: 'color: #00ff88' if x == 'positive' else ('color: #ff0066' if x == 'negative' else 'color: #e0f7ff'), subset=['sentiment'])
                    .set_properties(**{'background-color': 'rgba(10, 14, 23, 0.8)', 'color': '#e0f7ff', 'border': '1px solid #0084ff'}))

if __name__ == "__main__":
    main()
