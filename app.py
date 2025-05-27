from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging
import re
import random

app = Flask(__name__)
# Configure logging
logging.basicConfig(level=logging.INFO)
app.logger.info('Starting Flask app...')

# Restrict CORS to Netlify frontend (update with your Netlify URL)
CORS(app, resources={r"/api/*": {"origins": ["https://your-ssc-app.netlify.app", "http://localhost:3000"]}})

# Mock news data (replace with NewsAPI.org in production)
mock_news = [
    {
        "title": "Operation Sindoor: India's Response to Terrorism",
        "content": "On May 6-7, 2025, Indian forces conducted Operation Sindoor in retaliation to the Pahalgam attack, targeting terrorist bases. The operation was a significant step in counter-terrorism efforts. It involved coordinated strikes across multiple locations.",
        "source": "Utkarsh Classes",
        "date": "2025-05-07"
    },
    {
        "title": "8th Pay Commission Approved",
        "content": "The Union government approved the 8th Pay Commission on February 2, 2025, to revise salaries and pensions for government employees. This decision impacts millions of workers. The commission will review pay structures and benefits.",
        "source": "Indian Express",
        "date": "2025-02-02"
    }
]

@app.route('/', methods=['GET'])
def home():
    app.logger.info('Root endpoint accessed')
    return jsonify({"status": "SSC Exam Knowledge Helper API", "endpoints": ["/api/news", "/api/summarize", "/api/quiz"]}), 200

@app.route('/api/news', methods=['GET'])
def get_news():
    app.logger.info('Fetching news...')
    # For production, integrate NewsAPI.org
   
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
 
    return jsonify(mock_news)

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data.get('text', '')
    if not text:
        app.logger.warning('No text provided for summarization')
        return jsonify({"error": "No text provided"}), 400
    try:
        # Simple rule-based summarization: extract first 2 sentences
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        summary = ' '.join(sentences[:2])[:100]  # Limit to 100 characters
        if not summary:
            summary = text[:100]  # Fallback to first 100 characters
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
        # Simple rule-based quiz: generate a question based on the first sentence
        first_sentence = re.split(r'(?<=[.!?])\s+', text.strip())[0]
        question = f"What is the main focus of the following statement: {first_sentence}?"
        options = [
            "Counter-terrorism efforts" if "Operation Sindoor" in text else "Salary revision",
            "Economic policy",
            "International relations",
            "Scientific advancement"
        ]
        random.shuffle(options)
        answer = options[0]  # Simplified: first option is correct
        app.logger.info('Quiz generation successful')
        return jsonify({"question": question, "options": options, "answer": answer})
    except Exception as e:
        app.logger.error(f"Quiz generation failed: {str(e)}")
        return jsonify({"error": f"Quiz generation failed: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.logger.info(f'Starting server on port {port}, debug={debug}')
    app.run(host='0.0.0.0', port=port, debug=debug)
