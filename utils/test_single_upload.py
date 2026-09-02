#!/usr/bin/env python3
"""
TEST SINGLE FILE UPLOAD
-----------------------
Upload ONE .md file + summary to test the upload process
Verifies everything works before batch upload

Run: python utils/test_single_upload.py
"""

from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os
import time

load_dotenv()

print("="*70)
print("  🧪 TEST SINGLE FILE UPLOAD")
print("="*70)

# Check store exists
store_file = Path("ghl_store_name.txt")
if not store_file.exists():
    print("\n❌ Store not found!")
    print("   Create one first: python utils/create_ghl_store.py")
    exit(1)

store_name = store_file.read_text().strip()

# Find markdown files
pages_dir = Path("outputs/pages")
if not pages_dir.exists():
    print(f"\n❌ Directory not found: {pages_dir}")
    print("   Make sure crawler has finished!")
    exit(1)

md_files = list(pages_dir.glob("*.md"))
if not md_files:
    print(f"\n❌ No markdown files found in {pages_dir}")
    exit(1)

# Select first file (or specific one)
test_file = md_files[0]
summary_file = pages_dir / f"{test_file.stem}_SUMMARY.txt"

print(f"\n📁 Store: {store_name}")
print(f"\n📄 Test files:")
print(f"   1. {test_file.name}")

has_summary = summary_file.exists()
if has_summary:
    print(f"   2. {summary_file.name}")
else:
    print(f"   ⚠️  No summary file found (will upload .md only)")

# Create client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Upload markdown file
print(f"\n⏳ Uploading: {test_file.name}")
print("   (This takes a few seconds...)")

try:
    operation = client.file_search_stores.upload_to_file_search_store(
        file=str(test_file),
        file_search_store_name=store_name,
        config={
            'display_name': test_file.stem,
            'mime_type': 'text/markdown'
        }
    )
    
    # Wait for completion
    print("   Processing", end="", flush=True)
    while not operation.done:
        print(".", end="", flush=True)
        time.sleep(1)
        operation = client.operations.get(operation)
    
    print(" ✅")
    print(f"✅ Uploaded: {test_file.name}")
    
    # Upload summary if exists
    if has_summary:
        print(f"\n⏳ Uploading: {summary_file.name}")
        
        operation = client.file_search_stores.upload_to_file_search_store(
            file=str(summary_file),
            file_search_store_name=store_name,
            config={
                'display_name': summary_file.stem,
                'mime_type': 'text/plain'
            }
        )
        
        print("   Processing", end="", flush=True)
        while not operation.done:
            print(".", end="", flush=True)
            time.sleep(1)
            operation = client.operations.get(operation)
        
        print(" ✅")
        print(f"✅ Uploaded: {summary_file.name}")
    
    # Verify upload
    print("\n⏳ Verifying upload...")
    docs = list(client.file_search_stores.documents.list(parent=store_name))
    
    expected_count = 2 if has_summary else 1
    
    print(f"✅ Documents in store: {len(docs)}")
    print("\n📋 Uploaded documents:")
    for doc in docs:
        print(f"   • {doc.display_name}")
    
    print("\n" + "="*70)
    print("  ✅ TEST SUCCESSFUL!")
    print("="*70)
    
    print("\n🎯 Next steps:")
    print("   1. Query test: python utils/query_test.py")
    print("   2. Full upload: python utils/upload_all_ghl_docs.py")
    
    print("\n💡 To remove test files:")
    print("   python utils/cleanup_ghl_store.py")

except Exception as e:
    print(f"\n\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check file exists and is readable")
    print("2. Verify API connection: python utils/test_api_connection.py")
    exit(1)