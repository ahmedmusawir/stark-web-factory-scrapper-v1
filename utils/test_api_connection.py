#!/usr/bin/env python3
"""
TEST API CONNECTION
-------------------
Verify your GEMINI_API_KEY works and File Search API is available

Run: python utils/test_api_connection.py
"""

from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

print("="*70)
print("  🔍 TESTING GEMINI API CONNECTION")
print("="*70)

# Check if API key exists
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("\n❌ GEMINI_API_KEY not found in .env file!")
    print("   Create a .env file in project root with:")
    print("   GEMINI_API_KEY=your_key_here")
    exit(1)

print(f"\n✅ API key found: {api_key[:20]}...")

# Try to connect
print("\n⏳ Connecting to Gemini API...")

try:
    client = genai.Client(api_key=api_key)
    print("✅ Client created successfully!")
    
    # Test basic API call
    print("\n⏳ Testing basic API call...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello"
    )
    
    print("✅ API call successful!")
    print(f"   Response: {response.text[:50]}...")
    
    # Check File Search availability
    print("\n⏳ Checking File Search API availability...")
    
    if hasattr(client, 'file_search_stores'):
        print("✅ File Search API is available!")
        
        # List available methods
        print("\n📋 Available File Search methods:")
        methods = [m for m in dir(client.file_search_stores) if not m.startswith('_')]
        for method in methods[:5]:
            print(f"   • {method}")
        if len(methods) > 5:
            print(f"   ... and {len(methods) - 5} more")
    else:
        print("❌ File Search API not available!")
        print("   Update your SDK: pip install --upgrade google-genai")
        exit(1)
    
    print("\n" + "="*70)
    print("  ✅ ALL TESTS PASSED!")
    print("="*70)
    print("\n🎉 Your API connection is working perfectly!")
    print("   Ready to create File Search stores!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your API key is valid")
    print("2. Verify you have internet connection")
    print("3. Update SDK: pip install --upgrade google-genai")
    exit(1)