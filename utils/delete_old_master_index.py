#!/usr/bin/env python3
"""
DELETE OLD MASTER INDEX
-----------------------
Finds and deletes old/messy master index files from File Search store
Leaves all other documents untouched

Run: python utils/delete_old_master_index.py
"""

from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

print("="*70)
print("  🗑️  DELETE OLD MASTER INDEX FILES")
print("="*70)

# Load store
store_file = Path("ghl_store_name.txt")
if not store_file.exists():
    print("\n❌ Store not found!")
    exit(1)

store_name = store_file.read_text().strip()

# Create client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print(f"\n📁 Store: {store_name}")

# Get all documents
print("\n⏳ Loading documents...")
docs = list(client.file_search_stores.documents.list(parent=store_name))

print(f"✅ Total documents in store: {len(docs)}")

# Find master index files
master_index_docs = [
    d for d in docs 
    if 'MASTER_INDEX' in d.display_name.upper()
]

if not master_index_docs:
    print("\n✅ No master index files found!")
    print("   Store is clean.")
    exit(0)

print(f"\n📋 Found {len(master_index_docs)} master index file(s):")
for i, doc in enumerate(master_index_docs, 1):
    print(f"   {i}. {doc.display_name}")

# Confirm deletion
print("\n⚠️  WARNING: This will DELETE these files from File Search!")
print("   They cannot be recovered.")

try:
    confirm = input("\n⚡ Delete these files? (y/n): ").strip().lower()
except KeyboardInterrupt:
    print("\n\n❌ Cancelled")
    exit(0)

if confirm != 'y':
    print("\n✅ Cancelled. No files deleted.")
    exit(0)

# Delete files
print("\n🗑️  Deleting files...")

deleted = 0
failed = 0

for doc in master_index_docs:
    print(f"   Deleting: {doc.display_name}...", end=" ")
    
    try:
        client.file_search_stores.documents.delete(
            name=doc.name,
            config={'force': True}
        )
        print("✅")
        deleted += 1
    except Exception as e:
        print(f"❌ Error: {e}")
        failed += 1

print("\n" + "="*70)
print("  DELETION COMPLETE")
print("="*70)

print(f"\n📊 Results:")
print(f"   ✅ Deleted: {deleted}")
print(f"   ❌ Failed: {failed}")

print("\n🎯 Next step:")
print("   Upload new master index: python utils/upload_master_index_v2.py")

print("\n" + "="*70)