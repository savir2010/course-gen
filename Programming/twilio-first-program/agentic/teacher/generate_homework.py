from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import youtube_transcript_api

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key="AIzaSyDCTs2KxcKqRxDony-OPOeJs0tR34MOuoc")

def get_transcript(youtube_url):
    """Extract transcript from YouTube video."""
    try:
        video_id = youtube_url.split("v=")[1].split("&")[0]
        transcript = youtube_transcript_api.YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry["text"] for entry in transcript])
        return transcript_text
    except:
        return None

def generate_homework(transcript_text):
    """Generate a coding homework problem and its solution using Gemini."""
    if not transcript_text:
        return "No transcript available."

    prompt = f"""
    Based on this transcript from a programming video, create a coding homework problem and its solution in code:
    
    Transcript:
    {transcript_text[:2000]}  # Limiting to avoid excessive token usage
    - Homework should be slightly challenging.
    - The output should be fully in Python code.
    - The problem should be related to the concepts discussed in the transcript.
    - Include both the problem statement (as comments) and the solution in executable Python code.
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    return response.text

@app.route('/')
def index():
    return render_template('homework.html')

@app.route('/generate_homework', methods=['POST'])
def generate():
    youtube_url = request.form['youtube_url']
    
    transcript_text = get_transcript(youtube_url)
    
    if not transcript_text:
        return jsonify({"code": "# Error: Could not retrieve transcript."})
    
    homework_code = generate_homework(transcript_text)
    
    return jsonify({"code": homework_code})

if __name__ == '__main__':
    app.run(port=2152,debug=True)
