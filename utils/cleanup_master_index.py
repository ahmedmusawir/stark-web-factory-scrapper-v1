#!/usr/bin/env python3
"""
CLEANUP MASTER INDEX
--------------------
Fixes category explosion and garbage entries in master index
Normalizes categories and merges duplicates

Run: python utils/cleanup_master_index.py
"""

from pathlib import Path
from collections import defaultdict
import re

print("="*70)
print("  🧹 CLEANUP MASTER INDEX")
print("="*70)

# Configuration
INPUT_FILE = Path("outputs/pages/GHL_API_MASTER_INDEX_SUMMARY.txt")
OUTPUT_FILE = Path("outputs/pages/GHL_API_MASTER_INDEX_CLEAN.txt")

if not INPUT_FILE.exists():
    print(f"\n❌ Input file not found: {INPUT_FILE}")
    print("   Generate it first: python utils/master_index_generator.py")
    exit(1)

print(f"\n📄 Input: {INPUT_FILE.name}")
print(f"💾 Output: {OUTPUT_FILE.name}")

# Category normalization rules
def normalize_category(category):
    """Normalize category names to standard format."""
    
    # Remove garbage categories (markdown artifacts, bullets, etc.)
    garbage_patterns = [
        r'^###',           # Markdown headers
        r'^\*\s+\*\*',     # Bullet points with bold
        r'^\d+\.\s+\*\*',  # Numbered lists
        r'^---',           # Horizontal rules
        r'^\*\s+`',        # Bullets with code
        r'CODE EXAMPLES',  # Code examples header
        r'HTTP METHOD',    # HTTP method header
        r'AUTHENTICATION', # Auth header
        r'RESPONSE FORMAT',# Response header
        r'PURPOSE:',       # Purpose header
        r'TAGS:',          # Tags header
        r'Example:',       # Examples
        r'offset.*string', # Parameter descriptions
        r'^\d+\.',         # Just numbers
    ]
    
    for pattern in garbage_patterns:
        if re.search(pattern, category, re.IGNORECASE):
            return None
    
    # Clean up the category name
    cleaned = category.strip()
    
    # Remove parenthetical explanations
    # "Contacts (Bulk Operations)" -> "Contacts"
    # "Contacts (specifically Tasks)" -> "Contacts"
    cleaned = re.sub(r'\s*\(.*?\)', '', cleaned)
    
    # Remove sub-category markers
    # "Contacts - Campaigns" -> "Contacts"
    # "Contacts > Campaigns" -> "Contacts"
    # "Contacts / Campaigns" -> "Contacts"
    cleaned = re.split(r'\s*[-/>]\s*', cleaned)[0]
    
    # Remove markdown formatting
    cleaned = cleaned.replace('**', '').replace('*', '').replace('`', '')
    
    # Remove extra whitespace
    cleaned = ' '.join(cleaned.split())
    
    # Skip if too short or still looks like garbage
    if len(cleaned) < 3:
        return None
    
    if any(char in cleaned for char in [':', '[', ']', '{', '}']):
        return None
    
    # Standardize common variations
    standard_categories = {
        'oauth': 'OAuth 2.0',
        'oauth 2.0': 'OAuth 2.0',
        'authorization': 'OAuth 2.0',
        'business': 'Businesses',
        'businesses': 'Businesses',
        'calendar': 'Calendars',
        'calendars': 'Calendars',
        'campaign': 'Campaigns',
        'campaigns': 'Campaigns',
        'company': 'Companies',
        'companies': 'Companies',
        'contact': 'Contacts',
        'contacts': 'Contacts',
        'conversation': 'Conversations',
        'conversations': 'Conversations',
        'course': 'Courses',
        'courses': 'Courses',
        'custom field': 'Custom Fields',
        'custom fields': 'Custom Fields',
        'custom menu': 'Custom Menus',
        'custom menus': 'Custom Menus',
        'email': 'Email',
        'form': 'Forms',
        'forms': 'Forms',
        'funnel': 'Funnels',
        'funnels': 'Funnels',
        'invoice': 'Invoices',
        'invoices': 'Invoices',
        'location': 'Locations',
        'locations': 'Locations',
        'media': 'Media',
        'opportunity': 'Opportunities',
        'opportunities': 'Opportunities',
        'payment': 'Payments',
        'payments': 'Payments',
        'product': 'Products',
        'products': 'Products',
        'saas': 'SaaS',
        'snapshot': 'Snapshots',
        'snapshots': 'Snapshots',
        'social planner': 'Social Planner',
        'survey': 'Surveys',
        'surveys': 'Surveys',
        'user': 'Users',
        'users': 'Users',
        'webhook': 'Webhooks',
        'webhooks': 'Webhooks',
        'workflow': 'Workflows',
        'workflows': 'Workflows',
    }
    
    cleaned_lower = cleaned.lower()
    if cleaned_lower in standard_categories:
        return standard_categories[cleaned_lower]
    
    # Title case for consistency
    return cleaned.title()

