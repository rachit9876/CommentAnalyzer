# YouTube Comment Sentiment Analyzer ( [Try Now](https://commentanalyzer.pages.dev/) )

![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Chart.js](https://img.shields.io/badge/chart.js-F5788D.svg?style=for-the-badge&logo=chart.js&logoColor=white)
![YouTube](https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white)

A web application that analyzes the sentiment of YouTube video comments to help users decide whether a video is worth watching based on viewer feedback.

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