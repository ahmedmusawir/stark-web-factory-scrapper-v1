#!/usr/bin/env python3
"""
UPLOAD MASTER INDEX V2
----------------------
Upload the new quality master index to File Search store

Run: python utils/upload_master_index_v2.py
"""

from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os
import time

load_dotenv()

print("="*70)
print("  📤 UPLOAD MASTER INDEX V2")
print("="*70)

# Configuration
INDEX_FILE = Path("outputs/pages/GHL_API_MASTER_INDEX_V2.txt")
STORE_FILE = Path("ghl_store_name.txt")

# Check files exist
if not INDEX_FILE.exists():
    print(f"\n❌ Master index not found: {INDEX_FILE}")
    print("   Generate it first: python utils/master_index_generator_v2.py")
    exit(1)

if not STORE_FILE.exists():
    print(f"\n❌ Store not found: {STORE_FILE}")
    exit(1)

store_name = STORE_FILE.read_text().strip()

print(f"\n📁 Store: {store_name}")
print(f"📄 File: {INDEX_FILE.name}")
print(f"💾 Size: {INDEX_FILE.stat().st_size / 1024:.1f} KB")

# Create client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Upload
print("\n⏳ Uploading master index V2...")
print("   (This takes a few seconds...)")

try:
    operation = client.file_search_stores.upload_to_file_search_store(
        file=str(INDEX_FILE),
        file_search_store_name=store_name,
        config={
            'display_name': 'GHL_API_MASTER_INDEX_V2',
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
    print("\n✅ Master index V2 uploaded successfully!")
    
    # Verify
    print("\n⏳ Verifying upload...")
    docs = list(client.file_search_stores.documents.list(parent=store_name))
    
    master_doc = [d for d in docs if 'MASTER_INDEX_V2' in d.display_name]
    
    if master_doc:
        print(f"✅ Found in store: {master_doc[0].display_name}")
        print(f"   Total documents now: {len(docs)}")
    
    print("\n" + "="*70)
    print("  ✅ READY TO TEST!")
    print("="*70)
    
    print("\n🧪 Try these queries:")
    print("   • List all API categories")
    print("   • Show me all contact endpoints")
    print("   • How many endpoints are there total?")
    print("   • What are the email template endpoints?")
    
    print("\n🚀 Start chatbot:")
    print("   poetry run python ghl_chatbot_cli.py")
    
    print("\n💡 The chatbot already has the enhanced system prompt!")
    print("   It should give much better answers now.")

except Exception as e:
    print(f"\n\n❌ Error: {e}")
    exit(1)