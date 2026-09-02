#!/usr/bin/env python3
"""
CREATE GHL FILE SEARCH STORE
-----------------------------
Creates a new File Search store for GHL API documentation
Saves store ID to ghl_store_name.txt for other scripts to use

Run: python utils/create_ghl_store.py
"""

from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

print("="*70)
print("  📦 CREATE GHL FILE SEARCH STORE")
print("="*70)

# Check if store already exists
store_file = Path("ghl_store_name.txt")

if store_file.exists():
    existing_store = store_file.read_text().strip()
    print(f"\n⚠️  Store already exists!")
    print(f"   Store ID: {existing_store}")
    
    choice = input("\n   Create a NEW store anyway? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("\n✅ Using existing store")
        print("   Run utils/check_ghl_store.py to view contents")
        exit(0)
    
    print("\n🔄 Creating new store (old one still exists)...")

# Create client
print("\n⏳ Connecting to Gemini API...")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Create the store
print("⏳ Creating File Search store...")
print("   Display name: 'ghl-api-v2-docs'")

try:
    store = client.file_search_stores.create(
        config={'display_name': 'ghl-api-v2-docs'}
    )
    
    print("\n✅ Store created successfully!\n")
    
    print("📋 Store Details:")
    print(f"   Store ID: {store.name}")
    print(f"   Display Name: {store.display_name}")
    
    # Save store name
    store_file.write_text(store.name)
    print(f"\n💾 Store ID saved to: ghl_store_name.txt")
    
    print("\n" + "="*70)
    print("  ✅ SETUP COMPLETE!")
    print("="*70)
    
    print("\n📊 Current status:")
    print("   • Store: Created ✅")
    print("   • Documents: 0 (empty)")
    print("   • Cost so far: $0")
    
    print("\n🎯 Next steps:")
    print("   1. Check store: python utils/check_ghl_store.py")
    print("   2. Test upload: python utils/test_single_upload.py")
    print("   3. Upload all: python utils/upload_all_ghl_docs.py")

except Exception as e:
    print(f"\n❌ Error creating store: {e}")
    print("\nTroubleshooting:")
    print("1. Run: python utils/test_api_connection.py")
    print("2. Check your API key is valid")
    exit(1)