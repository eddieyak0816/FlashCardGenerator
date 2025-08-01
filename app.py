from flask import Flask, render_template, request, jsonify, send_file
from flashcard_generator import extract_video_id, fetch_transcript, create_google_sheet, create_anki_file
import google.generativeai as genai
import time
import os
import traceback
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # Preserve order of keys in JSON response

# Configure the Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple rate limiting implementation
last_request_time = 0
MIN_REQUEST_INTERVAL = 60  # minimum seconds between requests

def generate_flashcards_with_backoff(content):
    global last_request_time
    
    current_time = time.time()
    time_since_last_request = current_time - last_request_time
    
    if time_since_last_request < MIN_REQUEST_INTERVAL:
        wait_time = MIN_REQUEST_INTERVAL - time_since_last_request
        return {'error': f'Please wait {int(wait_time)} seconds before making another request'}, True
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = """Please create flashcards based on the provided text, with the following comprehensive guidelines:
                   1. Accuracy is Paramount
                   - Ensure 100% factual accuracy of the content
                   - Double-check all information before including

                   2. Make Learning an Adventure
                   - Write answers that are engaging for a 7th-grade student
                   - Sprinkle in age-appropriate humor
                   - Include interesting facts, quirky analogies, or fun twists
                   - Keep the tone conversational and relatable

                   3. Leverage Examples and Samples
                   - When possible, include concrete, real-world examples
                   - Use analogies that help visualize abstract concepts
                   - Provide specific, memorable illustrations
                   - Examples should:
                     * Clarify the concept
                     * Make the information more memorable
                     * Help students connect the idea to their own experiences

                   4. Humor and Engagement Techniques
                   - Use playful comparisons
                   - Include witty side comments
                   - Make unexpected connections
                   - Employ mild, school-appropriate jokes

                   Example Formatting:
                   Bad Example: "Photosynthesis is a process where plants make food."
                   Good Example: "Photosynthesis is like a plant's personal solar-powered kitchen! 🌱 Imagine a maple tree turning sunlight into lunch - just like you might use a microwave, but way cooler. For instance, a single oak leaf can create enough energy to power a tiny LED light for hours! 💡"

                   Bad Example: "Gravity is a force that pulls objects together."
                   Good Example: "Gravity is Earth's invisible superhero that keeps everything from floating away! 🦸‍♀️ Example: Drop an apple, and it always falls down - never sideways or up. Just ask Isaac Newton, who supposedly got his big idea when an apple bonked him on the head! 🍎"

                   Content to transform into awesome, example-rich flashcards:"""
        response = model.generate_content(f"{prompt}\n\nContent:\n{content}")
        last_request_time = time.time()
        flashcards_text = response.text
        # Parse the flashcards text into a list of tuples
        flashcards = []
        current_question = None
        
        logger.info("Generated Flashcards Text:")
        logger.info(flashcards_text)
        
        for line in flashcards_text.split('\n'):
            line = line.strip()
            if '**Front:**' in line or 'Front:' in line:
                clean_line = line.replace('*', '').strip()
                parts = clean_line.split('Front:', 1)
                if len(parts) > 1:
                    current_question = parts[1].strip()
            elif ('**Back:**' in line or 'Back:' in line) and current_question:
                clean_line = line.replace('*', '').strip()
                parts = clean_line.split('Back:', 1)
                if len(parts) > 1:
                    answer = parts[1].strip()
                    if current_question and answer:
                        flashcards.append([current_question, answer])
                    current_question = None
        
        logger.info("Parsed Flashcards:")
        logger.info(flashcards)
        
        return flashcards, False
    except Exception as e:
        logger.error(f"Error generating flashcards: {str(e)}")
        logger.error(traceback.format_exc())
        return {'error': f"Failed to generate flashcards: {str(e)}"}, True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():

    # Debug logging for incoming requests
    print('--- /generate endpoint called ---')
    print('Request method:', request.method)
    print('Request headers:', dict(request.headers))
    print('Request data:', request.data)
    try:
        data = request.get_json(force=True, silent=True)
        print('Parsed JSON:', data)
        input_type = data.get('input_type') if data else None
        content = data.get('content') if data else None
        export_format = data.get('export_format', 'sheets') if data else 'sheets'

        if not content:
            print('No content provided')
            return jsonify({'error': 'No content provided'}), 400

        # Get transcript if URL provided
        if input_type == 'url':
            video_id = extract_video_id(content)
            if not video_id:
                print('Invalid YouTube URL')
                return jsonify({'error': 'Invalid YouTube URL'}), 400
            content = fetch_transcript(video_id)
            if not content:
                print('Could not fetch video transcript')
                return jsonify({'error': 'Could not fetch video transcript'}), 400

        # Generate flashcards
        flashcards, is_error = generate_flashcards_with_backoff(content)
        if is_error:
            return jsonify(flashcards), 500

        result = {'flashcards': flashcards}

        # Export based on format
        if export_format in ['sheets', 'both']:
            sheets_url = create_google_sheet(flashcards, 'Generated_Flashcards')
            if sheets_url:
                result['sheets_url'] = sheets_url

        if export_format in ['anki', 'both']:
            anki_file = create_anki_file(flashcards, 'Generated_Flashcards')
            if anki_file:
                result['anki_file'] = os.path.basename(anki_file)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in generate endpoint: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/export')
def export():
    filename = request.args.get('file')
    if not filename:
        return 'No file specified', 400
    
    # Ensure the file is from our directory and exists
    file_path = os.path.join(os.getcwd(), filename)
    if not os.path.exists(file_path):
        return 'File not found', 404
    
    return send_file(file_path, 
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
