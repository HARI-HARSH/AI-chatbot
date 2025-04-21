// API Configuration
const API_URL = "http://localhost:5000/generate";

// DOM Elements
const platformSelect = document.getElementById('platform');
const topicInput = document.getElementById('topic');
const generateBtn = document.getElementById('generateBtn');
const loadingDiv = document.getElementById('loading');
const resultDiv = document.getElementById('result');
const errorDiv = document.getElementById('error');

// Result Elements
const contentTitle = document.getElementById('contentTitle');
const contentText = document.getElementById('contentText');
const hashtags = document.getElementById('hashtags');
const emojis = document.getElementById('emojis');
const postingTimes = document.getElementById('postingTimes');
const platformTips = document.getElementById('platformTips');

// Copy Buttons
const copyContentBtn = document.getElementById('copyContent');
const copyHashtagsBtn = document.getElementById('copyHashtags');
const copyAllBtn = document.getElementById('copyAll');

// Event Listeners
generateBtn.addEventListener('click', generateContent);
copyContentBtn.addEventListener('click', () => copyToClipboard(contentText.textContent));
copyHashtagsBtn.addEventListener('click', () => copyToClipboard(hashtags.textContent));
copyAllBtn.addEventListener('click', () => copyToClipboard(`${contentText.textContent}\n\n${hashtags.textContent}`));

async function generateContent() {
    const platform = platformSelect.value;
    const topic = topicInput.value.trim();

    if (!topic) {
        showError('Please enter a topic or idea first.');
        return;
    }

    // Show loading state
    loadingDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic: topic,
                platform: platform
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate content');
        }

        // Display the content
        displayContent(data);

    } catch (error) {
        showError(error.message);
    } finally {
        loadingDiv.classList.add('hidden');
    }
}

function displayContent(data) {
    contentTitle.textContent = data.title;
    contentText.textContent = data.content;
    hashtags.textContent = data.hashtags.join(' ');
    emojis.textContent = data.emoji_suggestions;
    postingTimes.textContent = data.best_posting_times;
    platformTips.textContent = data.platform_specific_tips;

    resultDiv.classList.remove('hidden');
}

function showError(message) {
    errorDiv.querySelector('.error-message').textContent = message;
    errorDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show success feedback (you could add a toast notification here)
        alert('Copied to clipboard!');
    }).catch(err => {
        showError('Failed to copy text: ' + err);
    });
} 