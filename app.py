import streamlit as st
import re
import pandas as pd
import emoji
import urllib.parse as urlparse
import matplotlib.pyplot as plt
import seaborn as sns
from googleapiclient.discovery import build

# Configure page for wide layout optimized for PC viewing
st.set_page_config(
    page_title="CommentAnalyzer - AI-Powered Sentiment Analysis",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for ultra-futuristic style optimized for PC screens
st.markdown("""
    <style>
    /* Main body styling - Cyberpunk theme optimized for PC */
    .stApp {
        background: radial-gradient(circle at center, #0a0e17 0%, #000000 100%);
        color: #e0f7ff;
        font-family: 'Rajdhani', 'Orbitron', sans-serif;
        max-width: 100% !important;
        padding: 0 2rem !important;
    }
    
    /* Main content container - Full width for PC */
    .main .block-container {
        max-width: 100% !important;
        padding-top: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Animated Title styling - Left aligned for PC */
    .animated-title {
        color: #ff69b4; /* Hot pink */
        text-shadow: 0 0 10px #ff69b4, 0 0 20px #ff1493, 0 0 30px #c71585;
        font-size: 3.5em;
        text-align: left !important;
        letter-spacing: 2px;
        margin-bottom: 0.5em;
        font-weight: 700;
        animation: glow 2s ease-in-out infinite;
        padding-left: 0 !important;
    }
    
    @keyframes glow {
        0% { text-shadow: 0 0 5px #ff69b4, 0 0 10px #ff1493, 0 0 15px #c71585; }
        50% { text-shadow: 0 0 15px #ff69b4, 0 0 25px #ff1493, 0 0 35px #c71585; }
        100% { text-shadow: 0 0 5px #ff69b4, 0 0 10px #ff1493, 0 0 15px #c71585; }
    }
    
    /* Section headers - Left aligned */
    h2, h3 {
        color: #00f2ff;
        text-shadow: 0 0 5px #00f2ff;
        border-bottom: 1px solid #0084ff;
        padding-bottom: 0.3em;
        text-align: left !important;
        margin-left: 0 !important;
    }
    
    /* Full width containers */
    .stContainer > div {
        width: 100% !important;
        max-width: 100% !important;
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
    
    /* PC Optimization - Metrics and cards */
    .stMetric {
        background-color: rgba(10, 14, 23, 0.8) !important;
        border: 1px solid #0084ff !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.3) !important;
    }
    
    .stMetric > div {
        color: #00f2ff !important;
    }
    
    /* Column spacing for PC */
    .stColumn {
        padding: 0 0.5rem !important;
    }
    
    /* Chart containers */
    .stPlotlyChart, .stPyplot {
        background-color: rgba(10, 14, 23, 0.5) !important;
        border-radius: 8px !important;
        border: 1px solid #0084ff !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.2) !important;
        padding: 1rem !important;
    }
    
    /* Dataframe optimization for PC */
    .stDataFrame {
        background-color: rgba(10, 14, 23, 0.8) !important;
        border: 1px solid #0084ff !important;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Remove center alignment from elements */
    .element-container {
        text-align: left !important;
    }
    
    /* Mobile Optimization - Responsive Design */
    @media (max-width: 768px) {
        /* Mobile: Stack elements vertically */
        .stApp {
            padding: 0 1rem !important;
        }
        
        .main .block-container {
            padding-top: 1rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        
        /* Mobile: Smaller title */
        .animated-title {
            font-size: 2.5em !important;
            text-align: center !important;
            line-height: 1.2 !important;
        }
        
        /* Mobile: Center align headers */
        h2, h3 {
            text-align: center !important;
            font-size: 1.2em !important;
        }
        
        h4 {
            text-align: center !important;
            font-size: 1em !important;
            color: #00f2ff !important;
        }
        
        /* Mobile: Stack columns vertically */
        .stColumn {
            padding: 0.5rem 0 !important;
            width: 100% !important;
        }
        
        /* Mobile: Smaller input fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            padding: 8px !important;
            font-size: 14px !important;
        }
        
        /* Mobile: Smaller buttons */
        .stButton > button {
            padding: 10px 16px !important;
            font-size: 1em !important;
            width: 100% !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Mobile: Compact metrics */
        .stMetric {
            padding: 0.5rem !important;
            margin: 0.25rem 0 !important;
        }
        
        .stMetric [data-testid="metric-container"] {
            text-align: center !important;
        }
        
        /* Mobile: Chart adjustments */
        .stPlotlyChart, .stPyplot {
            padding: 0.5rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Mobile: Terminal display */
        .terminal {
            padding: 10px !important;
            font-size: 0.9em !important;
            margin: 5px 0 !important;
        }
        
        /* Mobile: Dataframe adjustments */
        .stDataFrame {
            font-size: 0.8em !important;
        }
        
        /* Mobile: Tab adjustments */
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px !important;
            font-size: 0.9em !important;
        }
    }
    
    /* Tablet Optimization */
    @media (min-width: 769px) and (max-width: 1024px) {
        .stApp {
            padding: 0 1.5rem !important;
        }
        
        .animated-title {
            font-size: 3em !important;
        }
        
        .stColumn {
            padding: 0 0.25rem !important;
        }
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
    # Detect mobile view based on screen width
    st.markdown("""
    <script>
    function checkMobile() {
        return window.innerWidth <= 768;
    }
    </script>
    """, unsafe_allow_html=True)
    
    # Initialize mobile view detection
    if 'mobile_view' not in st.session_state:
        st.session_state.mobile_view = False
    
    # Mobile view toggle for testing
    with st.sidebar:
        st.markdown("### 📱 DISPLAY OPTIONS")
        mobile_mode = st.checkbox("📱 Mobile View", value=st.session_state.mobile_view)
        st.session_state.mobile_view = mobile_mode
        
        if mobile_mode:
            st.success("📱 Mobile layout active")
        else:
            st.info("🖥️ Desktop layout active")
    
    # Main header with responsive title
    if st.session_state.mobile_view:
        # Mobile header - centered and smaller
        st.markdown("""
        <div style="text-align: center;">
            <h1 class="animated-title">SENTIMENT ANALYTICS</h1>
            <p style="color: #00f2ff; font-size: 1em; text-shadow: 0 0 5px #00f2ff; text-align: center;">
                REAL-TIME YOUTUBE COMMENT SENTIMENT ANALYZER
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # PC header - left aligned
        st.markdown("""
        <div style="text-align: left;">
            <h1 class="animated-title">SENTIMENT ANALYTICS</h1>
            <p style="color: #00f2ff; font-size: 1.2em; text-shadow: 0 0 5px #00f2ff; text-align: left;">
                REAL-TIME YOUTUBE COMMENT SENTIMENT ANALYZER
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Input section with futuristic styling - Responsive for mobile and PC
    with st.container():
        st.markdown("### INPUT PARAMETERS")
        
        # Responsive layout: 3 columns for PC, stacked for mobile
        if st.session_state.get('mobile_view', False):
            # Mobile layout - stacked vertically
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
            
            st.markdown("#### 📺 VIDEO INPUT")
            link = st.text_input("ENTER YOUTUBE URL:", placeholder="https://youtube.com/watch?v=... or https://youtu.be/...")
            
            st.markdown("#### ⚙️ SETTINGS")
            max_comments = st.number_input("MAX COMMENTS:", min_value=1, max_value=5000, value=100)
        else:
            # PC/Tablet layout - side by side
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
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
            
            with col2:
                st.markdown("#### 📺 VIDEO INPUT")
                link = st.text_input("ENTER YOUTUBE URL:", placeholder="https://youtube.com/watch?v=... or https://youtu.be/...")
            
            with col3:
                st.markdown("#### ⚙️ SETTINGS")
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
        
        # Display results in futuristic terminal style - Mobile responsive layout
        st.markdown("### 📊 SENTIMENT ANALYSIS RESULTS")
        
        # Summary stats - responsive layout
        # Mobile: 2x2 grid, PC: 1x4 row
        if 'mobile_view' in st.session_state and st.session_state.mobile_view:
            # Mobile layout - 2x2 grid
            row1_col1, row1_col2 = st.columns(2)
            row2_col1, row2_col2 = st.columns(2)
            
            with row1_col1:
                st.metric(
                    label="📊 TOTAL",
                    value=len(comments_df)
                )
            with row1_col2:
                st.metric(
                    label="✅ POSITIVE",
                    value=positive_count,
                    delta=f"{(positive_count/len(comments_df)*100):.1f}%"
                )
            with row2_col1:
                st.metric(
                    label="❌ NEGATIVE", 
                    value=negative_count,
                    delta=f"{(negative_count/len(comments_df)*100):.1f}%"
                )
            with row2_col2:
                st.metric(
                    label="⚖️ NEUTRAL",
                    value=neutral_count,
                    delta=f"{(neutral_count/len(comments_df)*100):.1f}%"
                )
        else:
            # PC layout - horizontal row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    label="📊 TOTAL PROCESSED",
                    value=len(comments_df),
                    delta=None
                )
            with col2:
                st.metric(
                    label="✅ POSITIVE",
                    value=positive_count,
                    delta=f"{(positive_count/len(comments_df)*100):.1f}%"
                )
            with col3:
                st.metric(
                    label="❌ NEGATIVE", 
                    value=negative_count,
                    delta=f"{(negative_count/len(comments_df)*100):.1f}%"
                )
            with col4:
                st.metric(
                    label="⚖️ NEUTRAL",
                    value=neutral_count,
                    delta=f"{(neutral_count/len(comments_df)*100):.1f}%"
                )
        
        # Terminal-style status display
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

        # Visualizations with futuristic styling - Responsive design
        st.markdown("### 📈 SENTIMENT VISUALIZATION")
        
        # Responsive chart layout
        if 'mobile_view' in st.session_state and st.session_state.mobile_view:
            # Mobile: Stack charts vertically with tabs
            tab1, tab2 = st.tabs(["📊 POLARITY", "📈 STRENGTH"])
            
            with tab1:
                # Pie Chart for mobile
                fig1, ax1 = plt.subplots(facecolor='none', figsize=(5, 5))
                ax1.pie(
                    [positive_count, negative_count],
                    labels=['POSITIVE', 'NEGATIVE'],
                    autopct='%1.1f%%',
                    colors=['#00ff88', '#ff0066'],
                    startangle=90,
                    wedgeprops={'edgecolor': '#0a0e17', 'linewidth': 2},
                    textprops={'color': '#e0f7ff', 'fontsize': 9, 'fontweight': 'bold'},
                    explode=(0.05, 0.05),
                    shadow=True
                )
                ax1.set_title("POLARITY MATRIX", color='#00f2ff', pad=10, fontsize=11, fontweight='bold')
                plt.gca().set_facecolor('none')
                st.pyplot(fig1)
            
            with tab2:
                # Bar Chart for mobile
                fig2, ax2 = plt.subplots(facecolor='none', figsize=(5, 4))
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
                             ha="center", color='#e0f7ff', fontsize=9, fontweight='bold')
                
                ax2.set_xlabel("SENTIMENT", color='#00f2ff', fontsize=9, fontweight='bold')
                ax2.set_ylabel("COUNT", color='#00f2ff', fontsize=9, fontweight='bold')
                ax2.set_title("SIGNAL STRENGTH", color='#00f2ff', pad=10, fontsize=11, fontweight='bold')
                ax2.grid(axis='y', linestyle='--', alpha=0.3, color='#0084ff')
                ax2.set_facecolor('none')
                ax2.tick_params(colors='#e0f7ff', labelsize=8)
                
                # Add glow effect to bars
                for bar in bars.patches:
                    bar.set_edgecolor('#00f2ff')
                    bar.set_linestyle('-')
                    bar.set_linewidth(1)
                    bar.set_alpha(0.9)
                
                st.pyplot(fig2)
        else:
            # PC/Tablet: Side by side charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.markdown("#### POLARITY MATRIX")
                # Pie Chart (only Positive and Negative)
                fig1, ax1 = plt.subplots(facecolor='none', figsize=(6, 6))
                ax1.pie(
                    [positive_count, negative_count],
                    labels=['POSITIVE', 'NEGATIVE'],
                    autopct='%1.1f%%',
                    colors=['#00ff88', '#ff0066'],
                    startangle=90,
                    wedgeprops={'edgecolor': '#0a0e17', 'linewidth': 2},
                    textprops={'color': '#e0f7ff', 'fontsize': 10, 'fontweight': 'bold'},
                    explode=(0.05, 0.05),
                    shadow=True
                )
                ax1.set_title("POLARITY MATRIX", color='#00f2ff', pad=15, fontsize=12, fontweight='bold')
                plt.gca().set_facecolor('none')
                st.pyplot(fig1)
            
            with chart_col2:
                st.markdown("#### SIGNAL STRENGTH")
                # Bar Chart
                fig2, ax2 = plt.subplots(facecolor='none', figsize=(6, 6))
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
                             ha="center", color='#e0f7ff', fontsize=10, fontweight='bold')
                
                ax2.set_xlabel("SENTIMENT", color='#00f2ff', fontsize=10, fontweight='bold')
                ax2.set_ylabel("COUNT", color='#00f2ff', fontsize=10, fontweight='bold')
                ax2.set_title("SIGNAL STRENGTH ANALYSIS", color='#00f2ff', pad=15, fontsize=12, fontweight='bold')
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
        
        # Raw data display - Responsive layout
        st.markdown("### 📁 RAW DATA PREVIEW")
        
        # Responsive dataframe display
        if st.session_state.mobile_view:
            # Mobile: Show fewer rows and columns, smaller height
            display_df = comments_df.head(10)[['Text', 'sentiment']].copy()
            # Truncate text for mobile display
            display_df['Text'] = display_df['Text'].str[:50] + '...'
            
            st.dataframe(
                display_df.style
                .applymap(lambda x: 'color: #00ff88' if x == 'positive' else ('color: #ff0066' if x == 'negative' else 'color: #e0f7ff'), subset=['sentiment'])
                .set_properties(**{'background-color': 'rgba(10, 14, 23, 0.8)', 'color': '#e0f7ff', 'border': '1px solid #0084ff'}),
                use_container_width=True,
                height=300
            )
        else:
            # PC: Show more data and full width
            st.dataframe(
                comments_df.head(15).style
                .applymap(lambda x: 'color: #00ff88' if x == 'positive' else ('color: #ff0066' if x == 'negative' else 'color: #e0f7ff'), subset=['sentiment'])
                .set_properties(**{'background-color': 'rgba(10, 14, 23, 0.8)', 'color': '#e0f7ff', 'border': '1px solid #0084ff'}),
                use_container_width=True,
                height=400
            )

if __name__ == "__main__":
    main()
