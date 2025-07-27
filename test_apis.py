from youtube_transcript_api import YouTubeTranscriptApi
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Test YouTube Transcript API
video_id = '5ays3LXekW0'
try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print("Transcript fetched successfully.")
    print(transcript)
except Exception as e:
    print(f"Error fetching transcript: {e}")

# Test Google Sheets API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/Eddie/Google Drive/Windsurf/Flash Card Creator/gen-lang-client-0392817992-a1ea34dfff26.json', scope)
client = gspread.authorize(creds)

try:
    sheet = client.create('Test Sheet')
    print("Google Sheet created successfully.")
except Exception as e:
    print(f"Error creating Google Sheet: {e}")
