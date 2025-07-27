from youtube_transcript_api import YouTubeTranscriptApi

# Video ID extracted from the URL
video_id = 'VihYdlFIJaw'

try:
    # Fetch the transcript
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    
    # Print out the transcript
    for entry in transcript:
        print(f"{entry['start']:.2f} - {entry['start'] + entry['duration']:.2f}: {entry['text']}")

except Exception as e:
    print("An error occurred:", e)
