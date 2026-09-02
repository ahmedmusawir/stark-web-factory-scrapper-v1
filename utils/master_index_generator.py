#!/usr/bin/env python3
"""
MASTER INDEX GENERATOR
----------------------
Analyzes all 711 GHL API summaries and creates a comprehensive master index
This gives RAG a single source of truth for "list all" queries

Run: python utils/master_index_generator.py
"""

from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os
import re
from collections import defaultdict

load_dotenv()

print("="*70)
print("  📚 GHL API MASTER INDEX GENERATOR")
print("="*70)

# Configuration
SOURCE_DIR = Path("outputs/pages")
OUTPUT_FILE = SOURCE_DIR / "GHL_API_MASTER_INDEX_SUMMARY.txt"

print(f"\n📁 Source: {SOURCE_DIR}")
print(f"💾 Output: {OUTPUT_FILE}")

# Find all summary files
summary_files = list(SOURCE_DIR.glob("*_SUMMARY.txt"))

if not summary_files:
    print("\n❌ No summary files found!")
    print("   Run summary generator first!")
    exit(1)

print(f"\n📄 Found {len(summary_files)} summary files")
print("\n⏳ Analyzing summaries...\n")

# Data structures
categories = defaultdict(list)
all_endpoints = []
authentication_methods = set()
http_methods = set()

# Parse each summary
for i, summary_file in enumerate(summary_files, 1):
    if i % 50 == 0:
        print(f"   Processed {i}/{len(summary_files)}...")
    
    try:
        content = summary_file.read_text(encoding="utf-8")
        
        # Extract key information
        endpoint_name = ""
        category = "Other"
        http_method = ""
        endpoint_url = ""
        auth_info = ""
        
        # Parse summary content (handles both plain and markdown format)
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Handle markdown headers (### 1. ENDPOINT NAME:)
            if "ENDPOINT NAME" in line.upper():
                # Get next non-empty line as value
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    endpoint_name = lines[i].strip()
            
            elif "CATEGORY" in line.upper() and "HTTP" not in line.upper():
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    category = lines[i].strip()
            
            elif "HTTP METHOD" in line.upper():
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    http_method = lines[i].strip().upper()
                    if http_method and http_method not in ['N/A', 'NOT APPLICABLE']:
                        http_methods.add(http_method)
            
            elif "ENDPOINT URL" in line.upper() and "FULL" not in line.upper():
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    # Remove markdown code backticks
                    endpoint_url = lines[i].strip().replace('`', '')
            
            elif "FULL URL" in line.upper():
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    full_url = lines[i].strip().replace('`', '')
                    if not endpoint_url and full_url:
                        endpoint_url = full_url
            
            elif "AUTHENTICATION" in line.upper():
                # Read next few lines for auth info
                auth_lines = []
                i += 1
                for j in range(10):  # Read up to 10 lines
                    if i + j < len(lines):
                        auth_lines.append(lines[i + j])
                auth_info = ' '.join(auth_lines)
                
                # Extract auth methods
                if "OAuth" in auth_info or "oauth" in auth_info:
                    authentication_methods.add("OAuth Access Token")
                if "Bearer" in auth_info or "bearer" in auth_info:
                    authentication_methods.add("Bearer Token")
                if "Private" in auth_info or "private" in auth_info:
                    authentication_methods.add("Private Integration Token")
            
            i += 1
        
        # Store endpoint info
        if endpoint_name and category:
            endpoint_data = {
                "name": endpoint_name,
                "method": http_method,
                "url": endpoint_url,
                "category": category
            }
            
            categories[category].append(endpoint_data)
            all_endpoints.append(endpoint_data)
    
    except Exception as e:
        print(f"   ⚠️  Error processing {summary_file.name}: {e}")
        continue

print(f"✅ Analysis complete!\n")

# Generate master index
print("📝 Generating master index...\n")

master_index = []

# Header
master_index.append("="*70)
master_index.append("GHL API v2 MASTER INDEX")
master_index.append("Complete Reference for All API Endpoints")
master_index.append("="*70)
master_index.append("")

# Statistics
master_index.append("📊 STATISTICS:")
master_index.append(f"   • Total Categories: {len(categories)}")
master_index.append(f"   • Total Endpoints: {len(all_endpoints)}")
master_index.append(f"   • HTTP Methods: {', '.join(sorted(http_methods))}")
master_index.append(f"   • Authentication: {', '.join(sorted(authentication_methods))}")
master_index.append("")
master_index.append("="*70)
master_index.append("")

# Categories (alphabetical)
master_index.append("📚 ALL API CATEGORIES (Alphabetical):")
master_index.append("")

sorted_categories = sorted(categories.keys())
for i, category in enumerate(sorted_categories, 1):
    endpoint_count = len(categories[category])
    master_index.append(f"{i:2d}. {category} ({endpoint_count} endpoints)")

master_index.append("")
master_index.append("="*70)
master_index.append("")

# Endpoints by category
master_index.append("📋 ALL ENDPOINTS BY CATEGORY:")
master_index.append("")

for category in sorted_categories:
    master_index.append(f"## {category.upper()}")
    master_index.append("")
    
    # Sort endpoints within category
    category_endpoints = sorted(categories[category], key=lambda x: x['name'])
    
    for i, endpoint in enumerate(category_endpoints, 1):
        method = endpoint['method'] or 'N/A'
        url = endpoint['url'] or 'N/A'
        master_index.append(f"{i:3d}. [{method:6s}] {endpoint['name']}")
        master_index.append(f"     URL: {url}")
    
    master_index.append("")

master_index.append("="*70)
master_index.append("")

# Quick reference by HTTP method
master_index.append("🔍 QUICK REFERENCE BY HTTP METHOD:")
master_index.append("")

for method in sorted(http_methods):
    method_endpoints = [e for e in all_endpoints if e['method'] == method]
    master_index.append(f"## {method} ({len(method_endpoints)} endpoints)")
    
    for endpoint in sorted(method_endpoints, key=lambda x: x['name'])[:10]:
        master_index.append(f"   • {endpoint['name']} - {endpoint['category']}")
    
    if len(method_endpoints) > 10:
        master_index.append(f"   ... and {len(method_endpoints) - 10} more")
    
    master_index.append("")

master_index.append("="*70)
master_index.append("")

# Searchable keywords
master_index.append("🏷️  SEARCHABLE KEYWORDS:")
master_index.append("")
master_index.append("Categories: " + ", ".join(sorted_categories))
master_index.append("")
master_index.append("Common Operations: create, get, update, delete, list, search, " +
                   "upload, download, send, receive, process, validate, verify, " +
                   "enable, disable, activate, deactivate")
master_index.append("")
master_index.append("="*70)

# Write to file
master_index_text = "\n".join(master_index)
OUTPUT_FILE.write_text(master_index_text, encoding="utf-8")

print("✅ Master index generated!")
print(f"   File: {OUTPUT_FILE}")
print(f"   Size: {len(master_index_text):,} chars")
print(f"   Lines: {len(master_index):,}")

print("\n📊 Summary:")
print(f"   • Categories: {len(categories)}")
print(f"   • Endpoints: {len(all_endpoints)}")
print(f"   • Methods: {len(http_methods)}")

print("\n🎯 Next steps:")
print("   1. Review the master index file")
print("   2. Upload to store: python utils/upload_master_index.py")
print("   3. Test queries: 'List all categories', 'Show all endpoints'")

print("\n" + "="*70)