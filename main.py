# Main entry point for the Flash Card Creator application

import logging
import absl.logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Initialize logging
logging.basicConfig(level=logging.INFO)
absl.logging.set_verbosity('info')

from youtube_transcript import get_transcript_from_url
from flashcard_generator import generate_flashcards
from anki_integration import get_anki_decks, add_flashcards_to_deck
from tabulate import tabulate

# Function to create HTML file with flashcards
def create_html_flashcards(flashcards, video_title=None):
    html_content = """<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Flashcards</title>
    <style>
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Flashcards</h1>
    <h2>{}</h2>
    <table>
        <thead>
            <tr>
                <th>Front</th>
                <th>Back</th>
            </tr>
        </thead>
        <tbody>
""".format(video_title if video_title else "Untitled")
    for card in flashcards:
        html_content += f"<tr><td>{card[0]}</td><td>{card[1]}</td></tr>\n"
    html_content += """        </tbody>
    </table>
</body>
</html>"""

    with open("flashcards.html", "w") as file:
        file.write(html_content)
    print("Flashcards have been written to flashcards.html")

# Function to create and populate a Google Sheet with flashcards
def create_google_sheet(flashcards, video_title=None):
    # Define the scope
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Add your credentials file
    creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/Eddie/Google Drive/Windsurf/Flash Card Creator/gen-lang-client-0392817992-a1ea34dfff26.json', scope)
    client = gspread.authorize(creds)

    # Create sheet title using video title if available
    title = f'Flashcards - {video_title}' if video_title else 'Untitled Flashcards'
    
    # Create a new spreadsheet with the title
    sheet = client.create(title)
    worksheet = sheet.get_worksheet(0)

    # Populate the sheet with flashcards
    worksheet.append_row(['Front', 'Back'])  # Header
    for flashcard in flashcards:
        worksheet.append_row([flashcard[0], flashcard[1]])

    print("Flashcards have been added to Google Sheets.")

# Function to handle user input and process flashcards
def process_input():
    user_choice = input("Enter 1 to provide YouTube URL or 2 to paste transcript: ")
    
    video_title = None
    if user_choice == "1":
        video_url = input("Enter YouTube video URL: ")
        result = get_transcript_from_url(video_url)
        transcript = result['transcript']
        video_title = result['title']
        print(f"\nVideo Title: {video_title}")
        print(f"Transcript length: {len(transcript)} characters")
        
    elif user_choice == "2":
        transcript = input("Paste the transcript here: ")
        video_title = input("Enter a title for these flashcards: ")
        print(f"Transcript length: {len(transcript)} characters")
    else:
        print("Invalid choice. Please enter 1 or 2.")
        return

    # Prompt for flashcard generation
    prompt = input("Enter custom prompt for flashcard generation (or press Enter to use default): ")
    if not prompt:
        prompt = "Default prompt for flashcard generation"
    
    # Generate flashcards
    flashcards = generate_flashcards(transcript)
    
    if flashcards:
        # Export options
        print("\nExport Options:")
        print("1. Export to Google Sheets")
        print("2. Export to Anki")
        print("3. Export to HTML")
        print("4. Export to all formats")
        
        export_choice = input("Choose export format (1-4): ")
        
        if export_choice in ['1', '4']:
            create_google_sheet(flashcards, video_title)
        
        if export_choice in ['2', '4']:
            add_flashcards_to_deck(flashcards, "Flash Card Creator", video_title)
            
        if export_choice in ['3', '4']:
            create_html_flashcards(flashcards, video_title)

        print("\n✨ Flashcard generation complete! ✨")

if __name__ == "__main__":
    print("Welcome to the Flash Card Creator!")
    process_input()
