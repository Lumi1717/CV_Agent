#!/usr/bin/env python3
"""
Setup script for configuring the Gemini API key
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_gemini_api_key():
    """Setup Gemini API key in the .env file"""
    
    print("=== CV RAG Project - Gemini API Key Setup ===\n")
    
    # Check if .env file exists
    env_file = '.env'
    if not os.path.exists(env_file):
        print(f"Error: {env_file} file not found!")
        print("Please make sure you're running this script from the project root directory.")
        return False
    
    # Get API key from user
    print("To use this CV RAG project, you need a Gemini API key.")
    print("You can get one from: https://aistudio.google.com/app/apikey\n")
    
    api_key = input("Please enter your Gemini API key: ").strip()
    
    if not api_key:
        print("Error: API key cannot be empty!")
        return False
    
    # Read current .env content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace the placeholder API key
    if 'GEMINI_API_KEY=your_gemini_api_key_here' in content:
        new_content = content.replace('GEMINI_API_KEY=your_gemini_api_key_here', f'GEMINI_API_KEY={api_key}')
    elif 'GEMINI_API_KEY=' in content:
        # Update existing key
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('GEMINI_API_KEY='):
                lines[i] = f'GEMINI_API_KEY={api_key}'
                break
        new_content = '\n'.join(lines)
    else:
        # Add new key
        new_content = content + f'\nGEMINI_API_KEY={api_key}\n'
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.write(new_content)
    
    print(f"\n✅ Gemini API key has been saved to {env_file}")
    print("\nYour CV RAG API is now ready to use!")
    print("\nTo start the server, run:")
    print("  python wsgi.py")
    print("\nTo test the API, you can use:")
    print("  python test_api.py")
    
    return True

if __name__ == "__main__":
    setup_gemini_api_key()