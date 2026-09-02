#!/usr/bin/env python3
"""
UPLOAD ALL GHL DOCS
-------------------
Batch upload all .md files and summaries to File Search store
This is the BIG upload - all 1414 files!

Run: python utils/upload_all_ghl_docs.py
"""

from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os
import time

load_dotenv()

print("="*70)
print("  🚀 BATCH UPLOAD ALL GHL DOCS")
print("="*70)

# Check store exists
store_file = Path("ghl_store_name.txt")
if not store_file.exists():
    print("\n❌ Store not found!")
    print("   Create one first: python utils/create_ghl_store.py")
    exit(1)

store_name = store_file.read_text().strip()

# Find all files
pages_dir = Path("outputs/pages")
if not pages_dir.exists():
    print(f"\n❌ Directory not found: {pages_dir}")
    exit(1)

md_files = sorted(pages_dir.glob("*.md"))
summary_files = sorted(pages_dir.glob("*_SUMMARY.txt"))

if not md_files:
    print(f"\n❌ No markdown files found!")
    exit(1)

# Combine all files to upload
all_files = []
for md in md_files:
    all_files.append(md)
    # Add summary if exists
    summary = pages_dir / f"{md.stem}_SUMMARY.txt"
    if summary.exists():
        all_files.append(summary)

total_count = len(all_files)
total_size = sum(f.stat().st_size for f in all_files)

print(f"\n📁 Store: {store_name}")
print(f"📂 Source: {pages_dir}")

print(f"\n📊 Files to upload:")
print(f"   • Markdown files: {len(md_files)}")
print(f"   • Summary files: {len(summary_files)}")
print(f"   • Total files: {total_count}")
print(f"   • Total size: {total_size / 1024 / 1024:.1f} MB")

print(f"\n⏱️  Estimated time: {(total_count * 2.5) / 60:.0f} minutes")
print("   (~2.5 seconds per file)")

# Show sample
print(f"\n📄 Sample files (first 5):")
for f in all_files[:5]:
    size_kb = f.stat().st_size / 1024
    file_type = "📝" if f.suffix == '.txt' else "📄"
    print(f"   {file_type} {f.name} ({size_kb:.1f} KB)")

if total_count > 5:
    print(f"   ... and {total_count - 5} more")

# Confirm before starting
print("\n" + "="*70)
print("  ⚠️  IMPORTANT")
print("="*70)
print("""
This will upload ALL files to Google File Search.
- Upload is one-way (can't bulk-delete easily)
- Takes ~20-30 minutes
- Cost: ~$0.01-0.05 (very cheap!)
""")

try:
    proceed = input("⚡ Proceed with batch upload? (y/n): ").strip().lower()
except KeyboardInterrupt:
    print("\n\n❌ Cancelled")
    exit(0)

if proceed != 'y':
    print("\n❌ Cancelled")
    exit(0)

# Create client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("\n" + "="*70)
print("  🚀 STARTING BATCH UPLOAD")
print("="*70)
print(f"\n⏳ Uploading {total_count} files...")
print("   Grab a coffee! ☕\n")

# Upload all files
successful = 0
failed = 0
start_time = time.time()

for i, file in enumerate(all_files, 1):
    file_type = "📝" if file.suffix == '.txt' else "📄"
    
    print(f"[{i}/{total_count}] {file_type} {file.name}...", end=" ", flush=True)
    
    try:
        # Determine mime type based on file extension
        mime_type = 'text/plain' if file.suffix == '.txt' else 'text/markdown'
        
        operation = client.file_search_stores.upload_to_file_search_store(
            file=str(file),
            file_search_store_name=store_name,
            config={
                'display_name': file.stem,
                'mime_type': mime_type
            }
        )
        
        # Wait for completion (no dots, just wait)
        while not operation.done:
            time.sleep(0.5)
            operation = client.operations.get(operation)
        
        print("✅")
        successful += 1
        
        # Progress update every 50 files
        if i % 50 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed
            remaining = (total_count - i) / rate
            
            print(f"\n📊 Progress: {i}/{total_count} | ✅ {successful} | ❌ {failed}")
            print(f"   Time elapsed: {elapsed / 60:.1f} min | Remaining: ~{remaining / 60:.1f} min\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        failed += 1
        continue

elapsed = time.time() - start_time

# Final summary
print("\n" + "="*70)
print("  ✅ BATCH UPLOAD COMPLETE!")
print("="*70)

print(f"\n📊 Results:")
print(f"   ✅ Successful: {successful}")
print(f"   ❌ Failed: {failed}")
print(f"   ⏱️  Time: {elapsed / 60:.1f} minutes")
print(f"   📈 Rate: {successful / elapsed:.1f} files/sec")

print(f"\n🎯 Next steps:")
print("   1. Check store: python utils/check_ghl_store.py")
print("   2. Test queries: python utils/query_test.py")
print("   3. Build chatbot: streamlit run ghl_chatbot.py")

print("\n" + "="*70)
print("  🎉 YOUR GHL API KNOWLEDGE BASE IS READY!")
print("="*70)