"""
Smart URL Discovery V2 - AGGRESSIVE MODE
-----------------------------------------
Handles DEEPLY NESTED navigation (multiple levels of dropdowns)

Strategy:
1. Load page with full JavaScript
2. Find ALL dropdown toggles (any level)
3. Click them ALL repeatedly until no more can be expanded
4. Wait for animations between rounds
5. Extract ALL links from fully-expanded sidebar
6. Filter out junk and duplicates

Perfect for complex doc sites with nested navigation!
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

# Output path
OUTPUT_FILE = Path("outputs/discovered_pages_final.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


async def discover_urls_v2(base_url: str) -> list[str]:
    """
    Aggressively discover ALL documentation URLs by recursively expanding navigation.
    
    Args:
        base_url: The documentation page URL (must have sidebar)
        
    Returns:
        List of unique documentation URLs
    """
    print(f"🚀 Starting AGGRESSIVE discovery for: {base_url}\n")
    
    async with async_playwright() as p:
        # Launch browser
        print("⏳ Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to docs
        print(f"⏳ Loading page...")
        await page.goto(base_url, wait_until="networkidle")
        
        # Wait for sidebar to render
        print("⏳ Waiting for sidebar to render...")
        await page.wait_for_selector('.theme-doc-sidebar-menu, .sidebar, nav[class*="sidebar"]', timeout=10000)
        
        # AGGRESSIVE EXPANSION - Keep clicking until nothing left to click!
        print("🔽 Starting RECURSIVE dropdown expansion...\n")
        
        total_clicks = 0
        round_num = 1
        
        # Keep trying to expand dropdowns until we can't find any more
        while True:
            print(f"   Round {round_num}: Looking for collapsed dropdowns...")
            
            # Try multiple selector strategies for collapsed elements
            selectors_to_try = [
                'button[aria-expanded="false"]',                    # Standard ARIA
                'li[class*="collapsed"] > div',                     # Collapsed list items
                'li[class*="collapsed"] > a',                       # Collapsed links
                '.menu__list-item--collapsed',                      # Docusaurus specific
                '[class*="collapsible"]:not([class*="expanded"])',  # Generic collapsible
                'summary:not([open])',                              # HTML details/summary
                'li:has(ul[style*="display: none"]) > div',        # Hidden children
            ]
            
            clicks_this_round = 0
            
            for selector in selectors_to_try:
                elements = await page.query_selector_all(selector)
                
                for element in elements:
                    try:
                        # Check if visible and clickable
                        if await element.is_visible():
                            await element.click()
                            clicks_this_round += 1
                            total_clicks += 1
                            # Small delay for animation
                            await asyncio.sleep(0.05)
                    except Exception:
                        # Element might be stale or not clickable, skip
                        pass
            
            print(f"   Round {round_num}: Clicked {clicks_this_round} elements")
            
            # If we found nothing to click, we're done!
            if clicks_this_round == 0:
                print(f"\n✅ Expansion complete after {round_num} rounds!")
                print(f"✅ Total clicks: {total_clicks}\n")
                break
            
            round_num += 1
            
            # Safety limit (prevent infinite loops)
            if round_num > 20:
                print(f"\n⚠️  Reached safety limit (20 rounds). Stopping.\n")
                break
            
            # Wait a bit longer between rounds for complex animations
            await asyncio.sleep(0.5)
        
        # Final wait to ensure everything is rendered
        print("⏳ Waiting for final rendering...")
        await asyncio.sleep(2)
        
        # Extract all links from sidebar
        print("🔗 Extracting ALL links from sidebar...\n")
        
        # Try multiple sidebar selectors
        sidebar_selectors = [
            '.theme-doc-sidebar-menu a',      # Docusaurus
            'nav[class*="sidebar"] a',         # Generic
            '.sidebar a',                      # Generic
            '[role="navigation"] a',           # Accessibility
            'aside a',                         # Semantic HTML
        ]
        
        all_links = set()
        for selector in sidebar_selectors:
            links = await page.query_selector_all(selector)
            for link in links:
                try:
                    href = await link.get_attribute('href')
                    if href:
                        # Convert relative URLs to absolute
                        if href.startswith('/'):
                            from urllib.parse import urlparse
                            parsed = urlparse(base_url)
                            href = f"{parsed.scheme}://{parsed.netloc}{href}"
                        elif href.startswith('http'):
                            pass  # Already absolute
                        else:
                            continue  # Skip relative paths
                        
                        all_links.add(href)
                except Exception:
                    pass
        
        await browser.close()
        
        # Filter and clean URLs
        print("🧹 Filtering and cleaning URLs...\n")
        
        from urllib.parse import urlparse
        base_domain = urlparse(base_url).netloc
        
        filtered_links = []
        for url in sorted(all_links):
            # Must be same domain
            if urlparse(url).netloc != base_domain:
                continue
            
            # Must contain /docs/
            if '/docs/' not in url:
                continue
            
            # Skip category pages (they usually end with /category/)
            if '/category/' in url:
                continue
            
            # Remove anchors
            if '#' in url:
                url = url.split('#')[0]
            
            # Remove query parameters
            if '?' in url:
                url = url.split('?')[0]
            
            # Skip homepage itself
            if url.rstrip('/') == base_url.rstrip('/'):
                continue
            
            # Add if not duplicate
            if url not in filtered_links:
                filtered_links.append(url)
        
        print(f"✅ Found {len(filtered_links)} unique documentation pages!\n")
        
        return filtered_links


async def main():
    """Main entry point."""
    import sys
    
    # Get URL from command line or use default
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        print("❌ Error: Please provide a URL")
        print("\nUsage: python smart_discover_v2.py <url-with-sidebar>")
        print("\nExample:")
        print("  python smart_discover_v2.py https://example.com/docs/getting-started")
        return
    
    # Discover URLs
    try:
        urls = await discover_urls_v2(base_url)
    except Exception as e:
        print(f"❌ Error during discovery: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if not urls:
        print("❌ No URLs discovered. The site structure may not match expected patterns.")
        return
    
    # Save to JSON
    data = [{"url": url} for url in urls]
    OUTPUT_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    print(f"💾 Saved to: {OUTPUT_FILE}\n")
    
    # Preview first 15
    print("📋 Preview (first 15 URLs):")
    for url in urls[:15]:
        print(f"  • {url}")
    
    if len(urls) > 15:
        print(f"  ... and {len(urls) - 15} more\n")
    
    # Show some examples of different URL types found
    print("🔍 URL Pattern Analysis:")
    
    # Count different patterns
    patterns = {}
    for url in urls:
        path = url.replace('https://marketplace.gohighlevel.com/docs/', '')
        parts = path.split('/')
        if len(parts) >= 2:
            category = f"{parts[0]}/{parts[1]}"
            patterns[category] = patterns.get(category, 0) + 1
    
    print(f"   Found {len(patterns)} different categories")
    print("   Top categories:")
    for cat, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"     • {cat}: {count} pages")
    
    print("\n🎉 Discovery complete! Ready to crawl.")


if __name__ == "__main__":
    asyncio.run(main())