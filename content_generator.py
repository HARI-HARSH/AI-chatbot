import google.generativeai as genai
import json
import emoji

# Configure Gemini
genai.configure(api_key="AIzaSyALXYNsqWsmWQ0BWTzsxtrVI8gFv9tlTlI")

def generate_content(topic, platform="general"):
    """Generate social media content based on user input and platform."""
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
    - Optimized for {platform}
    """

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            f"{system_prompt}\n\nUser input: {topic}"
        )
        
        # Extract JSON from the response
        response_text = response.text
        # Find the JSON part in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        json_str = response_text[start_idx:end_idx]
        
        return json.loads(json_str)
    except Exception as e:
        print(f"Error generating content: {str(e)}")
        return None

def format_content_for_display(content_data):
    """Format the generated content for display."""
    if not content_data:
        return
    
    print("\n" + "="*50)
    print(f"Title: {emoji.emojize(content_data['title'])}")
    print("="*50)
    
    print("\nContent:")
    print(emoji.emojize(content_data['content']))
    
    print("\nHashtags:")
    print(" ".join(content_data['hashtags']))
    
    print("\nSuggested Emojis:")
    print(content_data['emoji_suggestions'])
    
    print("\nBest Posting Times:")
    print(content_data['best_posting_times'])
    
    print("\nPlatform-Specific Tips:")
    print(content_data['platform_specific_tips'])
    print("="*50)

def main():
    print("Social Media Content Generator")
    print("="*50)
    
    # Get platform selection
    platforms = ["General", "Twitter/X", "LinkedIn", "Instagram", "Facebook"]
    print("\nAvailable platforms:")
    for i, platform in enumerate(platforms, 1):
        print(f"{i}. {platform}")
    
    while True:
        try:
            choice = int(input("\nSelect platform (1-5): "))
            if 1 <= choice <= 5:
                platform = platforms[choice-1].lower()
                break
            else:
                print("Please enter a number between 1 and 5")
        except ValueError:
            print("Please enter a valid number")
    
    # Get topic
    topic = input("\nEnter your topic or idea: ")
    
    print("\nGenerating content...")
    content_data = generate_content(topic, platform)
    
    if content_data:
        format_content_for_display(content_data)
        
        # Save to file option
        save = input("\nWould you like to save this content to a file? (y/n): ")
        if save.lower() == 'y':
            filename = f"content_{platform}_{topic.replace(' ', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Title: {content_data['title']}\n\n")
                f.write(f"Content:\n{content_data['content']}\n\n")
                f.write(f"Hashtags: {' '.join(content_data['hashtags'])}\n\n")
                f.write(f"Suggested Emojis: {content_data['emoji_suggestions']}\n\n")
                f.write(f"Best Posting Times:\n{content_data['best_posting_times']}\n\n")
                f.write(f"Platform-Specific Tips:\n{content_data['platform_specific_tips']}")
            print(f"\nContent saved to {filename}")

if __name__ == "__main__":
    main() 