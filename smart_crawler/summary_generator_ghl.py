#!/usr/bin/env python3
"""
GHL API SUMMARY GENERATOR
-------------------------
Generates API-specific summaries for each endpoint markdown file
Optimized for answering questions like:
- "List all endpoints"
- "Show me contact-related endpoints"
- "What parameters does create contact need?"
- "Give me Python code examples"

Run: python summary_generator_ghl.py
"""

from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os
import time

load_dotenv()

print("="*80)
print("  📋 GHL API SUMMARY GENERATOR")
print("="*80)

# Configuration
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
SOURCE_DIR = Path("outputs/pages")
SUMMARY_SUFFIX = "_SUMMARY.txt"

# Verify source directory
if not SOURCE_DIR.exists():
    print(f"\n❌ Source directory not found: {SOURCE_DIR}")
    print("   Make sure crawler has completed!")
    exit(1)

# Get all markdown files
md_files = list(SOURCE_DIR.glob("*.md"))

if not md_files:
    print(f"\n❌ No markdown files found in {SOURCE_DIR}")
    exit(1)

print(f"\n📁 Source directory: {SOURCE_DIR}")
print(f"📄 Found {len(md_files)} markdown files")

# API-SPECIFIC SUMMARY PROMPT
# This is DIFFERENT from the generic PDF prompt!
SUMMARY_PROMPT = """
Analyze this API documentation and create a STRUCTURED SUMMARY optimized for search and retrieval.

Extract the following information:

1. ENDPOINT NAME: (The main title/name of this API endpoint)

2. CATEGORY: (What category does this belong to? e.g., Contacts, Calendars, Campaigns, Businesses, etc.)

3. HTTP METHOD: (GET, POST, PUT, PATCH, DELETE)

4. ENDPOINT URL: (The API endpoint path, e.g., /contacts/ or /contacts/:contactId)

5. FULL URL: (Complete URL including domain if available)

6. REQUIRED PARAMETERS: (List ALL required parameters with their types and descriptions)
   Format: - paramName (type): description

7. OPTIONAL PARAMETERS: (List ALL optional parameters with their types and descriptions)
   Format: - paramName (type): description

8. AUTHENTICATION: (Required scopes, auth methods, token types)

9. RESPONSE FORMAT: (What does a successful response look like? Status code and structure)

10. PURPOSE: (One sentence explaining what this endpoint does)

11. TAGS: (Keywords for searchability: category, action, resource type, etc.)

Be EXHAUSTIVE with parameters - list EVERY single parameter mentioned.
If code examples (Python, Node, cURL) are present, note their availability.
If no information is available for a section, write "Not specified in documentation"

Format clearly with headers and bullet points for easy parsing.
"""

print("\n" + "="*80)
print("  🚀 STARTING SUMMARY GENERATION")
print("="*80)
print(f"\n⏱️  This will take ~20-30 minutes for {len(md_files)} files")
print("   Using Gemini 2.5 Flash for speed")
print("\n☕ Grab a coffee while this runs!\n")

# Confirm before starting
try:
    proceed = input("⚡ Proceed with summary generation? (y/n): ").strip().lower()
except KeyboardInterrupt:
    print("\n\n❌ Aborted by user")
    exit(0)

if proceed != "y":
    print("❌ Aborted")
    exit(0)

print("\n" + "="*80)

# Process each file
successful = 0
failed = 0
skipped = 0

for i, md_file in enumerate(md_files, 1):
    # Check if summary already exists
    summary_file = md_file.parent / f"{md_file.stem}{SUMMARY_SUFFIX}"
    
    if summary_file.exists():
        print(f"[{i}/{len(md_files)}] ⏭️  Skipping (summary exists): {md_file.name}")
        skipped += 1
        continue
    
    print(f"\n[{i}/{len(md_files)}] Processing: {md_file.name}")
    
    try:
        # Read markdown file
        markdown_text = md_file.read_text(encoding="utf-8")
        
        if len(markdown_text) < 100:
            print(f"   ⚠️  File too short ({len(markdown_text)} chars), skipping")
            failed += 1
            continue
        
        print(f"   📄 Read {len(markdown_text):,} chars")
        print(f"   🤔 Generating summary with Gemini...")
        
        # Generate summary with Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Fast model for speed
            contents=[markdown_text, SUMMARY_PROMPT]
        )
        
        summary_text = response.text.strip()
        
        if not summary_text:
            print(f"   ❌ Empty summary generated")
            failed += 1
            continue
        
        # Save summary
        summary_file.write_text(summary_text, encoding="utf-8")
        
        print(f"   ✅ Summary saved: {summary_file.name}")
        print(f"   📊 Summary size: {len(summary_text):,} chars")
        successful += 1
        
        # Rate limiting - small delay to avoid hitting API limits
        if i % 10 == 0:
            print(f"\n📊 Progress: {i}/{len(md_files)} | ✅ {successful} | ❌ {failed} | ⏭️  {skipped}\n")
            time.sleep(1)  # Brief pause every 10 files
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        failed += 1
        continue

# Final summary
print("\n" + "="*80)
print("✅ SUMMARY GENERATION COMPLETE!")
print("="*80)
print(f"\n📊 Results:")
print(f"   ✅ Successful: {successful}")
print(f"   ❌ Failed: {failed}")
print(f"   ⏭️  Skipped (already exists): {skipped}")
print(f"\n📁 Summaries saved to: {SOURCE_DIR}")

if successful > 0:
    # Show examples
    print(f"\n📄 Example files created:")
    summary_files = list(SOURCE_DIR.glob(f"*{SUMMARY_SUFFIX}"))
    for summary in summary_files[:3]:
        size_kb = summary.stat().st_size / 1024
        print(f"   • {summary.name} ({size_kb:.1f} KB)")
    
    if len(summary_files) > 3:
        print(f"   ... and {len(summary_files) - 3} more")

print("\n🎯 Next step: Upload to File Search")
print("   Files to upload:")
print(f"   • {len(md_files)} markdown files")
print(f"   • {successful} summary files")
print(f"   • Total: {len(md_files) + successful} files")

print("\n" + "="*80)
print("💡 TIP: You can re-run this script anytime")
print("   It will skip files that already have summaries")
print("="*80)