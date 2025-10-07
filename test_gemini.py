#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key loaded: {'Yes' if api_key else 'No'}")
print(f"API Key length: {len(api_key) if api_key else 0}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # List available models
        print("Available models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
        
        # Try with the correct model name
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Test with a simple prompt
        test_prompt = "Say 'Hello, Gemini API is working!' in a professional tone."
        response = model.generate_content(test_prompt)
        
        print("✅ Gemini API Test SUCCESS!")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print("❌ Gemini API Test FAILED!")
        print(f"Error: {e}")
else:
    print("❌ No API key found in environment variables!")