print("\n⏳ Reading and parsing master index...")

# Read current master index
content = INPUT_FILE.read_text(encoding='utf-8')

# Parse categories and endpoints
current_category = None
endpoints_by_category = defaultdict(list)
all_endpoints = []

for line in content.split('\n'):
    line = line.strip()
    
    # Detect category headers (## CATEGORY_NAME)
    if line.startswith('## '):
        current_category = line[3:].strip().upper()
        continue
    
    # Parse endpoint lines (format: "  1. [METHOD] Endpoint Name")
    match = re.match(r'\s*\d+\.\s+\[([A-Z]+)\s*\]\s+(.+)', line)
    if match and current_category:
        method = match.group(1).strip()
        name = match.group(2).strip()
        
        # Normalize the category
        normalized_cat = normalize_category(current_category)
        
        if normalized_cat:
            endpoint_data = {
                'name': name,
                'method': method,
                'category': normalized_cat
            }
            endpoints_by_category[normalized_cat].append(endpoint_data)
            all_endpoints.append(endpoint_data)

print(f"✅ Parsed {len(all_endpoints)} endpoints")
print(f"✅ Found {len(endpoints_by_category)} valid categories")

# Generate clean master index
print("\n📝 Generating clean master index...")

master_index = []

# Header
master_index.append("="*70)
master_index.append("GHL API v2 MASTER INDEX (CLEANED)")
master_index.append("Complete Reference for All API Endpoints")
master_index.append("="*70)
master_index.append("")

# Statistics
http_methods = set(e['method'] for e in all_endpoints)

master_index.append("📊 STATISTICS:")
master_index.append(f"   • Total Categories: {len(endpoints_by_category)}")
master_index.append(f"   • Total Endpoints: {len(all_endpoints)}")
master_index.append(f"   • HTTP Methods: {', '.join(sorted(http_methods))}")
master_index.append("")
master_index.append("="*70)
master_index.append("")

# Categories (alphabetical)
master_index.append("📚 ALL API CATEGORIES (Alphabetical):")
master_index.append("")

sorted_categories = sorted(endpoints_by_category.keys())
for i, category in enumerate(sorted_categories, 1):
    endpoint_count = len(endpoints_by_category[category])
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
    category_endpoints = sorted(endpoints_by_category[category], key=lambda x: x['name'])
    
    for i, endpoint in enumerate(category_endpoints, 1):
        master_index.append(f"{i:3d}. [{endpoint['method']:6s}] {endpoint['name']}")
    
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

# Write to file
master_index_text = "\n".join(master_index)
OUTPUT_FILE.write_text(master_index_text, encoding="utf-8")

print("✅ Clean master index generated!")
print(f"   File: {OUTPUT_FILE}")
print(f"   Size: {len(master_index_text):,} chars")

print("\n📊 Summary:")
print(f"   • Categories: {len(endpoints_by_category)} (was 290)")
print(f"   • Endpoints: {len(all_endpoints)}")

print("\n📋 Top 10 Categories:")
top_cats = sorted(endpoints_by_category.items(), key=lambda x: len(x[1]), reverse=True)[:10]
for cat, endpoints in top_cats:
    print(f"   • {cat}: {len(endpoints)} endpoints")

print("\n🎯 Next step:")
print("   Upload to store: python utils/upload_master_index.py")
print("   (Update the script to use GHL_API_MASTER_INDEX_CLEAN.txt)")

print("\n" + "="*70)