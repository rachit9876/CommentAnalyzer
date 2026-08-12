// Global variables
let chart = null;

// Load saved API key when page loads
document.addEventListener('DOMContentLoaded', function() {
    const savedApiKey = localStorage.getItem('youtube-api-key');
    if (savedApiKey) {
        document.getElementById('api-key').value = savedApiKey;
    }
});

// Event listeners
document.getElementById('analyze-btn').addEventListener('click', analyzeComments);
document.getElementById('api-key').addEventListener('input', saveApiKey);
document.getElementById('random-url-btn').addEventListener('click', function() {
    document.getElementById('youtube-url').value = 'https://www.youtube.com/watch?v=qjwjMA2SIFs';
    document.getElementById('api-key').value = 'AIzaSyDrkk7LmuT1o_57Z1gx824ktqhsQtXcyvs';
    saveApiKey();
});

// Save API key to localStorage
function saveApiKey() {
    const apiKey = document.getElementById('api-key').value;
    if (apiKey) {
        localStorage.setItem('youtube-api-key', apiKey);
    }
}

// Extract video ID from YouTube URL
function extractVideoId(url) {
    const patterns = [
        /(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})/, // Standard watch URL
        /(?:youtu\.be\/)([a-zA-Z0-9_-]{11})/, // Shortened URL
        /(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/, // Embed URL
        /(?:youtube\.com\/v\/)([a-zA-Z0-9_-]{11})/, // Old embed format
        /(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})/ // Shorts URL
    ];
    
    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match) return match[1];
    }
    return null;
}

