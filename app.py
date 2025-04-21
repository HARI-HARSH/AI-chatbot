from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import json
import os
import markdown
from markdown.extensions import tables, fenced_code

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Configure Gemini
genai.configure(api_key="AIzaSyALXYNsqWsmWQ0BWTzsxtrVI8gFv9tlTlI")

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/generate', methods=['POST'])
def generate_content():
    try:
        data = request.json
        topic = data.get('topic')
        platform = data.get('platform', 'general')

        if not topic:
            return jsonify({'error': 'Please enter a topic or idea first.'}), 400

        system_prompt = f"""You are a social media content expert. Create engaging, well-formatted content based on the user's input.
        Format the response as JSON with the following structure:
        {{
            "title": "Main topic or headline",
            "content": "The main content in markdown format with proper formatting and emojis",
            "hashtags": ["relevant", "hashtags"],
            "emoji_suggestions": "Relevant emojis to use",
            "best_posting_times": "Suggested posting times",
            "platform_specific_tips": "Tips specific to the platform"
        }}
        
        Ensure the content is:
        - Engaging and conversational
        - Well-structured with clear sections using markdown headers (# for main title, ## for sections)
        - Uses appropriate line breaks
        - Includes relevant emojis throughout the content
        - Uses markdown formatting for lists, bold, italics, etc.
        - Optimized for {platform}
        
        Example format:
        # Main Title 🍽️
        
        ## Section 1 📝
        - Point 1
        - Point 2
        
        ## Section 2 🔥
        Some text with **bold** and *italic* formatting.
        
        Remember to:
        - Use emojis naturally throughout the content
        - Format lists with proper markdown syntax
        - Use headers for better structure
        - Include relevant hashtags and emoji suggestions"""

        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            f"{system_prompt}\n\nUser input: {topic}"
        )
        
        # Extract JSON from the response
        response_text = response.text
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        json_str = response_text[start_idx:end_idx]
        data = json.loads(json_str)
        
        # Convert markdown content to HTML while preserving emojis
        md = markdown.Markdown(extensions=['tables', 'fenced_code'])
        data['content'] = md.convert(data['content'])
        
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Create static files with UTF-8 encoding
    with open('static/index.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Media Content Generator</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="header-content">
                <i class="fas fa-robot"></i>
                <h1>Social Media Content Generator</h1>
            </div>
            <div class="header-controls">
                <div class="custom-dropdown">
                    <button class="dropdown-toggle">
                        <i class="fas fa-globe"></i>
                        <span class="selected-text">General</span>
                        <i class="fas fa-chevron-down"></i>
                    </button>
                    <div class="dropdown-menu">
                        <div class="dropdown-item" data-value="general">
                            <i class="fas fa-globe"></i>
                            <span>General</span>
                        </div>
                        <div class="dropdown-item" data-value="twitter">
                            <i class="fab fa-twitter"></i>
                            <span>Twitter/X</span>
                        </div>
                        <div class="dropdown-item" data-value="linkedin">
                            <i class="fab fa-linkedin"></i>
                            <span>LinkedIn</span>
                        </div>
                        <div class="dropdown-item" data-value="instagram">
                            <i class="fab fa-instagram"></i>
                            <span>Instagram</span>
                        </div>
                        <div class="dropdown-item" data-value="facebook">
                            <i class="fab fa-facebook"></i>
                            <span>Facebook</span>
                        </div>
                    </div>
                </div>
                <button class="theme-toggle" id="themeToggle">
                    <i class="fas fa-sun"></i>
                </button>
            </div>
        </div>

        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                <div class="message-content">
                    <p>👋 Hi! I'm your social media content assistant. What would you like to create content about?</p>
                </div>
            </div>
        </div>

        <div class="chat-input-container">
            <div class="input-wrapper">
                <textarea id="topic" placeholder="Type your topic or idea here..." rows="1"></textarea>
                <button id="generateBtn">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>

    <script src="script.js"></script>
</body>
</html>''')

    with open('static/style.css', 'w', encoding='utf-8') as f:
        f.write(''':root {
    --primary-color: #4a90e2;
    --secondary-color: #2c3e50;
    --background-color: #f5f7fa;
    --chat-bg: #ffffff;
    --user-message-bg: #e3f2fd;
    --bot-message-bg: #ffffff;
    --text-color: #333;
    --border-color: #ddd;
    --success-color: #2ecc71;
    --error-color: #e74c3c;
    --dropdown-bg: #ffffff;
    --dropdown-hover: #f0f0f0;
    --header-bg: #4a90e2;
    --header-text: #ffffff;
    --input-bg: #ffffff;
    --input-text: #333;
    --input-placeholder: #666;
}

[data-theme="dark"] {
    --primary-color: #4a90e2;
    --secondary-color: #a0b3c6;
    --background-color: #1a1a1a;
    --chat-bg: #2d2d2d;
    --user-message-bg: #4a90e2;
    --bot-message-bg: #3d3d3d;
    --text-color: #ffffff;
    --border-color: #404040;
    --dropdown-bg: #3d3d3d;
    --dropdown-hover: #4d4d4d;
    --header-bg: #2d2d2d;
    --header-text: #ffffff;
    --input-bg: #2d2d2d;
    --input-text: #ffffff;
    --input-placeholder: #888;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    transition: background-color 0.3s, color 0.3s, border-color 0.3s;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    background-color: var(--background-color);
    color: var(--text-color);
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.chat-container {
    width: 100%;
    max-width: 800px;
    height: 90vh;
    background-color: var(--chat-bg);
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    margin: 20px;
}

.chat-header {
    padding: 1rem;
    background-color: var(--primary-color);
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-content {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.header-content i {
    font-size: 1.5rem;
}

.header-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.custom-dropdown {
    position: relative;
    min-width: 150px;
}

.dropdown-toggle {
    width: 100%;
    padding: 0.5rem 1rem;
    background-color: var(--dropdown-bg);
    border: none;
    border-radius: 4px;
    color: var(--text-color);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    transition: background-color 0.3s;
}

.dropdown-toggle:hover {
    background-color: var(--dropdown-hover);
}

.dropdown-toggle .fa-chevron-down {
    margin-left: auto;
    transition: transform 0.3s;
}

.custom-dropdown.open .fa-chevron-down {
    transform: rotate(180deg);
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    margin-top: 0.5rem;
    background-color: var(--dropdown-bg);
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s;
    z-index: 1000;
}

.custom-dropdown.open .dropdown-menu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.dropdown-item {
    padding: 0.5rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    color: var(--text-color);
    transition: background-color 0.3s;
}

.dropdown-item:hover {
    background-color: var(--dropdown-hover);
}

.theme-toggle {
    background: transparent;
    border: none;
    color: var(--header-text);
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.3s;
}

.theme-toggle:hover {
    transform: rotate(30deg);
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    background-color: var(--background-color);
}

.message {
    max-width: 80%;
    padding: 1rem;
    border-radius: 12px;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message.user {
    align-self: flex-end;
    background-color: var(--user-message-bg);
    border-bottom-right-radius: 4px;
}

.message.bot {
    align-self: flex-start;
    background-color: var(--bot-message-bg);
    border-bottom-left-radius: 4px;
}

.message-content {
    word-wrap: break-word;
}

.message-content .markdown-body {
    background-color: transparent !important;
    color: var(--text-color) !important;
}

.message-content .content-details {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
}

.message-content .content-details p {
    margin-bottom: 0.5rem;
}

.chat-input-container {
    padding: 1rem;
    border-top: 1px solid var(--border-color);
    background-color: var(--chat-bg);
}

.input-wrapper {
    display: flex;
    gap: 0.5rem;
    align-items: flex-end;
}

textarea {
    flex: 1;
    padding: 0.8rem;
    border: 1px solid var(--border-color);
    border-radius: 20px;
    resize: none;
    font-size: 1rem;
    max-height: 150px;
    overflow-y: auto;
    background-color: var(--input-bg);
    color: var(--input-text);
}

textarea::placeholder {
    color: var(--input-placeholder);
}

textarea:focus {
    outline: none;
    border-color: var(--primary-color);
    background-color: var(--input-bg);
    color: var(--input-text);
}

button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    padding: 0.8rem;
    border-radius: 50%;
    cursor: pointer;
    transition: background-color 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
}

button:hover {
    background-color: #357abd;
}

#generateBtn {
    width: 40px;
    height: 40px;
}

.hidden {
    display: none;
}

.message.loading {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.typing-indicator {
    display: flex;
    gap: 0.3rem;
    padding: 0.5rem;
}

.typing-circle {
    width: 8px;
    height: 8px;
    background-color: var(--primary-color);
    border-radius: 50%;
    opacity: 0.4;
    animation: typing-bounce 1s infinite;
}

.typing-circle:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-circle:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing-bounce {
    0%, 100% {
        transform: translateY(0);
        opacity: 0.4;
    }
    50% {
        transform: translateY(-4px);
        opacity: 0.8;
    }
}

/* Markdown styles */
.markdown-body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.5;
    word-wrap: break-word;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
    color: var(--text-color);
}

.markdown-body p {
    margin-top: 0;
    margin-bottom: 16px;
}

.markdown-body ul,
.markdown-body ol {
    padding-left: 2em;
    margin-top: 0;
    margin-bottom: 16px;
}

.markdown-body li {
    margin-bottom: 0.5em;
}

.markdown-body code {
    padding: 0.2em 0.4em;
    margin: 0;
    font-size: 85%;
    background-color: rgba(27, 31, 35, 0.05);
    border-radius: 3px;
}

.markdown-body pre {
    padding: 16px;
    overflow: auto;
    font-size: 85%;
    line-height: 1.45;
    background-color: #f6f8fa;
    border-radius: 3px;
}

.markdown-body blockquote {
    padding: 0 1em;
    color: #6a737d;
    border-left: 0.25em solid #dfe2e5;
    margin: 0 0 16px 0;
}

/* Responsive Design */
@media (max-width: 600px) {
    .chat-container {
        height: 100vh;
        margin: 0;
        border-radius: 0;
    }
    
    .message {
        max-width: 90%;
    }
}''')

    with open('static/script.js', 'w', encoding='utf-8') as f:
        f.write('''// API Configuration
const API_URL = "/generate";

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const topicInput = document.getElementById('topic');
const generateBtn = document.getElementById('generateBtn');
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;
const dropdown = document.querySelector('.custom-dropdown');
const dropdownToggle = document.querySelector('.dropdown-toggle');
const dropdownItems = document.querySelectorAll('.dropdown-item');
const selectedText = document.querySelector('.selected-text');
let selectedPlatform = 'general';

// Theme Management
function toggleTheme() {
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update theme toggle icon
    themeToggle.innerHTML = newTheme === 'light' 
        ? '<i class="fas fa-sun"></i>' 
        : '<i class="fas fa-moon"></i>';
}

// Initialize theme
const savedTheme = localStorage.getItem('theme') || 'light';
html.setAttribute('data-theme', savedTheme);
themeToggle.innerHTML = savedTheme === 'light' 
    ? '<i class="fas fa-sun"></i>' 
    : '<i class="fas fa-moon"></i>';

// Dropdown functionality
dropdownToggle.addEventListener('click', () => {
    dropdown.classList.toggle('open');
});

document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
    }
});

