from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import re

# Initialize Flask app
app = Flask(__name__)

# Set up Google Gemini API
genai.configure(api_key="GEMINI API KEY")

def get_video_id(url):
    match = re.search(r"(?:v=|youtu.be/)([\w-]+)", url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        return str(e)

def split_transcript(transcript, interval=300):
    segments, current_text, current_time = [], "", 0
    for entry in transcript:
        start, text = entry['start'], entry['text']
        if start - current_time >= interval:
            segments.append(current_text.strip())
            current_text, current_time = "", start
        current_text += " " + text
    if current_text:
        segments.append(current_text.strip())
    return segments

def generate_question(text):
    prompt = (
        f"Generate a multiple-choice quiz question based on the following content:\n{text}\n"
        "Format the output **exactly** as follows:\n\n"
        "Question: <Your question here>\n"
        "(A) <Option A>\n"
        "(B) <Option B>\n"
        "(C) <Option C>\n"
        "(D) <Option D>\n"
        "Correct Answer: <Correct option number (1, 2, 3, or 4)>\n\n"
        "Ensure:\n"
        "- There are exactly 4 answer choices.\n"
        "- The correct answer is listed at the end in the correct format."
        "Correct answer should be in format with just number For example:1"
        "Correct answer should never me a letter only numbers."
    )
    response = genai.GenerativeModel("gemini-pro").generate_content(prompt)

    if response and response.text:
        lines = [line.strip() for line in response.text.strip().split("\n") if line.strip()]
        
        if len(lines) >= 6:  # Ensure we have enough lines
            question = lines[0]
            choices = lines[1:5]  # Extract exactly 4 choices
            correct_answer = lines[-1]  # Assume last line contains the correct answer
            print(correct_answer)
            match = re.search(r"\d+", correct_answer)  # Finds the first digit in the string
            answer = int(match.group()) if match else None
            print(answer) 
            return {"question": question, "choices": choices, "correct": answer}
        
    return {"question": "Error generating question.", "choices": [], "correct": ""}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    data = request.json
    video_url = data.get('video_url')
    
    if not video_url:
        return jsonify({'error': 'Missing video URL'}), 400
    
    video_id = get_video_id(video_url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    transcript = get_transcript(video_id)
    if isinstance(transcript, str):
        return jsonify({'error': transcript}), 400
    
    segments = split_transcript(transcript)
    quiz = [generate_question(segment) for segment in segments]
    
    return jsonify({'quiz': quiz})

if __name__ == '__main__':
    app.run(port=1222,debug=True)
