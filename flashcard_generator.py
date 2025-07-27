# Placeholder function for AI-powered flashcard generation
# This function will use an AI model to generate flashcards from a transcript

# Default prompt for generating flashcards for a 7th grade geography student
def get_custom_prompt():
    default_prompt = """<s>You are a friendly teacher creating flashcards about educational content. Your students are curious learners who love interesting facts, cool comparisons, and memorable examples. Make learning fun by including:
- Real-world comparisons they can relate to
- Interesting "Did you know?" facts
- Fun emoji that help remember the content
- Clear, simple language
- Connections to things they know (movies, sports, food, etc.)
</s>

<input>I will provide you with educational content that needs to be transformed into flashcards.</input>

<output_format>
Create each flashcard in this exact format:
{
    "front": "Question goes here",
    "back": "Answer goes here"
}
</output_format>

<guidelines>
1. Question Types to Include:
   - Fundamental Concepts: "What is...?", "How does... work?"
   - Key Definitions: "Define...", "Explain the meaning of..."
   - Practical Applications: "Where can you use...?", "Why is this important?"
   - Comparative Analysis: "How is... different from...?", "What makes... unique?"
   - Cause and Effect: "What happens when...?", "Why does... occur?"

2. Make it Memorable:
   - Use real-world analogies and comparisons
   - Include surprising or counterintuitive facts
   - Connect to common experiences or interests
   - Add visual or mnemonic memory aids

3. Keep it Simple:
   - Use clear, straightforward language
   - Break down complex ideas
   - Focus on the most interesting and essential parts
   - Avoid unnecessary technical jargon

4. Make it Relevant:
   - Provide context for why the information matters
   - Link to broader concepts or real-life applications
   - Use examples that spark curiosity
   - Highlight practical or interesting aspects

5. Avoid:
   - Overly complex or technical explanations
   - Excessive details that distract from core concepts
   - Dry, academic language
   - Information overload
</guidelines>

<examples>
{
    "front": "How can AI help you be more creative in visual storytelling?",
    "back": "AI can assist in generating character descriptions, creating consistent character attributes, and producing video prompts that help bring creative ideas to life across different scenes."
}

{
    "front": "How can AI tools enhance the video creation process?",
    "back": "AI can help generate video prompts, analyze visual references, suggest character attributes, and create animation scenes with consistent character representation."
}
</examples>

<task>
1. Read the content carefully
2. Create 5-10 engaging flashcards that:
   - Focus on the most interesting facts
   - Use comparisons kids understand
   - Include relevant emoji
   - Make learning fun and memorable
3. Format each card properly
4. Focus on information that would interest a curious learner
</task>

<content_placeholder>Content to transform into flashcards will be provided here.</content_placeholder>"""
    
    print("\nCurrent prompt:")
    print(default_prompt)
    
    while True:
        change_prompt = input("\nWould you like to customize this prompt? (yes/no, hit Enter = No): ").lower()
        if change_prompt == 'yes':
            return input("\nPlease enter your custom prompt: ")
        elif change_prompt == 'no' or change_prompt == '':  # Enter = No
            return default_prompt
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

import os
import google.generativeai as genai
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import csv
import json
import re

# Load environment variables from .env file
load_dotenv()

# Retrieve the Gemini API key from environment variables
gemini_api_key = os.getenv('GEMINI_API_KEY')

# Configure the Gemini API with the API key
genai.configure(api_key=gemini_api_key)

