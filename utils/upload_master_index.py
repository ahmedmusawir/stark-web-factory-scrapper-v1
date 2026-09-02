#!/usr/bin/env python3
"""
UPLOAD MASTER INDEX
-------------------
Upload the generated master index to File Search store

Run: python utils/upload_master_index.py
"""

from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os
import time

load_dotenv()

print("="*70)
print("  📤 UPLOAD MASTER INDEX TO FILE SEARCH")
print("="*70)

# Configuration
INDEX_FILE = Path("outputs/pages/GHL_API_MASTER_INDEX_SUMMARY.txt")
STORE_FILE = Path("ghl_store_name.txt")

# Check files exist
if not INDEX_FILE.exists():
    print(f"\n❌ Master index not found: {INDEX_FILE}")
    print("   Generate it first: python utils/master_index_generator.py")
    exit(1)

if not STORE_FILE.exists():
    print(f"\n❌ Store not found: {STORE_FILE}")
    print("   Create store first: python utils/create_ghl_store.py")
    exit(1)

store_name = STORE_FILE.read_text().strip()

print(f"\n📁 Store: {store_name}")
print(f"📄 File: {INDEX_FILE.name}")
print(f"💾 Size: {INDEX_FILE.stat().st_size / 1024:.1f} KB")

# Create client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Upload
print("\n⏳ Uploading master index...")
print("   (This takes a few seconds...)")

try:
    operation = client.file_search_stores.upload_to_file_search_store(
        file=str(INDEX_FILE),
        file_search_store_name=store_name,
        config={
            'display_name': 'GHL_API_MASTER_INDEX_SUMMARY',
            'mime_type': 'text/plain'
        }
    )
    
    # Wait for completion
    print("   Processing", end="", flush=True)
    while not operation.done:
        print(".", end="", flush=True)
        time.sleep(1)
        operation = client.operations.get(operation)
    
    print(" ✅")
    print("\n✅ Master index uploaded successfully!")
    
    # Verify
    print("\n⏳ Verifying upload...")
    docs = list(client.file_search_stores.documents.list(parent=store_name))
    
    master_doc = [d for d in docs if 'MASTER_INDEX' in d.display_name]
    
    if master_doc:
        print(f"✅ Found in store: {master_doc[0].display_name}")
        print(f"   Document ID: {master_doc[0].name}")
    
    print("\n" + "="*70)
    print("  ✅ READY TO TEST!")
    print("="*70)
    
    print("\n🧪 Try these queries:")
    print("   • List all API categories")
    print("   • Show me all endpoints")
    print("   • How many contact endpoints are there?")
    print("   • What are all the HTTP methods available?")
    
    print("\n🚀 Start chatbot:")
    print("   poetry run python ghl_chatbot_cli.py")

except Exception as e:
    print(f"\n\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check file exists and is readable")
    print("2. Verify API connection: python utils/test_api_connection.py")
    exit(1)