from flask import Flask, request, jsonify
from transformers import pipeline
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

# Initialize Hugging Face pipelines
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    quiz_generator = pipeline("text-generation", model="distilgpt2")
except Exception as e:
    app.logger.error(f"Failed to initialize Hugging Face pipelines: {str(e)}")
    raise

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
        summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
        app.logger.info('Summarization successful')
        return jsonify({"summary": summary[0]['summary_text']})
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
        prompt = f"Create a multiple-choice question based on: {text[:200]}"
        quiz = quiz_generator(prompt, max_length=150, num_return_sequences=1)
        question = quiz[0]['generated_text'].split('\n')[0]
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