# Function to generate flashcards using the Gemini API
def generate_flashcards(content):
    """Generate flashcards from content using Google's Generative AI"""
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Set up the model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Get the prompt
        prompt = get_custom_prompt()
        
        # Replace content placeholder with actual content
        prompt = prompt.replace('<content_placeholder>Content to transform into flashcards will be provided here.</content_placeholder>', 
                              f'<content>{content}</content>')
        
        # Generate the response
        response = model.generate_content(prompt)
        
        if response.text:
            print("\nGenerated Response:")
            print(response.text)
            
            # Clean up the response text
            cleaned_text = response.text
            # Replace smart quotes and apostrophes
            cleaned_text = cleaned_text.replace('"', '"').replace('"', '"')
            cleaned_text = cleaned_text.replace(''', "'").replace(''', "'")
            # Remove any line breaks within JSON objects
            cleaned_text = re.sub(r'\n\s*(?=(?:[^"]*"[^"]*")*[^"]*$)', ' ', cleaned_text)
            
            # Find all JSON objects (single curly brace format)
            flashcards = []
            pattern = r'\{[^}]+\}'
            matches = re.finditer(pattern, cleaned_text)
            
            for match in matches:
                try:
                    # Remove any double curly braces
                    card_text = match.group().strip().replace('{{', '{').replace('}}', '}')
                    card = json.loads(card_text)
                    if 'front' in card and 'back' in card:
                        # Clean up the text
                        front = card['front'].strip()
                        back = card['back'].strip()
                        # Replace any remaining smart quotes or problematic characters
                        front = front.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
                        back = back.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
                        flashcards.append({
                            'front': front,
                            'back': back
                        })
                except json.JSONDecodeError as e:
                    print(f"Failed to parse card: {card_text}")
                    print(f"Error: {str(e)}")
            
            print(f"\nTotal flashcards found: {len(flashcards)}")
            
            if not flashcards:
                print("\nNo flashcards were successfully parsed. Please check the generated response format.")
                return None
                
            return flashcards
            
        else:
            print("\nNo response generated from the AI model.")
            return None
            
    except Exception as e:
        print(f"\nError generating flashcards: {str(e)}")
        return None

# Function to fetch transcript from a YouTube video
def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # Combine transcript entries into a single string
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        print("An error occurred while fetching the transcript:", e)
        return None

# Function to create a Google Sheet and populate it with flashcards
def create_google_sheet(flashcards, keyword):
    """Create a Google Sheet with the flashcards"""
    try:
        # Load credentials from the service account file
        creds = service_account.Credentials.from_service_account_file(
            'gen-lang-client-0392817992-a1ea34dfff26.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets',
                   'https://www.googleapis.com/auth/drive']
        )

        # Create the Sheets API service
        sheets_service = build('sheets', 'v4', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)

        # Create a new spreadsheet
        spreadsheet = {
            'properties': {
                'title': f"FC_{keyword}"
            }
        }
        spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')

        # Prepare the data
        values = [['Front', 'Back']]  # Header row
        for card in flashcards:
            values.append([card['front'], card['back']])

        # Update the spreadsheet with the flashcard data
        body = {
            'values': values
        }
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Sheet1!A1',
            valueInputOption='RAW',
            body=body
        ).execute()

        # Get the spreadsheet URL
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        print(f"\nGoogle Sheet created: {spreadsheet_url}")
        
        # Share the sheet
        share_google_sheet(spreadsheet_id, "eddie0816@gmail.com")
        
        return spreadsheet_url

    except Exception as e:
        print(f"Error creating Google Sheet: {str(e)}")
        return None

# Function to share the Google Sheet with a specific email
def share_google_sheet(spreadsheet_id, user_email):
    drive_service = build('drive', 'v3', credentials=service_account.Credentials.from_service_account_file(
        'gen-lang-client-0392817992-a1ea34dfff26.json',
        scopes=["https://www.googleapis.com/auth/drive"]
    ))
    permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': user_email
    }
    drive_service.permissions().create(
        fileId=spreadsheet_id,
        body=permission,
        fields='id'
    ).execute()

# Function to create an Anki CSV file
def create_anki_file(flashcards, keyword):
    """Create a CSV file for Anki import"""
    try:
        # Create filename using the keyword
        filename = os.path.join(os.getcwd(), f"FC_{keyword}.csv")
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write flashcards directly without header
            for card in flashcards:
                writer.writerow([card['front'], card['back']])
        
        print(f"\nFlashcards saved to: {filename}")
        return filename
    except Exception as e:
        print(f"Error creating Anki file: {str(e)}")
        return None

# Function to extract video ID from a YouTube URL
def extract_video_id(url):
    video_id = url.split('v=')[-1]
    return video_id

# Function to get video title using YouTube Data API
def get_video_title(video_id):
    """Get video title using YouTube Data API"""
    try:
        # Load credentials from the service account file
        creds = service_account.Credentials.from_service_account_file(
            'gen-lang-client-0392817992-a1ea34dfff26.json',
            scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
        )

        # Build the YouTube API client
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Call the videos().list method to retrieve video details
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()

        # Get the video title from the response
        if response['items']:
            return response['items'][0]['snippet']['title']
        else:
            return None
            
    except Exception as e:
        print(f"Error getting video title from YouTube API: {str(e)}")
        return None

