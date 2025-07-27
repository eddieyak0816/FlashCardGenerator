from googleapiclient.discovery import build
import re
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import logging
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Function to extract transcript from YouTube video
# Note: This is a placeholder function. The actual implementation requires handling YouTube API authentication and response parsing.
def get_transcript_from_url(video_url):
    # Extract video ID from URL
    video_id = extract_video_id(video_url)
    
    if not video_id:
        raise ValueError("Invalid YouTube URL: Unable to extract video ID.")

    try:
        # Alternative method to get video title
        video_title = scrape_video_title(video_url)
        
        # Get transcript
        transcript = get_transcript(video_id)
        
        return {
            'title': video_title,
            'transcript': transcript,
            'video_id': video_id
        }
        
    except Exception as e:
        logging.error(f"Error processing video {video_url}: {str(e)}")
        raise

# Enhanced helper function to extract video ID from URL
def extract_video_id(url):
    # Regular expression to match YouTube video IDs
    video_id_match = re.search(r"(?<=v=)[^&#]+|(?<=be/)[^&#]+", url)
    if video_id_match:
        return video_id_match.group(0)
    return None

# Function to retrieve transcript using youtube-transcript-api
def get_transcript(video_id):
    try:
        logging.debug(f"Fetching transcript for video ID: {video_id}")
        # Fetch the transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # Combine the transcript into a single string
        transcript = " ".join([entry['text'] for entry in transcript_list])
        logging.debug(f"Transcript fetched successfully for video ID: {video_id}")
        return transcript
    except Exception as e:
        logging.error(f"Failed to retrieve transcript for video ID: {video_id}: {e}")
        raise ValueError(f"Failed to retrieve transcript: {e}")

# Function to scrape transcript from YouTube video
# Note: This is a basic implementation and may not work for all videos, especially those without captions.
def scrape_transcript_from_url(video_url):
    # Fetch the video page
    response = requests.get(video_url)
    if response.status_code != 200:
        raise ValueError("Failed to retrieve video page.")

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the transcript in the page (this is a placeholder logic)
    # You may need to adjust this based on the actual structure of the page
    transcript_div = soup.find('div', class_='transcript')  # Placeholder class name
    if not transcript_div:
        raise ValueError("Transcript not found on the page.")

    # Extract the text
    transcript = transcript_div.get_text(separator=" ", strip=True)
    return transcript

def scrape_video_title(url):
    try:
        # Use requests to fetch the page and BeautifulSoup to parse title
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').string
        # Remove " - YouTube" from the end of the title
        return title.replace(" - YouTube", "").strip() if title else "Unknown Title"
    except Exception as e:
        logging.error(f"Could not scrape video title: {e}")
        return "Unknown Title"

# Replace get_transcript_from_url with scrape_transcript_from_url in the main logic if needed
def main():
    video_url = input("Enter the YouTube video URL: ")
    video_id = extract_video_id(video_url)
    if not video_id:
        print("Invalid YouTube URL: Unable to extract video ID.")
        return
    try:
        result = get_transcript_from_url(video_url)
        print(f"Title: {result['title']}")
        print(result['transcript'])
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
