from flask import Flask, request, jsonify
from flask_cors import CORS
from .chatbot import handle_recruiter_questions
import os
from dotenv import load_dotenv
from pathlib import Path  # Add this import
from .chatbot import FRIENDLY_API_ERROR_MESSAGE


env_path = Path('.') / '.env' 
load_dotenv(dotenv_path=env_path)
app = Flask(__name__)
CORS(app) 

@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        DEFAULT_PLACEHOLDER = "your-default-key-here" 
        if not api_key or api_key == DEFAULT_PLACEHOLDER:
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
        
        # session_id = data.get('session_id')
        # if not session_id:
        #     session_id = str(uuid.uuid4())

        # Process the question
        answer = handle_recruiter_questions(question=question, api_key=api_key)

        # If the chatbot hit an internal error, return a friendly message
        if answer == FRIENDLY_API_ERROR_MESSAGE:
            return (
                jsonify(
                    {
                        "answer": FRIENDLY_API_ERROR_MESSAGE,
                        "message": FRIENDLY_API_ERROR_MESSAGE,
                        "status": "error",
                    }
                ),
                503,
            )
        
        return jsonify({
            "answer": answer,
            "status": "success"
        })
        
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "answer": FRIENDLY_API_ERROR_MESSAGE,
                    "message": FRIENDLY_API_ERROR_MESSAGE,
                    "error": str(e),
                }
            ),
            500,
        )

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "CV RAG API is running"
    })
@app.route('/')
def home():
    return jsonify({"message": "CV Agent API is running. Go to /ask to ask questions about Ahlam's CV", "status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
