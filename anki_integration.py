import requests
import json
import os
import csv

# Function to get list of decks from Anki
# Requires AnkiConnect to be running

def get_anki_decks():
    """Get list of available Anki decks"""
    try:
        response = requests.post('http://localhost:8765', json={
            "action": "deckNames",
            "version": 6
        })
        return response.json().get('result', [])
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Anki. Please ensure Anki is running with AnkiConnect installed.")
        return []

# Function to add flashcards to a specific Anki deck
def add_flashcards_to_deck(flashcards, deck_name, video_title=None):
    """
    Create a CSV file for Anki import with just front and back columns
    """
    # Use video title if available, otherwise use deck name
    title = video_title if video_title else "Untitled Flashcards"
    
    # Create filename with sanitized title
    safe_title = "".join(x for x in title if x.isalnum() or x in (' ', '-', '_')).strip()
    if len(safe_title) > 50:
        safe_title = safe_title[:50] + "..."
    
    filename = f'Flashcards - {safe_title}.csv'
    
    # Get the absolute path of the file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(['Front', 'Back'])
            # Write flashcards
            for card in flashcards:
                writer.writerow([card['front'], card['back']])
        
        print(f"\nAnki import file created at:")
        print(filepath)
        print("\nTo import into Anki:")
        print("1. Open Anki")
        print("2. Click 'File' -> 'Import'")
        print("3. Select this CSV file")
        print("4. Ensure the field separator is set to comma")
        print("5. Map 'Front' to Front field and 'Back' to Back field")
        print("6. Click 'Import'")
        return True
        
    except Exception as e:
        print(f"\nError creating Anki import file: {str(e)}")
        return False
