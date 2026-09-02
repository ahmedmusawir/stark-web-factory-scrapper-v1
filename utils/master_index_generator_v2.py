#!/usr/bin/env python3
"""
MASTER INDEX GENERATOR V2 - QUALITY EDITION
--------------------------------------------
Uses filename-based category extraction with strict mapping to ground truth
Processes all 711 summaries and creates perfect master index

Run: python utils/master_index_generator_v2.py
"""

from pathlib import Path
from collections import defaultdict
import re

print("="*70)
print("  🏆 MASTER INDEX GENERATOR V2 - QUALITY EDITION")
print("="*70)

# GROUND TRUTH CATEGORIES (from GHL docs sidebar)
TRUE_CATEGORIES = {
    'oauth': 'OAuth 2.0',
    'oauth2': 'OAuth 2.0',
    'authorization': 'OAuth 2.0',
    'business': 'Business',
    'businesses': 'Business',
    'calendars': 'Calendars',
    'calendar': 'Calendars',
    'campaigns': 'Campaigns',
    'campaign': 'Campaigns',
    'companies': 'Companies',
    'company': 'Companies',
    'contacts': 'Contacts',
    'contact': 'Contacts',
    'objects': 'Objects',
    'object': 'Objects',
    'associations': 'Associations',
    'association': 'Associations',
    'customfields': 'Custom Fields V2',
    'custom-fields': 'Custom Fields V2',
    'conversations': 'Conversations',
    'conversation': 'Conversations',
    'courses': 'Courses',
    'course': 'Courses',
    'email': 'Email',
    'emails': 'Email',
    'forms': 'Forms',
    'form': 'Forms',
    'invoice': 'Invoice',
    'invoices': 'Invoice',
    'triggerlinks': 'Trigger Links',
    'trigger-links': 'Trigger Links',
    'medias': 'Media Storage',
    'media': 'Media Storage',
    'marketplace': 'Developer marketplace',
    'developer': 'Developer marketplace',
    'blogs': 'Blogs',
    'blog': 'Blogs',
    'funnels': 'Funnels',
    'funnel': 'Funnels',
    'opportunities': 'Opportunities',
    'opportunity': 'Opportunities',
    'payments': 'Payments',
    'payment': 'Payments',
    'products': 'Products',
    'product': 'Products',
    'saas': 'Saas',
    'snapshots': 'Snapshots',
    'snapshot': 'Snapshots',
    'socialplanner': 'Social Planner',
    'social-planner': 'Social Planner',
    'surveys': 'Surveys',
    'survey': 'Surveys',
    'users': 'Users',
    'user': 'Users',
    'workflows': 'Workflows',
    'workflow': 'Workflows',
    'lc-email': 'LC Email',
    'custommenus': 'Custom menus',
    'custom-menus': 'Custom menus',
    'voiceai': 'Voice AI',
    'voice-ai': 'Voice AI',
    'proposals': 'Proposals',
    'proposal': 'Proposals',
    'knowledgebase': 'Knowledge Base',
    'knowledge-base': 'Knowledge Base',
    'conversationai': 'Conversation AI',
    'conversation-ai': 'Conversation AI',
    'phonesystem': 'Phone System',
    'phone-system': 'Phone System',
    'store': 'Store',
    'agentstudio': 'AI Agent Studio',
    'agent-studio': 'AI Agent Studio',
    'webhooks': 'Webhooks',
    'webhook': 'Webhooks',
}

# Configuration
SOURCE_DIR = Path("outputs/pages")
OUTPUT_FILE = SOURCE_DIR / "GHL_API_MASTER_INDEX_V2.txt"

print(f"\n📁 Source: {SOURCE_DIR}")
print(f"💾 Output: {OUTPUT_FILE}")

# Find all summary files (exclude old master indexes)
summary_files = [
    f for f in SOURCE_DIR.glob("*_SUMMARY.txt")
    if 'MASTER_INDEX' not in f.name
]

if not summary_files:
    print("\n❌ No summary files found!")
    exit(1)

print(f"\n📄 Found {len(summary_files)} summary files")
print("\n⏳ Processing summaries...\n")

def extract_category_from_filename(filename):
    """Extract category from filename pattern."""
    # Pattern: marketplace-gohighlevel-com-docs-ghl-{CATEGORY}-{endpoint}
    
    # Remove .txt and _SUMMARY
    name = filename.replace('_SUMMARY.txt', '').replace('.txt', '')
    
    # Split by dashes
    parts = name.split('-')
    
    # Find 'ghl' index
    try:
        ghl_index = parts.index('ghl')
        # Category is usually right after 'ghl'
        if ghl_index + 1 < len(parts):
            category_part = parts[ghl_index + 1]
            
            # Map to true category
            category_lower = category_part.lower()
            if category_lower in TRUE_CATEGORIES:
                return TRUE_CATEGORIES[category_lower]
    except ValueError:
        pass
    
    # Fallback: check for category keywords anywhere in filename
    name_lower = name.lower()
    for key, value in TRUE_CATEGORIES.items():
        if key in name_lower:
            return value
    
    return "Other"

