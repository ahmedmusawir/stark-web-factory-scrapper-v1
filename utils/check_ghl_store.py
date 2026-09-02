#!/usr/bin/env python3
"""
CHECK GHL STORE STATUS
----------------------
Shows what's currently in your GHL File Search Store

Run: python utils/check_ghl_store.py
"""

from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

print("="*70)
print("  📊 GHL FILE SEARCH STORE STATUS")
print("="*70)

# Load store name
store_file = Path("ghl_store_name.txt")

if not store_file.exists():
    print("\n❌ Store not found!")
    print("   Create one first: python utils/create_ghl_store.py")
    exit(1)

store_name = store_file.read_text().strip()

# Create client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print(f"\n📁 Store: {store_name}")

# Get all documents
print("\n⏳ Loading documents...")

try:
    docs = list(client.file_search_stores.documents.list(parent=store_name))
    
    print(f"\n✅ Documents in store: {len(docs)}")
    
    if len(docs) == 0:
        print("\n   (Store is empty)")
        print("\n💡 Next step: Upload files")
        print("   python utils/test_single_upload.py")
    else:
        # Group by type (md vs summary)
        md_docs = [d for d in docs if not d.display_name.endswith('_SUMMARY')]
        summary_docs = [d for d in docs if d.display_name.endswith('_SUMMARY')]
        
        print(f"\n📄 Breakdown:")
        print(f"   • Markdown files: {len(md_docs)}")
        print(f"   • Summary files: {len(summary_docs)}")
        
        print("\n📋 Sample documents (first 10):")
        for i, doc in enumerate(docs[:10], 1):
            doc_type = "📝" if doc.display_name.endswith('_SUMMARY') else "📄"
            print(f"   {i}. {doc_type} {doc.display_name}")
        
        if len(docs) > 10:
            print(f"\n   ... and {len(docs) - 10} more")
        
        print(f"\n💡 View full list with store ID:")
        print(f"   {store_name}")
    
    print("\n" + "="*70)

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Verify store exists: check ghl_store_name.txt")
    print("2. Test API: python utils/test_api_connection.py")
    exit(1)