// Fetch real YouTube comments using API with pagination support
async function fetchYouTubeComments(videoId, apiKey, targetCount) {
    let comments = [];
    let pageToken = '';

    while (comments.length < targetCount) {
        const pageSize = Math.min(100, targetCount - comments.length);
        let url = `https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=${videoId}&maxResults=${pageSize}&key=${apiKey}&order=relevance`;
        if (pageToken) {
            url += `&pageToken=${pageToken}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.error) {
            const errorMsg = data.error.message.replace(/<[^>]*>/g, '');
            if (errorMsg.includes('could not be found')) {
                throw new Error('Video not found. The video may have been deleted, is private, or the URL is incorrect.');
            } else if (errorMsg.includes('disabled comments')) {
                throw new Error('Comments are disabled for this video.');
            } else if (errorMsg.includes('quota')) {
                throw new Error('API quota exceeded. Please try again later or use a different API key.');
            } else if (errorMsg.includes('API key')) {
                throw new Error('Invalid API key. Please check your YouTube Data API key.');
            }
            throw new Error(errorMsg);
        }

        if (!data.items || data.items.length === 0) {
            if (comments.length === 0) {
                throw new Error('No comments found. Comments may be disabled or there are no comments yet.');
            }
            break;
        }

        const newComments = data.items.map(item => 
            item.snippet.topLevelComment.snippet.textDisplay
                .replace(/<[^>]*>/g, '') // Remove HTML tags
                .trim()
        );

        comments.push(...newComments);

        if (!data.nextPageToken) {
            break;
        }
        pageToken = data.nextPageToken;
    }

    return comments;
}

// Categorize sentiment score (3-way)
function categorizeSentiment(score) {
    if (score > 0.3) return 'positive';
    if (score < -0.3) return 'negative';
    return 'neutral';
}

// Get recommendation based on sentiment analysis
function getRecommendation(positivePercent, neutralPercent, negativePercent) {
    if (positivePercent >= 65) {
        return {
            text: "🎉 Highly Recommended! Overwhelmingly positive feedback from viewers. It's likely to be engaging and worth your time.",
            class: "positive"
        };
    } else if (positivePercent >= 50 && positivePercent > negativePercent) {
        return {
            text: "👍 Recommended! Mostly positive sentiment in viewer comments.",
            class: "positive"
        };
    } else if (negativePercent >= 45) {
        return {
            text: "❌ Not Recommended! This video has predominantly negative feedback.",
            class: "negative"
        };
    } else {
        return {
            text: "🤔 Mixed / Neutral Reviews! The video has balanced or mostly neutral feedback.",
            class: "neutral"
        };
    }
}

// Create or update 3-way pie chart
function createChart(positive, neutral, negative) {
    const ctx = document.getElementById('sentiment-chart').getContext('2d');
    
    if (chart) {
        chart.destroy();
    }
    
    chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [positive, neutral, negative],
                backgroundColor: [
                    '#10b981', // positive (green)
                    '#9ca3af', // neutral (gray)
                    '#ef4444'  // negative (red)
                ],
                borderWidth: 2,
                borderColor: '#141414'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e5e5e5',
                        padding: 16,
                        font: { size: 13 }
                    }
                }
            }
        }
    });
}

// Display sample comments
function displaySampleComments(comments, sentiments) {
    const commentsList = document.getElementById('comments-list');
    commentsList.innerHTML = '';
    
    const sampleCount = Math.min(10, comments.length);
    
    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    for (let i = 0; i < sampleCount; i++) {
        const commentDiv = document.createElement('div');
        const sentiment = categorizeSentiment(sentiments[i]);
        let badgeColor = '#9ca3af';
        if (sentiment === 'positive') badgeColor = '#10b981';
        else if (sentiment === 'negative') badgeColor = '#ef4444';

        commentDiv.className = `comment ${sentiment}`;
        commentDiv.innerHTML = `
            <div style="color:rgba(245,245,245,0.9);margin-bottom:8px">${escapeHtml(comments[i])}</div>
            <div style="font-weight:600;color:${badgeColor};text-transform:uppercase;font-size:12px">${sentiment}</div>
        `;

        commentsList.appendChild(commentDiv);
    }
}

// Main analysis function
async function analyzeComments() {
    const apiKeyInput = document.getElementById('api-key');
    const urlInput = document.getElementById('youtube-url');
    const countSelect = document.getElementById('comment-count');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultsSection = document.getElementById('results-section');
    
    const apiKey = apiKeyInput.value.trim();
    const url = urlInput.value.trim();
    const commentCount = parseInt(countSelect.value);
    
    // Validate inputs
    if (!apiKey) {
        alert('Please enter your YouTube API key');
        return;
    }
    
    if (!url) {
        alert('Please enter a YouTube URL');
        return;
    }
    
    const videoId = extractVideoId(url);
    if (!videoId) {
        alert('Invalid YouTube URL. Please use a valid format like:\nhttps://www.youtube.com/watch?v=VIDEO_ID\nor\nhttps://youtu.be/VIDEO_ID');
        return;
    }
    
    // Show loading state
    analyzeBtn.disabled = true;
    if (!analyzeBtn.dataset.originalText) analyzeBtn.dataset.originalText = analyzeBtn.textContent || 'Analyze';
    analyzeBtn.textContent = 'Fetching Comments...';
    
    try {
        // Ensure sentiment dictionary initialization is finished
        if (typeof sentimentInitPromise !== 'undefined') {
            await sentimentInitPromise;
        }

        // Fetch real YouTube comments (with pagination loop)
        const comments = await fetchYouTubeComments(videoId, apiKey, commentCount);
        
        if (comments.length === 0) {
            throw new Error('No comments found for this video');
        }

        analyzeBtn.textContent = 'Analyzing Sentiment...';
        
        // Analyze sentiment for each comment
        const sentiments = comments.map(comment => {
            try {
                const res = (typeof analyzeSentiment === 'function') ? analyzeSentiment(comment) : null;
                return res && typeof res.score === 'number' ? res.score : 0;
            } catch (e) {
                console.warn('sentiment.js analyze error:', e);
                return 0;
            }
        });

        // Categorize sentiments (3-way)
        let positive = 0, neutral = 0, negative = 0;

        sentiments.forEach(score => {
            const category = categorizeSentiment(score);
            if (category === 'positive') positive++;
            else if (category === 'negative') negative++;
            else neutral++;
        });
        
        // Calculate percentages
        const total = positive + neutral + negative;
        const positivePercent = Math.round((positive / total) * 100) || 0;
        const neutralPercent = Math.round((neutral / total) * 100) || 0;
        const negativePercent = Math.round((negative / total) * 100) || 0;
        
        // Update UI
        document.getElementById('positive-count').textContent = positive;
        const neutralCountElem = document.getElementById('neutral-count');
        if (neutralCountElem) neutralCountElem.textContent = neutral;
        document.getElementById('negative-count').textContent = negative;
        
        document.getElementById('positive-percentage').textContent = positivePercent + '%';
        const neutralPercElem = document.getElementById('neutral-percentage');
        if (neutralPercElem) neutralPercElem.textContent = neutralPercent + '%';
        document.getElementById('negative-percentage').textContent = negativePercent + '%';
        
        // Create chart
        createChart(positive, neutral, negative);
        
        // Display sample comments
        displaySampleComments(comments, sentiments);
        
        // Show recommendation
        const recommendation = getRecommendation(positivePercent, neutralPercent, negativePercent);
        document.getElementById('recommendation-text').textContent = recommendation.text;
        const recElement = document.getElementById('recommendation');
        if (recommendation.class === 'positive') {
            recElement.style.background = 'rgba(16, 185, 129, 0.05)';
            recElement.style.borderColor = 'rgba(16, 185, 129, 0.2)';
        } else if (recommendation.class === 'negative') {
            recElement.style.background = 'rgba(239, 68, 68, 0.05)';
            recElement.style.borderColor = 'rgba(239, 68, 68, 0.2)';
        } else {
            recElement.style.background = 'rgba(156, 163, 175, 0.05)';
            recElement.style.borderColor = 'rgba(156, 163, 175, 0.2)';
        }
        
        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Error analyzing comments:', error);
        alert(error.message || 'Error analyzing comments. Please check your API key and try again.');
    } finally {
        // Hide loading state
        analyzeBtn.disabled = false;
        if (analyzeBtn.dataset.originalText) {
            analyzeBtn.textContent = analyzeBtn.dataset.originalText;
            delete analyzeBtn.dataset.originalText;
        }
    }
}

// Add utility functions for better UX
document.getElementById('youtube-url').addEventListener('input', function(e) {
    const url = e.target.value;
    if (url && !extractVideoId(url)) {
        e.target.style.borderColor = '#f56565';
    } else {
        e.target.style.borderColor = '#e2e8f0';
    }
});

// Add enter key support
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        analyzeComments();
    }
});