dropdownItems.forEach(item => {
    item.addEventListener('click', () => {
        const value = item.getAttribute('data-value');
        const text = item.querySelector('span').textContent;
        const icon = item.querySelector('i').cloneNode(true);
        
        selectedPlatform = value;
        selectedText.textContent = text;
        
        // Update toggle button icon
        const toggleIcon = dropdownToggle.querySelector('i:first-child');
        toggleIcon.className = icon.className;
        
        dropdown.classList.remove('open');
    });
});

// Event Listeners
themeToggle.addEventListener('click', toggleTheme);
generateBtn.addEventListener('click', generateContent);
topicInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        generateContent();
    }
});

// Auto-resize textarea
topicInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

function createLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot loading';
    messageDiv.id = 'loadingMessage';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    
    for (let i = 0; i < 3; i++) {
        const circle = document.createElement('div');
        circle.className = 'typing-circle';
        typingIndicator.appendChild(circle);
    }
    
    contentDiv.appendChild(typingIndicator);
    messageDiv.appendChild(contentDiv);
    return messageDiv;
}

async function generateContent() {
    const topic = topicInput.value.trim();

    if (!topic) {
        return;
    }

    // Add user message
    addMessage(topic, 'user');
    topicInput.value = '';
    topicInput.style.height = 'auto';

    // Add loading message
    const loadingMessage = createLoadingMessage();
    chatMessages.appendChild(loadingMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic: topic,
                platform: selectedPlatform
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate content');
        }

        // Remove loading message and display the content
        loadingMessage.remove();
        displayContent(data);

    } catch (error) {
        // Remove loading message and show error
        loadingMessage.remove();
        addMessage('Sorry, there was an error generating content. Please try again.', 'bot');
    }
}

function addMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (typeof content === 'string') {
        contentDiv.innerHTML = content;
    } else {
        contentDiv.innerHTML = content;
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function displayContent(data) {
    // Create the content message
    let content = `
        <div class="markdown-body">
            <h2>${data.title}</h2>
            ${data.content}
            <div class="content-details">
                <p><strong>Hashtags:</strong> ${data.hashtags.join(' ')}</p>
                <p><strong>Suggested Emojis:</strong> ${data.emoji_suggestions}</p>
                <p><strong>Best Posting Times:</strong> ${data.best_posting_times}</p>
                <p><strong>Platform Tips:</strong> ${data.platform_specific_tips}</p>
            </div>
        </div>
    `;
    
    addMessage(content, 'bot');
}''')

    app.run(debug=True, port=5000) 