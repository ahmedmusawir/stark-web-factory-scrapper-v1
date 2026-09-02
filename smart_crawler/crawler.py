#!/usr/bin/env python3
"""
UPGRADED BATCH CRAWLER - Crawl4AI v0.6.x
-----------------------------------------
Processes all URLs with AI-cleaned markdown (fit_markdown)
Superior quality output - removes navigation junk automatically

Run (from repo root): python -m smart_crawler.crawler
Reads outputs/discovered_pages_final.json, writes outputs/pages/*.md
"""

from pathlib import Path
import asyncio
import json
import re
import sys
from typing import Sequence

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# ---------------------------------------------------------------------------
# Constants & paths
# ---------------------------------------------------------------------------
BASE_DIR = Path.cwd()
OUTPUT_DIR = BASE_DIR / "outputs"
PAGE_DIR = OUTPUT_DIR / "pages"  # New folder to keep old ones
PAGE_DIR.mkdir(parents=True, exist_ok=True)
URL_FILE = OUTPUT_DIR / "discovered_pages_final.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Convert URL to safe filename."""
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-") or "root"


# ---------------------------------------------------------------------------
# Core crawl helpers
# ---------------------------------------------------------------------------

async def fetch_markdown(crawler: "AsyncWebCrawler", url: str) -> str:
    """Fetch and return cleaned markdown using fit_markdown."""
    print(f"🔍 Fetching: {url}")

    # UPGRADED SETTINGS - v0.7.x patterns
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        page_timeout=90000,              # 90 seconds
        delay_before_return_html=3.0,    # Wait 3s after page load
        wait_for_images=True,            # Wait for all images
    )

    try:
        result = await crawler.arun(url=url, config=run_config)
    except Exception as e:
        print(f"❌ Exception during crawl: {e}")
        return ""

    if not result:
        print(f"⚠️  No result object returned")
        return ""

    if not result.success:
        print(f"⚠️  Crawl failed")
        if hasattr(result, 'status_code') and result.status_code:
            print(f"   Status: {result.status_code}")
        if hasattr(result, 'error_message') and result.error_message:
            print(f"   Error: {result.error_message}")
        return ""

    if result.markdown is None:
        print(f"⚠️  No markdown in result")
        return ""

    # PRIORITIZE fit_markdown (AI-cleaned, navigation removed)
    fit_md = getattr(result.markdown, "fit_markdown", "")
    raw_md = getattr(result.markdown, "raw_markdown", "")

    final_markdown = ""
    
    if fit_md:
        final_markdown = fit_md.strip()
        reduction = ((len(raw_md) - len(fit_md)) / len(raw_md)) * 100 if raw_md else 0
        print(f"✅ Using fit_markdown ({len(final_markdown):,} chars, {reduction:.0f}% cleaner)")
    elif raw_md:
        print(f"⚠️  fit_markdown empty, using raw_markdown")
        final_markdown = raw_md.strip()
        print(f"✅ Using raw_markdown ({len(final_markdown):,} chars)")
    
    if not final_markdown:
        print(f"❌ Both markdown versions are empty!")
        return ""
    
    # Quality check
    if len(final_markdown) < 500:
        print(f"⚠️  Warning: Very short content ({len(final_markdown)} chars)")
    
    return final_markdown


async def process_file(crawler: "AsyncWebCrawler", url: str) -> Path | None:
    """Crawl a URL and save to markdown file."""
    print(f"\n{'='*80}")
    print(f"Processing: {url}")
    print(f"{'='*80}")
    
    markdown = await fetch_markdown(crawler, url)

    if not markdown:
        print(f"❌ Skipping (no content)\n")
        return None
    
    # Save to file
    name = slugify(url.replace("https://", "").replace("http://", ""))
    out_path = PAGE_DIR / f"{name}.md"
    
    try:
        out_path.write_text(markdown, encoding="utf-8")
        print(f"✅ Saved: {out_path.relative_to(BASE_DIR)}")
        print(f"   Size: {len(markdown):,} chars\n")
        return out_path
    except Exception as e:
        print(f"❌ Error writing file: {e}\n")
        return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def load_urls() -> Sequence[str]:
    """Load URLs from JSON file."""
    if not URL_FILE.exists():
        print(f"❌ File not found: {URL_FILE}")
        print("   Run discovery first!")
        sys.exit(1)

    try:
        data = json.loads(URL_FILE.read_text(encoding="utf-8"))
        urls = [d["url"] if isinstance(d, dict) else str(d) for d in data if d]
        return urls
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading URLs: {e}")
        sys.exit(1)


async def crawl_all(urls: Sequence[str]):
    """Crawl all URLs with upgraded crawler."""
    browser_config = BrowserConfig(
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = []
        successful = 0
        failed = 0
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Starting...")
            result = await process_file(crawler, url)
            
            if result:
                successful += 1
                results.append(result)
            else:
                failed += 1
            
            # Progress update every 10 URLs
            if i % 10 == 0:
                print(f"\n📊 Progress: {i}/{len(urls)} | ✅ {successful} | ❌ {failed}\n")
        
        return results, successful, failed


def main() -> None:
    """Main entry point."""
    urls = list(load_urls())
    
    if not urls:
        print("⚠️  No URLs found in file")
        return

    print("\n" + "="*80)
    print(f"🚀 UPGRADED BATCH CRAWLER - v0.7.x")
    print("="*80)
    print(f"\n📋 Ready to crawl {len(urls)} URLs")
    print(f"📂 From: {URL_FILE}")
    print(f"💾 To: {PAGE_DIR}")
    print("\n✨ Using fit_markdown (AI-cleaned output)")
    print("   - Removes navigation junk")
    print("   - Cleaner, smaller files")
    
    print("\n📄 First 5 URLs:")
    for u in urls[:5]:
        print(f"  • {u}")
    if len(urls) > 5:
        print(f"  ... and {len(urls) - 5} more")

    try:
        proceed = input("\n⚡ Proceed with batch crawl? (y/n): ").strip().lower()
    except KeyboardInterrupt:
        print("\n\n❌ Aborted by user")
        return
        
    if proceed != "y":
        print("❌ Aborted")
        return

    print("\n" + "="*80)
    print("🚀 STARTING BATCH CRAWL")
    print("="*80)
    print("⏱️  This will take ~30-40 minutes for 707 URLs")
    print("   Grab a coffee! ☕\n")
    
    results, successful, failed = asyncio.run(crawl_all(urls))
    
    print("\n" + "="*80)
    print("✅ BATCH CRAWL COMPLETE!")
    print("="*80)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Files saved to: {PAGE_DIR}")
    
    if results:
        print(f"\n📄 Sample files created:")
        for p in results[:5]:
            size_kb = p.stat().st_size / 1024
            print(f"  • {p.name} ({size_kb:.1f} KB)")
        if len(results) > 5:
            print(f"  ... and {len(results) - 5} more")
    
    # Quality summary
    if successful > 0:
        total_size = sum(p.stat().st_size for p in results)
        avg_size = total_size / successful
        print(f"\n📊 Quality Stats:")
        print(f"   Total size: {total_size / 1024 / 1024:.1f} MB")
        print(f"   Average per file: {avg_size / 1024:.1f} KB")
        print(f"   Success rate: {(successful / len(urls)) * 100:.1f}%")
    

if __name__ == "__main__":
    main()