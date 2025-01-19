from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import handle_recruiter_questions

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    data = request.json
    question = data.get('question')
    api_key = data.get('apiKey')
    answer = handle_recruiter_questions(questions=question, api_key=api_key)
    return jsonify({"answer": answer})
