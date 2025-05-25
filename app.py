from flask import Flask, request, jsonify
from transformers import pipeline
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# Restrict CORS to Netlify frontend (update with your Netlify URL)
CORS(app, resources={r"/api/*": {"origins": ["https://your-ssc-app.netlify.app", "http://localhost:3000"]}})

# Initialize Hugging Face pipelines
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
# For quiz generation, using a simple text-generation approach
quiz_generator = pipeline("text-generation", model="distilgpt2")

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
    # For production, integrate NewsAPI.org
    """
    api_key = "YOUR_NEWSAPI_KEY"
    url = f"https://newsapi.org/v2/everything?q=india+ssc&apiKey={api_key}"
    response = requests.get(url)
    articles = response.json()['articles']
    formatted_articles = [
        {
            "title": article["title"],
            "content": article["content"] or article["description"],
            "source": article["source"]["name"],
            "date": article["publishedAt"]
        } for article in articles[:5]  # Limit to 5 articles
    ]
    return jsonify(formatted_articles)
    """
    return jsonify(mock_news)

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400
    try:
        summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
        return jsonify({"summary": summary[0]['summary_text']})
    except Exception as e:
        return jsonify({"error": f"Summarization failed: {str(e)}"}), 500

@app.route('/api/quiz', methods=['POST'])
def generate_quiz():
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400
    try:
        # Generate a simple MCQ using text-generation
        prompt = f"Create a multiple-choice question based on: {text[:200]}"
        quiz = quiz_generator(prompt, max_length=150, num_return_sequences=1)
        # Parse output (simplified; improve for production)
        question = quiz[0]['generated_text'].split('\n')[0]
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]  # Mock options
        return jsonify({"question": question, "options": options, "answer": options[0]})
    except Exception as e:
        return jsonify({"error": f"Quiz generation failed: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Render's PORT or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)
