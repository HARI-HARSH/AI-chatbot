from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini
genai.configure(api_key="AIzaSyALXYNsqWsmWQ0BWTzsxtrVI8gFv9tlTlI")

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
            "content": "The main content with proper formatting",
            "hashtags": ["relevant", "hashtags"],
            "emoji_suggestions": "Relevant emojis to use",
            "best_posting_times": "Suggested posting times",
            "platform_specific_tips": "Tips specific to the platform"
        }}
        
        Ensure the content is:
        - Engaging and conversational
        - Well-structured with clear sections
        - Uses appropriate line breaks
        - Includes relevant emojis
        - Optimized for {platform}"""

        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            f"{system_prompt}\n\nUser input: {topic}"
        )
        
        # Extract JSON from the response
        response_text = response.text
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        json_str = response_text[start_idx:end_idx]
        
        return jsonify(json.loads(json_str))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 