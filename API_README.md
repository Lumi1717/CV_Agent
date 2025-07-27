# CV RAG API Documentation

This is a Retrieval-Augmented Generation (RAG) API that allows users to ask questions about Ahlam Yusuf's professional background and CV using Google's Gemini AI.

## Features

- **Smart CV Querying**: Ask natural language questions about work experience, skills, education, and achievements
- **Gemini AI Integration**: Powered by Google's Gemini 1.5 Pro for intelligent responses
- **Secure API Key Management**: Environment-based configuration for API keys
- **RESTful API**: Simple JSON-based API endpoints
- **Error Handling**: Comprehensive error handling and validation
- **Health Checks**: Built-in health monitoring endpoint

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Gemini API Key

**Option A: Use the setup script (Recommended)**
```bash
python setup_api_key.py
```

**Option B: Manual setup**
1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Open the `.env` file
3. Replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Start the Server

```bash
python wsgi.py
```

The API will be available at `http://localhost:8080`

### 4. Test the API

```bash
# Run automated tests
python test_api.py

# Or run interactive tests
python test_api.py --interactive
```

## API Endpoints

### Health Check
```
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "message": "CV RAG API is running"
}
```

### Ask Questions
```
POST /ask
```

**Request Body:**
```json
{
    "question": "What are Ahlam's top skills?"
}
```

**Response (Success):**
```json
{
    "answer": "Ahlam's top skills include Machine Learning, Data Analysis, Deep Learning, Problem resolution, Statistical Data Analysis, Prophet, ARIMA, Python, and SQL. She's particularly strong in developing predictive models and using machine learning algorithms for time series analysis.",
    "status": "success"
}
```

**Response (Error):**
```json
{
    "error": "Error message description",
    "status": "error"
}
```

## Example Questions

Here are some example questions you can ask:

- "What are Ahlam's top skills?"
- "Tell me about her work experience at Omantel"
- "What education does she have?"
- "What programming languages does she know?"
- "What are her achievements and awards?"
- "What projects has she worked on?"
- "Tell me about her experience with machine learning"
- "What is her background in data science?"

## API Integration Examples

### Python (using requests)
```python
import requests

url = "http://localhost:8080/ask"
payload = {"question": "What are Ahlam's top skills?"}

response = requests.post(url, json=payload)
result = response.json()

if result.get("status") == "success":
    print(result["answer"])
else:
    print(f"Error: {result.get('error')}")
```

### JavaScript (using fetch)
```javascript
const response = await fetch('http://localhost:8080/ask', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        question: "What are Ahlam's top skills?"
    })
});

const result = await response.json();

if (result.status === 'success') {
    console.log(result.answer);
} else {
    console.error('Error:', result.error);
}
```

### cURL
```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are Ahlam's top skills?"}'
```

## Error Handling

The API provides detailed error messages for common issues:

- **Missing API Key**: When Gemini API key is not configured
- **Invalid Request**: When request body is malformed or missing required fields
- **Empty Question**: When the question field is empty
- **Processing Errors**: When there are issues with AI processing
- **CV Data Loading**: When the CV data file cannot be loaded

## Security Notes

- **API Key Protection**: The Gemini API key is stored in environment variables and never exposed in responses
- **CORS Enabled**: Cross-origin requests are enabled for frontend integration
- **Input Validation**: All inputs are validated before processing
- **Error Sanitization**: Error messages are sanitized to prevent information leakage

## Deployment

### Local Development
```bash
python wsgi.py
```

### Production (using Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8080 src.api:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "src.api:app"]
```

## Project Structure

```
├── src/
│   ├── api.py              # Flask API endpoints
│   ├── chatbot.py          # AI processing logic
│   ├── cv_data.py          # CV data loading utilities
│   └── __init__.py
├── data/
│   └── cv.json             # CV data file
├── .env                    # Environment variables (API keys)
├── wsgi.py                 # WSGI entry point
├── setup_api_key.py        # API key setup utility
├── test_api.py             # API testing script
└── requirements.txt        # Python dependencies
```

## Troubleshooting

### Common Issues

1. **"Gemini API key not configured"**
   - Run `python setup_api_key.py` to configure your API key
   - Ensure your `.env` file contains a valid `GEMINI_API_KEY`

2. **"Could not load CV data"**
   - Ensure `data/cv.json` exists and is readable
   - Check file permissions and JSON syntax

3. **Connection refused**
   - Make sure the server is running: `python wsgi.py`
   - Check if port 8080 is available

4. **Empty or invalid responses**
   - Verify your Gemini API key is valid and has quota
   - Check the server logs for detailed error messages

### Logs and Debugging

- The application uses Python's logging module
- Check console output for detailed error messages
- For production, consider configuring log files

## Contributing

When making changes to the API:

1. Update the CV data in `data/cv.json` if needed
2. Test all endpoints using `python test_api.py`
3. Update this documentation for any API changes
4. Ensure environment variables are properly configured

## License

This project is for demonstration purposes of a CV RAG system using Gemini AI.