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
    answer = handle_recruiter_questions(question)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
