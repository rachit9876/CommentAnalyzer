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
    document.getElementById('youtube-url').value = 'https://youtu.be/qjwjMA2SIFs';
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

// Fetch real YouTube comments using API
async function fetchYouTubeComments(videoId, apiKey, maxResults) {
    const url = `https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=${videoId}&maxResults=${maxResults}&key=${apiKey}&order=relevance`;
    
    try {
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
            throw new Error('No comments found. Comments may be disabled or there are no comments yet.');
        }
        
        return data.items.map(item => 
            item.snippet.topLevelComment.snippet.textDisplay
                .replace(/<[^>]*>/g, '') // Remove HTML tags
                .trim()
        );
    } catch (error) {
        if (error.message.startsWith('Video not found') || 
            error.message.startsWith('Comments are disabled') ||
            error.message.startsWith('API quota') ||
            error.message.startsWith('Invalid API key') ||
            error.message.startsWith('No comments found')) {
            throw error;
        }
        throw new Error(`Failed to fetch comments: ${error.message}`);
    }
}

// Categorize sentiment score
function categorizeSentiment(score) {
    return score >= 0 ? 'positive' : 'negative';
}

// Get recommendation based on sentiment analysis
function getRecommendation(positivePercent, negativePercent) {
    if (positivePercent >= 70) {
        return {
            text: "🎉 Highly Recommended! This video has overwhelmingly positive feedback from viewers. It's likely to be engaging, informative, and worth your time.",
            class: "positive"
        };
    } else if (positivePercent >= 60) {
        return {
            text: "👍 Recommended! This video has mostly positive feedback. It's probably worth watching.",
            class: "positive"
        };
    } else if (positivePercent >= 40) {
        return {
            text: "🤔 Mixed Reviews! This video has balanced feedback. Whether you'll enjoy it depends on your personal preferences.",
            class: "neutral"
        };
    } else {
        return {
            text: "❌ Not Recommended! This video has predominantly negative feedback. You might want to skip this one.",
            class: "negative"
        };
    }
}

// Create or update the pie chart
function createChart(positive, negative) {
    const ctx = document.getElementById('sentiment-chart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (chart) {
        chart.destroy();
    }
    
    chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Positive', 'Negative'],
            datasets: [{
                data: [positive, negative],
                backgroundColor: [
                    '#48bb78',
                    '#f56565'
                ],
                borderWidth: 3,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 14
                        }
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
    
    // Show first 10 comments as samples
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
        const badgeColor = sentiment === 'positive' ? '#16a34a' : '#ef4444';

        commentDiv.className = 'comment';
        commentDiv.innerHTML = `
            <div style="color:rgba(230,238,248,0.9);margin-bottom:8px">${escapeHtml(comments[i])}</div>
            <div style="font-weight:600;color:${badgeColor};text-transform:uppercase">${sentiment}</div>
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
    
    console.log('Extracted Video ID:', videoId);
    
    // Show loading state
    analyzeBtn.disabled = true;
    if (!analyzeBtn.dataset.originalText) analyzeBtn.dataset.originalText = analyzeBtn.textContent || 'Analyze';
    analyzeBtn.textContent = 'Analyzing...';
    
    try {
        // Fetch real YouTube comments
        const comments = await fetchYouTubeComments(videoId, apiKey, commentCount);
        
        if (comments.length === 0) {
            throw new Error('No comments found for this video');
        }
        
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

        // Categorize sentiments
        let positive = 0, negative = 0;

        sentiments.forEach(score => {
            const category = categorizeSentiment(score);
            if (category === 'positive') positive++;
            else negative++;
        });
        
        // Calculate percentages
        const total = positive + negative;
        const positivePercent = Math.round((positive / total) * 100);
        const negativePercent = Math.round((negative / total) * 100);
        
        // Update UI
        document.getElementById('positive-count').textContent = positive;
        document.getElementById('negative-count').textContent = negative;
        
        document.getElementById('positive-percentage').textContent = positivePercent + '%';
        document.getElementById('negative-percentage').textContent = negativePercent + '%';
        
        // Create chart
        createChart(positive, negative);
        
        // Display sample comments
        displaySampleComments(comments, sentiments);
        
        // Show recommendation
        const recommendation = getRecommendation(positivePercent, negativePercent);
        document.getElementById('recommendation-text').textContent = recommendation.text;
        const recElement = document.getElementById('recommendation');
        if (recommendation.class === 'positive') {
            recElement.style.background = 'linear-gradient(90deg, rgba(34,197,94,0.08), transparent)';
        } else if (recommendation.class === 'negative') {
            recElement.style.background = 'linear-gradient(90deg, rgba(239,68,68,0.08), transparent)';
        } else {
            recElement.style.background = 'linear-gradient(90deg, rgba(250,204,21,0.08), transparent)';
        }
        recElement.style.border = '1px solid rgba(255,255,255,0.06)';
        recElement.style.padding = '12px';
        recElement.style.borderRadius = '12px';
        
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
