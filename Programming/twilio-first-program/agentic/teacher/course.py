from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import requests
import re
import time
import yt_dlp


app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key="AIzaSyDCTs2KxcKqRxDony-OPOeJs0tR34MOuoc")
SERPAPI_KEY = "ec7af2935cb905bbdbad818fc9319bfc93dc142806a0ece9708c03d6610cfb83"

def get_video_duration_yt_dlp(youtube_url):
    """Fetches the duration of a YouTube video using yt-dlp."""
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "force_generic_extractor": False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        duration = info.get("duration", 0)
        minutes = duration // 60
        seconds = duration % 60
        print(f"{minutes} min {seconds} sec ({duration} seconds)")
        return minutes,seconds
    
def get_yt_link(yt_name, max_retries=5):
    """Fetch a real YouTube video link under 10 minutes using SerpAPI, retrying up to 5 times."""
    search_query = f"{yt_name} site:youtube.com"

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": search_query,
        "api_key": SERPAPI_KEY,
        "num": 10
    }

    for attempt in range(max_retries):
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Attempt {attempt+1}: Error fetching data from SerpAPI.")
            time.sleep(2)  # Wait 2 seconds before retrying
            continue

        results = response.json()
        for result in results.get("organic_results", []):
            link = result.get("link", "")

            # Check if link is in the desired format
            if link.startswith("https://www.youtube.com/watch?v="):
                # Check if video is under 11 minutes
                minutes, seconds = get_video_duration_yt_dlp(link)
                if minutes < 15:
                    return link
                # print(link)  # Valid link
                # return link

        print(f"Attempt {attempt+1}: No valid video found, retrying...")
        time.sleep(1)  # Wait before retrying

    return "Failed"

@app.route('/')
def index():
    return render_template('course.html')

@app.route('/generate', methods=['POST'])
def generate():
    topic = request.form['topic']
    response = get_yt_link(topic)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(port=8933,debug=True)


