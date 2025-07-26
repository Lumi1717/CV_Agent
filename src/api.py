from flask import Flask, request, jsonify
from flask_cors import CORS
from .chatbot import handle_recruiter_questions
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    try:
        # Check if Gemini API key is configured
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            return jsonify({
                "error": "Gemini API key not configured. Please set GEMINI_API_KEY in your .env file."
            }), 500
        
        # Get question from request
        data = request.json
        if not data or 'question' not in data:
            return jsonify({
                "error": "Missing 'question' field in request body"
            }), 400
        
        question = data.get('question', '').strip()
        if not question:
            return jsonify({
                "error": "Question cannot be empty"
            }), 400
        
        # Process the question
        answer = handle_recruiter_questions(question=question, api_key=api_key)
        
        return jsonify({
            "answer": answer,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}",
            "status": "error"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "CV RAG API is running"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