# Function to extract main topic keywords from video title
def extract_keywords(title):
    """Extract short, meaningful keywords from video title"""
    # Common words to filter out
    common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was', 'were', 'will', 'with', 'by', 'of', 'using', 'how', 'what', 'why', 'when', 'where', 'who']
    
    # Special cases for common topics
    lower_title = title.lower()
    if 'llama' in lower_title:
        return 'Llama'
    elif 'qwq' in lower_title or 'reasoning' in lower_title:
        return 'QWQ'
    elif 'machine learning' in lower_title or 'ml' in lower_title:
        return 'ML'
    elif 'artificial intelligence' in lower_title or 'ai' in lower_title:
        return 'AI'
    elif 'programming' in lower_title or 'coding' in lower_title:
        return 'Code'
    
    # Get main words
    words = title.split()
    keywords = [word for word in words if word.lower() not in common_words and len(word) > 1]
    
    # Take first meaningful word, or first two if they're short
    if not keywords:
        return 'Topic'
    elif len(keywords[0]) <= 3 and len(keywords) > 1:
        return f"{keywords[0]}_{keywords[1]}"[:8]
    else:
        return keywords[0][:8]

# Main function
def main():
    try:
        print("\n=== YouTube Flashcard Generator ===")
        print("Generate flashcards from YouTube videos or custom text!")
        
        # Input type selection
        print("\nChoose input type:")
        print("1. YouTube Video")
        print("2. Custom Text")
        
        while True:
            try:
                input_choice = input("Enter your choice (1/2): ").strip()
                
                if input_choice == '1':
                    # YouTube Video Input
                    video_url = input("\nEnter the YouTube video URL: ").strip()
                    
                    # Extract video ID
                    video_id = extract_video_id(video_url)
                    if not video_id:
                        print("Invalid YouTube URL. Please try again.")
                        continue
                    
                    # Get video title using YouTube Data API
                    video_title = get_video_title(video_id)
                    if video_title:
                        print(f"\nVideo Title: {video_title}")
                        # Extract keywords for file naming
                        keyword = extract_keywords(video_title)
                    else:
                        keyword = input("Could not fetch video title. Please enter a topic keyword: ").strip()
                    
                    # Fetch transcript
                    transcript = fetch_transcript(video_id)
                    if not transcript:
                        print("Could not fetch transcript. Please try another video.")
                        continue
                    
                    break
                
                elif input_choice == '2':
                    # Custom Text Input (multi-line)
                    print("\nPaste the text for flashcard generation. When finished, type END on a new line and press Enter:")
                    lines = []
                    while True:
                        line = input()
                        if line.strip() == "END":
                            break
                        lines.append(line)
                    transcript = "\n".join(lines)
                    keyword = input("Enter a topic keyword: ").strip() or "Custom Text Flashcards"
                    
                    if not transcript:
                        print("Text cannot be empty. Please try again.")
                        continue
                    
                    break
                
                else:
                    print("Invalid choice. Please enter 1 or 2.")
            
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return
        
        # Generate flashcards
        # Clean up the transcript or custom text before generating flashcards
        cleaned_content = ' '.join(transcript.split())
        flashcards = generate_flashcards(cleaned_content)
        
        if not flashcards:
            print("No flashcards could be generated.")
            return
        
        # Export preferences
        print("\nExport Options:")
        print("1. Google Sheets")
        print("2. Anki")
        print("3. Both")
        
        while True:
            export_choice = input("Choose export option (1/2/3): ").strip()
            
            if export_choice in ['1', '2', '3']:
                break
            print("Invalid choice. Please enter 1, 2, or 3.")
        
        # Perform export based on choice
        if export_choice in ['1', '3']:
            create_google_sheet(flashcards, keyword)
        
        if export_choice in ['2', '3']:
            create_anki_file(flashcards, keyword)
        
        print("\n✨ Flashcard generation complete! ✨")

    except UnicodeEncodeError:
        print("\nError: Unicode encoding issue. Please try running the script in a different terminal or command prompt.")

if __name__ == "__main__":
    while True:
        main()
        again = input("\nWould you like to generate more flashcards? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            print("Goodbye!")
            break
