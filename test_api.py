#!/usr/bin/env python3
"""
Test script for the CV RAG API
"""

import requests
import json
import sys

def test_api():
    """Test the CV RAG API endpoints"""
    
    base_url = "http://localhost:8080"
    
    print("=== CV RAG API Test ===\n")
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the API server.")
        print("   Make sure the server is running with: python wsgi.py")
        return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False
    
    print()
    
    # Test ask endpoint with sample questions
    test_questions = [
        "What are Ahlam's top skills?",
        "Tell me about her work experience at Omantel",
        "What education does she have?",
        "What programming languages does she know?",
        "What are her achievements?"
    ]
    
    print("2. Testing ask endpoint with sample questions...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n   Question {i}: {question}")
        
        try:
            payload = {"question": question}
            response = requests.post(
                f"{base_url}/ask",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print("   ✅ Success")
                    answer = result.get("answer", "")
                    # Print first 100 characters of answer
                    preview = answer[:100] + "..." if len(answer) > 100 else answer
                    print(f"   Answer preview: {preview}")
                else:
                    print(f"   ❌ API returned error: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Request failed with status code: {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Request error: {str(e)}")
    
    print("\n=== Test Complete ===")
    return True

def test_interactive():
    """Interactive testing mode"""
    
    base_url = "http://localhost:8080"
    
    print("=== Interactive CV RAG API Test ===")
    print("Ask questions about Ahlam's CV. Type 'quit' to exit.\n")
    
    while True:
        question = input("Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not question:
            print("Please enter a question.\n")
            continue
        
        try:
            payload = {"question": question}
            response = requests.post(
                f"{base_url}/ask",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print(f"\nAnswer: {result.get('answer', '')}\n")
                else:
                    print(f"Error: {result.get('error', 'Unknown error')}\n")
            else:
                print(f"Request failed with status code: {response.status_code}\n")
                
        except requests.exceptions.ConnectionError:
            print("Cannot connect to the API server. Make sure it's running.\n")
            break
        except Exception as e:
            print(f"Error: {str(e)}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        test_interactive()
    else:
        test_api()