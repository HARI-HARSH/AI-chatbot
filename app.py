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

def format_hashtags(hashtags):
    """Format hashtags to include # and comma separation"""
    return [f"#{tag.strip()}" if not tag.startswith('#') else tag.strip() for tag in hashtags]

@app.route('/generate', methods=['POST'])
def generate_content():
    try:
        data = request.json
        topic = data.get('topic')
        platform = data.get('platform', 'general')

        if not topic:
            return jsonify({'error': 'Please enter a topic or idea first.'}), 400

        # Define content creation related keywords
        content_keywords = [
            'content', 'post', 'blog', 'article', 'social media', 'write', 'create',
            'instagram', 'facebook', 'twitter', 'linkedin', 'tiktok', 'youtube',
            'marketing', 'engagement', 'followers', 'audience', 'viral', 'trending',
            'hashtag', 'caption', 'story', 'reel', 'tweet', 'thread', 'video',
            'ideas', 'tips', 'strategy', 'brand', 'suggest', 'captions', 'travel'
        ]

        # Check if the topic is related to content creation
        is_content_related = any(keyword in topic.lower() for keyword in content_keywords)
        
        if not is_content_related:
            return jsonify({
                "title": "Content Creation Focus Only",
                "content": "I am a content recommender that only gives recommendations for content creation. Please ask me about creating content, social media posts, blogs, articles, or other content-related topics.",
                "is_content_related": False
            })

        system_prompt = """You are a social media content expert. Create engaging content based on the user's request. Strictly ask user to ask about content creation, if the user asks about anything else, say you are not able to help with that.
        
        IMPORTANT: Return ONLY a JSON object in this exact format (no markdown code blocks, no extra text):
        {
            "title": "Your Title Here",
            "content": "Your content here. Use regular quotes and escape special characters.",
            "hashtags": ["tag1", "tag2", "tag3"],
            "emoji_suggestions": "Your emoji suggestions here",
            "best_posting_times": "Your timing suggestions here",
            "platform_specific_tips": "Your platform tips here",
            "is_content_related": true
        }

        STRICT FORMATTING RULES:
        1. Use only regular quotes (") for JSON properties
        2. Escape all special characters properly
        3. No markdown code blocks or extra text
        4. Keep content simple and avoid complex formatting
        5. Use simple line breaks instead of special characters
        6. Include 5-10 relevant hashtags
        7. Keep responses concise and clear"""

        user_prompt = f"Topic: {topic}\nPlatform: {platform}\n\nCreate content following the exact JSON format above."

        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
        
        # Clean and parse the response
        try:
            # Clean up the response text
            response_text = response.text.strip()
            response_text = response_text.replace('```json', '').replace('```', '')
            response_text = response_text.replace('\n', ' ').replace('\r', '')
            
            # Find the JSON object
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No valid JSON found in response")
            
            json_str = response_text[start_idx:end_idx]
            
            # Parse and validate JSON
            data = json.loads(json_str)
            
            # Add the content_related flag
            data['is_content_related'] = True
            
            # Validate required fields
            required_fields = ['title', 'content']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Format hashtags only if content is related
            if 'hashtags' in data and isinstance(data['hashtags'], list):
                data['hashtags'] = format_hashtags(data['hashtags'])
            
            # Clean up content formatting
            if 'content' in data:
                data['content'] = data['content'].replace('\\n', '\n').replace('\\t', '\t')
            
            return jsonify(data)
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {str(e)}\nResponse text: {response_text}")
            return jsonify({
                'error': 'Failed to generate content. Please try again.',
                'details': str(e)
            }), 500
        except ValueError as e:
            print(f"Validation Error: {str(e)}\nResponse text: {response_text}")
            return jsonify({
                'error': 'Invalid content format. Please try again.',
                'details': str(e)
            }), 500
        except Exception as e:
            print(f"Processing Error: {str(e)}\nResponse text: {response_text}")
            return jsonify({
                'error': 'An error occurred while processing the content.',
                'details': str(e)
            }), 500

    except Exception as e:
        print(f"General Error: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred.',
            'details': str(e)
        }), 500

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
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Grand+Hotel&family=Quicksand:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="video-background">
        <video autoplay muted loop playsinline id="myVideo">
            <source src="bac.mp4" type="video/mp4">
        </video>
    </div>
    <div class="chat-container">
        <div class="chat-header">
            <div class="header-content">
                <img src="bot.png" alt="Content Generator Logo" class="header-logo">
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
        f.write('''/* Instagram-style dropdown */
.custom-dropdown {
    position: relative;
    min-width: 150px;
}

.dropdown-toggle {
    width: 100%;
    padding: 8px 16px;
    background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
    border: none;
    border-radius: 8px;
    color: white;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: 'Grand Hotel', cursive;
    font-size: 1.4rem;
    letter-spacing: 1px;
}

.dropdown-toggle:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

.dropdown-toggle .selected-text {
    font-family: 'Grand Hotel', cursive;
    font-size: 1.4rem;
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    margin-top: 0.5rem;
    background-color: var(--dropdown-bg);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s ease;
    z-index: 1000;
    overflow: hidden;
}

.custom-dropdown.open .dropdown-menu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.dropdown-item {
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    color: var(--text-color);
    transition: all 0.3s ease;
    font-family: 'Grand Hotel', cursive;
    font-size: 1.3rem;
}

.dropdown-item:hover {
    background: linear-gradient(45deg, rgba(240, 148, 51, 0.1) 0%, rgba(230, 104, 60, 0.1) 25%, rgba(220, 39, 67, 0.1) 50%, rgba(204, 35, 102, 0.1) 75%, rgba(188, 24, 136, 0.1) 100%);
}

.dropdown-item i {
    font-size: 1.2rem;
    width: 24px;
    text-align: center;
    background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Rest of the existing CSS */
:root {
    --primary-color: #833AB4; /* Instagram purple */
    --secondary-color: #C13584; /* Instagram magenta */
    --background-color: rgba(250, 250, 250, 0.85); /* Instagram light background */
    --chat-bg: rgba(255, 255, 255, 0.9);
    --user-message-bg: linear-gradient(45deg, rgba(131, 58, 180, 0.85), rgba(193, 53, 132, 0.85)); /* Instagram gradient */
    --bot-message-bg: rgba(255, 255, 255, 0.85);
    --text-color: #262626; /* Instagram text color */
    --border-color: #dbdbdb; /* Instagram border color */
    --success-color: #58C322; /* Instagram green */
    --error-color: #ed4956; /* Instagram red */
    --dropdown-bg: rgba(255, 255, 255, 0.9);
    --dropdown-hover: rgba(245, 245, 245, 0.9);
    --header-bg: linear-gradient(45deg, #405DE6, #5851DB, #833AB4, #C13584, #E1306C, #FD1D1D); /* Instagram brand gradient */
    --header-text: #ffffff;
    --input-bg: rgba(255, 255, 255, 0.9);
    --input-text: #262626;
    --input-placeholder: #8e8e8e; /* Instagram placeholder color */
}

[data-theme="dark"] {
    --primary-color: #833AB4;
    --secondary-color: #C13584;
    --background-color: rgba(0, 0, 0, 0.85); /* Instagram dark mode */
    --chat-bg: rgba(18, 18, 18, 0.9);
    --user-message-bg: linear-gradient(45deg, rgba(131, 58, 180, 0.85), rgba(193, 53, 132, 0.85));
    --bot-message-bg: rgba(38, 38, 38, 0.85);
    --text-color: #fafafa;
    --border-color: #262626;
    --dropdown-bg: rgba(38, 38, 38, 0.9);
    --dropdown-hover: rgba(54, 54, 54, 0.9);
    --header-bg: linear-gradient(45deg, #405DE6, #5851DB, #833AB4, #C13584, #E1306C, #FD1D1D);
    --header-text: #ffffff;
    --input-bg: rgba(38, 38, 38, 0.9);
    --input-text: #fafafa;
    --input-placeholder: #8e8e8e;
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
    max-width: 1000px;
    height: 95vh;
    background-color: rgba(255, 255, 255, 0.65);
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    margin: 20px;
    backdrop-filter: blur(8px);
}

.chat-header {
    padding: 1.2rem;
    background-color: var(--header-bg);
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    height: 48px;
}

.header-logo {
    width: 48px;
    height: 48px;
    object-fit: contain;
    margin-right: 0.5rem;
}

.header-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
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
    max-width: 85%;
    padding: 1.2rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    font-size: 1.25rem;
}

.message.user {
    align-self: flex-end;
    background: linear-gradient(45deg, rgba(131, 58, 180, 0.85), rgba(193, 53, 132, 0.85));
    color: white;
    border-bottom-right-radius: 4px;
}

.message.bot {
    align-self: flex-start;
    background-color: var(--bot-message-bg);
    border: 1px solid var(--border-color);
    border-bottom-left-radius: 4px;
}

.message-content {
    word-wrap: break-word;
    font-size: 1.25rem;
}

.message-content p {
    margin-bottom: 0.8rem;
    line-height: 1.6;
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
    padding: 1.2rem;
    border-top: 1px solid var(--border-color);
    background-color: var(--chat-bg);
    position: sticky;
    bottom: 0;
}

.input-wrapper {
    display: flex;
    gap: 0.8rem;
    align-items: flex-end;
    max-width: 100%;
}

textarea {
    flex: 1;
    min-height: 24px;
    max-height: 150px;
    padding: 12px 16px;
    border: 1px solid var(--border-color);
    border-radius: 20px;
    resize: none;
    font-size: 1.1rem;
    line-height: 1.5;
    font-family: 'Quicksand', sans-serif;
    background-color: var(--input-bg);
    color: var(--input-text);
    overflow-y: auto;
    width: calc(100% - 60px); /* Account for send button width + gap */
    transition: all 0.3s ease;
}

textarea:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 1px rgba(131, 58, 180, 0.1);
}

textarea::placeholder {
    color: var(--input-placeholder);
}

#generateBtn {
    width: 48px;
    height: 48px;
    min-width: 48px; /* Prevent shrinking */
    padding: 0;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(45deg, #405DE6, #5851DB, #833AB4, #C13584, #E1306C, #FD1D1D);
    color: white;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
}

#generateBtn:hover {
    opacity: 0.9;
    transform: scale(1.05);
}

#generateBtn:active {
    transform: scale(0.95);
}

/* Responsive adjustments */
@media (max-width: 600px) {
    .chat-input-container {
        padding: 0.8rem;
    }
    
    textarea {
        font-size: 1rem;
        padding: 10px 14px;
    }
    
    #generateBtn {
        width: 44px;
        height: 44px;
        min-width: 44px;
    }
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
    background: linear-gradient(45deg, #405DE6, #5851DB, #833AB4);
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
}

.video-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    overflow: hidden;
}

.video-background video {
    position: absolute;
    min-width: 100%;
    min-height: 100%;
    width: auto;
    height: auto;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    object-fit: cover;
}

.chat-header h1 {
    font-size: 1.8rem;
    margin: 0;
}

[data-theme="dark"] .chat-container {
    background-color: rgba(45, 45, 45, 0.65);
}

[data-theme="dark"] .message.user {
    background-color: rgba(74, 144, 226, 0.65);
}

[data-theme="dark"] .message.bot {
    background-color: rgba(61, 61, 61, 0.65);
}

[data-theme="dark"] textarea {
    background-color: rgba(45, 45, 45, 0.65);
}
''')

    # Run the app on 0.0.0.0 (all network interfaces)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 