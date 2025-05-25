from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging

app = Flask(__name__)
# Configure logging
logging.basicConfig(level=logging.INFO)
app.logger.info('Starting Flask app...')

# Restrict CORS to Netlify frontend (update with your Netlify URL)
CORS(app, resources={r"/api/*": {"origins": ["https://your-ssc-app.netlify.app", "http://localhost:3000"]}})

# Hugging Face Inference API configuration
HF_API_TOKEN = os.environ.get('HF_API_TOKEN')  # Set in Render environment variables
SUMMARIZATION_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
QUIZ_GEN_URL = "https://api-inference.huggingface.co/models/distilgpt2"

# Mock news data (replace with NewsAPI.org in production)
mock_news = [
    {
        "title": "Operation Sindoor: India's Response to Terrorism",
        "content": "On May 6-7, 2025, Indian forces conducted Operation Sindoor in retaliation to the Pahalgam attack, targeting terrorist bases.",
        "source": "Utkarsh Classes",
        "date": "2025-05-07"
    },
    {
        "title": "8th Pay Commission Approved",
        "content": "The Union government approved the 8th Pay Commission on February 2, 2025, to revise salaries and pensions for government employees.",
        "source": "Indian Express",
        "date": "2025-02-02"
    }
]

@app.route('/api/news', methods=['GET'])
def get_news():
    app.logger.info('Fetching news...')
    # For production, integrate NewsAPI.org
    """
    api_key = os.environ.get('NEWSAPI_KEY')
    if not api_key:
        app.logger.error('NewsAPI key not configured')
        return jsonify({"error": "NewsAPI key not configured"}), 500
    url = f"https://newsapi.org/v2/everything?q=india+ssc&apiKey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json()['articles']
        formatted_articles = [
            {
                "title": article["title"],
                "content": article["content"] or article["description"],
                "source": article["source"]["name"],
                "date": article["publishedAt"]
            } for article in articles[:5]
        ]
        return jsonify(formatted_articles)
    except Exception as e:
        app.logger.error(f"NewsAPI request failed: {str(e)}")
        return jsonify({"error": f"Failed to fetch news: {str(e)}"}), 500
    """
    return jsonify(mock_news)

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data.get('text', '')
    if not text:
        app.logger.warning('No text provided for summarization')
        return jsonify({"error": "No text provided"}), 400
    try:
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        payload = {"inputs": text, "parameters": {"max_length": 100, "min_length": 30}}
        response = requests.post(SUMMARIZATION_URL, headers=headers, json=payload)
        response.raise_for_status()
        summary = response.json()[0]['summary_text']
        app.logger.info('Summarization successful')
        return jsonify({"summary": summary})
    except Exception as e:
        app.logger.error(f"Summarization failed: {str(e)}")
        return jsonify({"error": f"Summarization failed: {str(e)}"}), 500

@app.route('/api/quiz', methods=['POST'])
def generate_quiz():
    data = request.json
    text = data.get('text', '')
    if not text:
        app.logger.warning('No text provided for quiz generation')
        return jsonify({"error": "No text provided"}), 400
    try:
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        prompt = f"Create a multiple-choice question based on: {text[:200]}"
        payload = {"inputs": prompt, "parameters": {"max_length": 150}}
        response = requests.post(QUIZ_GEN_URL, headers=headers, json=payload)
        response.raise_for_status()
        question = response.json()[0]['generated_text'].split('\n')[0]
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]  # Mock options
        app.logger.info('Quiz generation successful')
        return jsonify({"question": question, "options": options, "answer": options[0]})
    except Exception as e:
        app.logger.error(f"Quiz generation failed: {str(e)}")
        return jsonify({"error": f"Quiz generation failed: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.logger.info(f'Starting server on port {port}')
    app.run(host='0.0.0.0', port=port, debug=True)
