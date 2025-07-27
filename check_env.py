#!/usr/bin/env python3
"""
Simple environment check script
"""

import os

print("=== Environment Check ===")

# Check if .env file exists
if os.path.exists('.env'):
    print("✅ .env file found")
    
    # Read the file
    with open('.env', 'r') as f:
        content = f.read()
    
    # Check for API key line
    lines = content.split('\n')
    api_key_line = None
    for line in lines:
        if line.startswith('GEMINI_API_KEY='):
            api_key_line = line
            break
    
    if api_key_line:
        api_key = api_key_line.split('=', 1)[1].strip()
        if api_key in ['your_gemini_api_key_here', 'YOUR_ACTUAL_API_KEY_HERE', '']:
            print("❌ API key is still placeholder or empty")
            print(f"   Current value: {api_key}")
            print("\n🔧 TO FIX:")
            print("1. Get your API key from: https://aistudio.google.com/app/apikey")
            print("2. Edit .env file and replace the placeholder with your actual key")
            print("3. Should look like: GEMINI_API_KEY=AIzaSyD...your_key_here")
        else:
            print("✅ API key appears to be set")
            print(f"   Key starts with: {api_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY line not found in .env file")
else:
    print("❌ .env file not found")

print("\n=== Check Complete ===")