// Global variables
let sentimentData = {};
let chart = null;

// Load sentiment data and saved API key when page loads
document.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch('sentiment.json');
        sentimentData = await response.json();
        console.log('Sentiment data loaded successfully');
        
        // Load saved API key
        const savedApiKey = localStorage.getItem('youtube-api-key');
        if (savedApiKey) {
            document.getElementById('api-key').value = savedApiKey;
        }
    } catch (error) {
        console.error('Error loading sentiment data:', error);
        alert('Error loading sentiment analysis data. Please refresh the page.');
    }
});

// Event listeners
document.getElementById('analyze-btn').addEventListener('click', analyzeComments);
document.getElementById('api-key').addEventListener('input', saveApiKey);
document.getElementById('random-url-btn').addEventListener('click', function() {
    document.getElementById('youtube-url').value = 'https://www.youtube.com/watch?v=YbJOTdZBX1g';
    
    //👇Well, I’m aware of it, but bro, it only works on my whitelisted site — so it’s useless for you anyway, LOL.
    document.getElementById('api-key').value = 'AIzaSyCYIiEO_xynKzt51-dadWc6jO8MMI0Nvbo'; 
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
    const regex = /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

// Fetch real YouTube comments using API
async function fetchYouTubeComments(videoId, apiKey, maxResults) {
    const url = `https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=${videoId}&maxResults=${maxResults}&key=${apiKey}&order=relevance`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error.message);
        }
        
        return data.items.map(item => 
            item.snippet.topLevelComment.snippet.textDisplay
                .replace(/<[^>]*>/g, '') // Remove HTML tags
                .trim()
        );
    } catch (error) {
        throw new Error(`Failed to fetch comments: ${error.message}`);
    }
}

// Analyze sentiment of a single comment
function analyzeSentiment(comment) {
    const words = comment.toLowerCase()
        .replace(/[^\w\s]/g, ' ')
        .split(/\s+/)
        .filter(word => word.length > 0);
    
    let totalScore = 0;
    let wordCount = 0;
    
    // Check each word against sentiment dictionary
    words.forEach(word => {
        if (sentimentData[word] !== undefined) {
            totalScore += sentimentData[word];
            wordCount++;
        }
    });
    
    // Check for phrases (2-word combinations)
    for (let i = 0; i < words.length - 1; i++) {
        const phrase = words[i] + ' ' + words[i + 1];
        if (sentimentData[phrase] !== undefined) {
            totalScore += sentimentData[phrase];
            wordCount++;
        }
    }
    
    // If no sentiment words found, return neutral
    if (wordCount === 0) {
        return 0;
    }
    
    // Return average sentiment score
    return totalScore / wordCount;
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
    
    for (let i = 0; i < sampleCount; i++) {
        const commentDiv = document.createElement('div');
        const sentiment = categorizeSentiment(sentiments[i]);
        const borderColor = sentiment === 'positive' ? 'border-cyan-400' : 'border-blue-500';
        const textColor = sentiment === 'positive' ? 'text-cyan-400' : 'text-blue-500';
        
        commentDiv.className = `bg-black/40 backdrop-blur-sm rounded-2xl p-4 shadow-lg border-l-4 ${borderColor} transition-all hover:translate-x-1 hover:-translate-y-0.5 hover:shadow-xl`;
        
        commentDiv.innerHTML = `
            <div class="text-gray-400 mb-2 leading-relaxed">${comments[i]}</div>
            <div class="text-sm font-semibold uppercase tracking-wide ${textColor}">${sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}</div>
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
        alert('Please enter a valid YouTube URL');
        return;
    }
    
    // Show loading state
    analyzeBtn.disabled = true;
    analyzeBtn.querySelector('.btn-text').style.display = 'none';
    analyzeBtn.querySelector('.loading-spinner').style.display = 'inline';
    
    try {
        // Fetch real YouTube comments
        const comments = await fetchYouTubeComments(videoId, apiKey, commentCount);
        
        if (comments.length === 0) {
            throw new Error('No comments found for this video');
        }
        
        // Analyze sentiment for each comment
        const sentiments = comments.map(comment => analyzeSentiment(comment));
        
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
        let bgColor = 'bg-black/30';
        if (recommendation.class === 'positive') bgColor = 'bg-green-500/20';
        else if (recommendation.class === 'negative') bgColor = 'bg-red-500/20';
        else if (recommendation.class === 'neutral') bgColor = 'bg-yellow-500/20';
        recElement.className = `text-center mb-8 p-6 ${bgColor} rounded-xl border border-white/10`;
        
        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Error analyzing comments:', error);
        alert(error.message || 'Error analyzing comments. Please check your API key and try again.');
    } finally {
        // Hide loading state
        analyzeBtn.disabled = false;
        analyzeBtn.querySelector('.btn-text').style.display = 'inline';
        analyzeBtn.querySelector('.loading-spinner').style.display = 'none';
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