def parse_summary(summary_file):
    """Parse summary file and extract endpoint data."""
    try:
        content = summary_file.read_text(encoding='utf-8')
        
        endpoint_name = ""
        http_method = ""
        endpoint_url = ""
        full_url = ""
        
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Handle markdown headers (### 1. ENDPOINT NAME:)
            if "ENDPOINT NAME" in line.upper():
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    endpoint_name = lines[i].strip()
            
            elif "HTTP METHOD" in line.upper():
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    http_method = lines[i].strip().upper()
                    # Clean up method
                    if '`' in http_method:
                        http_method = http_method.replace('`', '')
                    # Handle things like "POST (inferred)"
                    http_method = http_method.split('(')[0].split()[0].strip()
            
            elif "ENDPOINT URL" in line.upper() and "FULL" not in line.upper():
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    endpoint_url = lines[i].strip().replace('`', '')
            
            elif "FULL URL" in line.upper():
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    full_url = lines[i].strip().replace('`', '')
            
            i += 1
        
        # Use full URL if endpoint URL not found
        if not endpoint_url and full_url:
            endpoint_url = full_url
        
        # Validate we have minimum data
        if endpoint_name and http_method:
            # Validate HTTP method
            valid_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
            if http_method not in valid_methods:
                http_method = "GET"  # Default fallback
            
            return {
                'name': endpoint_name,
                'method': http_method,
                'url': endpoint_url or 'Not specified'
            }
        
        return None
        
    except Exception as e:
        print(f"   ⚠️  Error processing {summary_file.name}: {e}")
        return None

# Process all summaries
endpoints_by_category = defaultdict(list)
all_endpoints = []
skipped = 0

for i, summary_file in enumerate(summary_files, 1):
    if i % 50 == 0:
        print(f"   Processed {i}/{len(summary_files)}...")
    
    # Get category from filename
    category = extract_category_from_filename(summary_file.name)
    
    # Skip "Other" category (non-endpoint docs)
    if category == "Other":
        skipped += 1
        continue
    
    # Parse endpoint data
    endpoint_data = parse_summary(summary_file)
    
    if endpoint_data:
        endpoint_data['category'] = category
        endpoints_by_category[category].append(endpoint_data)
        all_endpoints.append(endpoint_data)

print(f"\n✅ Processed {len(summary_files)} files")
print(f"✅ Found {len(all_endpoints)} valid endpoints")
print(f"⏭️  Skipped {skipped} non-endpoint files")
print(f"✅ Organized into {len(endpoints_by_category)} categories")

# Generate master index
print("\n📝 Generating master index...\n")

master_index = []

# Header
master_index.append("="*70)
master_index.append("GHL API v2 MASTER INDEX (QUALITY EDITION)")
master_index.append("Complete Reference for All API Endpoints")
master_index.append("Filename-based categorization with ground truth mapping")
master_index.append("="*70)
master_index.append("")

# SEARCHABLE ALIASES SECTION (NEW!)
master_index.append("🔍 QUICK SEARCH GUIDE:")
master_index.append("")
master_index.append("Common queries and where to find answers:")
master_index.append("")
master_index.append("• 'list all endpoints' → See 'ALL ENDPOINTS BY CATEGORY' below")
master_index.append("• 'show api list' → See 'ALL API CATEGORIES' below")
master_index.append("• 'how many endpoints' → See STATISTICS section below")
master_index.append("• 'api categories' → See 'ALL API CATEGORIES' below")
master_index.append("• 'category list' → See 'ALL API CATEGORIES' below")
master_index.append("• 'endpoint count' → See STATISTICS section below")
master_index.append("• 'create contact' → See CONTACTS category")
master_index.append("• 'contact endpoints' → See CONTACTS category")
master_index.append("• 'email endpoints' → See EMAIL category")
master_index.append("• 'calendar endpoints' → See CALENDARS category")
master_index.append("")
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
        if endpoint['url'] != 'Not specified':
            master_index.append(f"     URL: {endpoint['url']}")
    
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

print("✅ Master index V2 generated!")
print(f"   File: {OUTPUT_FILE}")
print(f"   Size: {len(master_index_text):,} chars")

print("\n📊 Summary:")
print(f"   • Categories: {len(endpoints_by_category)}")
print(f"   • Endpoints: {len(all_endpoints)}")

print("\n📋 Top 10 Categories:")
top_cats = sorted(endpoints_by_category.items(), key=lambda x: len(x[1]), reverse=True)[:10]
for cat, endpoints in top_cats:
    print(f"   • {cat}: {len(endpoints)} endpoints")

print("\n🎯 Next steps:")
print("   1. Review the master index")
print("   2. Delete old master index: python utils/delete_old_master_index.py")
print("   3. Upload new one: python utils/upload_master_index_v2.py")

print("\n" + "="*70)