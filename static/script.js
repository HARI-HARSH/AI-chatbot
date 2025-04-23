// API Configuration
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
        contentDiv.innerHTML = `<p>${content}</p>`;
    } else {
        contentDiv.appendChild(content);
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function displayContent(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    
    let content = '<div class="message-content">';
    
    if (!data.is_content_related) {
        // For non-content-related queries, only show the basic message
        content += `
            <h2>${data.title}</h2>
            <p>${data.content}</p>
        `;
    } else {
        // For content-related queries, show all details
        content += `
            <h2>${data.title}</h2>
            <p>${data.content}</p>
            <div class="content-details">
                <p><strong>Hashtags:</strong> ${data.hashtags.join(' ')}</p>
                <p><strong>Suggested Emojis:</strong> ${data.emoji_suggestions}</p>
                <p><strong>Best Posting Times:</strong> ${data.best_posting_times}</p>
                <p><strong>Platform Tips:</strong> ${data.platform_specific_tips}</p>
            </div>
        `;
    }
    
    content += '</div>';
    messageDiv.innerHTML = content;
    
    // Add message to chat
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}