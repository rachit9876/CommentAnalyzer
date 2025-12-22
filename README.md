# YouTube Comment Sentiment Analyzer ( [Try Now](https://commentanalyzer.pages.dev/) )

![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Chart.js](https://img.shields.io/badge/chart.js-F5788D.svg?style=for-the-badge&logo=chart.js&logoColor=white)
![YouTube](https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white)

A web application that analyzes the sentiment of YouTube video comments to help users decide whether a video is worth watching based on viewer feedback.

```mermaid
make it digarm
graph TD

%% =========================
%% ACTORS
%% =========================
User["User (Browser User)"]

%% =========================
%% CLIENT DEVICE
%% =========================
subgraph Client["Client Device (Web Browser)"]

    Browser["Web Browser Runtime"]

    %% -------------------------
    %% UI CONTAINERS
    %% -------------------------
    subgraph UI["Presentation Layer (Static HTML + CSS)"]

        IndexUI["YouTube Analyzer UI<br/>index.html"]
        TextUI["Text Analyzer UI<br/>text-analyzer.html"]
        Styles["Shared UI Theme<br/>style.css<br/>Material 3 Inspired"]

    end

    %% -------------------------
    %% APPLICATION LOGIC
    %% -------------------------
    subgraph AppLogic["Application Logic (JavaScript)"]

        YTController["YouTube Analysis Controller<br/>script.js"]
        TextController["Text Analysis Controller<br/>(inline JS)"]

    end

    %% -------------------------
    %% DOMAIN / CORE
    %% -------------------------
    subgraph Domain["Sentiment Domain Engine"]

        SentimentEngine["Sentiment Analyzer<br/>sentiment.js"]
        Lexicon["Sentiment Lexicon<br/>sentiment.json"]

    end

    %% -------------------------
    %% VISUALIZATION
    %% -------------------------
    subgraph Visualization["Visualization Layer"]

        ChartJS["Chart Renderer<br/>Chart.js"]

    end

end

%% =========================
%% EXTERNAL SYSTEMS
%% =========================
subgraph External["External Services"]

    YouTubeAPI["YouTube Data API v3"]
    GoogleFonts["Google Fonts CDN"]
    ChartCDN["Chart.js CDN"]

end

%% =========================
%% USER INTERACTIONS
%% =========================
User --> Browser
Browser --> IndexUI
Browser --> TextUI

%% =========================
%% UI DEPENDENCIES
%% =========================
IndexUI --> Styles
TextUI --> Styles
Styles --> GoogleFonts

%% =========================
%% UI → CONTROLLERS
%% =========================
IndexUI --> YTController
TextUI --> TextController

%% =========================
%% CONTROLLERS → DOMAIN
%% =========================
YTController --> SentimentEngine
TextController --> SentimentEngine
SentimentEngine --> Lexicon

%% =========================
%% YOUTUBE DATA FLOW
%% =========================
YTController -->|Fetch Comments| YouTubeAPI
YouTubeAPI -->|Comment Threads JSON| YTController

%% =========================
%% SENTIMENT PIPELINE
%% =========================
YTController -->|Normalized Comments| SentimentEngine
TextController -->|Raw User Text| SentimentEngine

SentimentEngine -->|Score, Label, Tokens| YTController
SentimentEngine -->|Score, Label, Tokens| TextController

%% =========================
%% VISUALIZATION FLOW
%% =========================
ChartCDN --> ChartJS
YTController -->|Aggregated Sentiment Stats| ChartJS
ChartJS -->|Canvas Render| IndexUI

%% =========================
%% RESULT RENDERING
%% =========================
YTController -->|Counts, Percentages, Recommendation| IndexUI
TextController -->|Label, Score, Confidence, Tokens| TextUI
```

## Features

- **Real-time Comment Analysis**: Fetches actual YouTube comments using the YouTube Data API
- **Sentiment Classification**: Categorizes comments as positive or negative using a sentiment dictionary
- **Visual Analytics**: Interactive pie chart showing sentiment distribution
- **Smart Recommendations**: Provides viewing recommendations based on comment sentiment
- **Sample Comments**: Displays analyzed comments with their sentiment labels
- **Responsive Design**: Works on desktop and mobile devices

## Setup

1. **Get YouTube API Key**:
   - Visit [Google Cloud Console](https://console.developers.google.com/)
   - Create a new project or select existing one
   - Enable YouTube Data API v3
   - Create credentials (API Key)

2. **Run the Application**:
   - Open `index.html` in a web browser
   - Enter your YouTube API key
   - Paste a YouTube video URL
   - Select number of comments to analyze (50-2000)
   - Click "Analyze"

## Usage

1. Enter your YouTube API key in the API Key field
2. Paste a YouTube video URL
3. Choose how many comments to analyze
4. Click "Analyze" to start the sentiment analysis
5. View results including:
   - Overall recommendation
   - Sentiment distribution chart
   - Positive/negative comment counts and percentages
   - Sample analyzed comments

## Files

- `index.html` - Main application interface
- `script.js` - Core functionality and API integration
- `styles.css` - Application styling
- `sentiment.json` - Sentiment analysis dictionary


## Requirements

- Modern web browser with JavaScript enabled
- Valid YouTube Data API key
- Internet connection for API calls