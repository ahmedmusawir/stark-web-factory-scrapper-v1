import json
import argparse
from pathlib import Path
from urllib.parse import urlparse, urljoin

import asyncio
import sys
from bs4 import BeautifulSoup

from discover_site.sitemap_utils import canonical_url, discover

# Anchor to the repo root so the script works from any CWD (run as: python -m discover_site.discover <url>)
REPO_ROOT = Path(__file__).resolve().parents[1]
output_path = REPO_ROOT / 'outputs' / 'discovered_pages.json'

def is_valid_link(href, domain):
    if not href:
        return False
    if href.startswith("mailto:") or href.startswith("tel:"):
        return False
    parsed = urlparse(href)
    return (not parsed.netloc or parsed.netloc == domain) and not parsed.fragment

def normalize_link(href, base_url):
    return canonical_url(urljoin(base_url, href))

async def extract_internal_links(base_url, browser, out, bootstrap_html):
    routes, _, _ = await discover(base_url,browser,out,mode='homepage',bootstrap_html=bootstrap_html)
    return [r['url'] for r in routes['routes']]

def write_to_json(urls, output_path):
    data = [ {"url": url} for url in urls ]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[SUCCESS] Saved {len(data)} links to {output_path}")

def main():
    parser=argparse.ArgumentParser(description="Discover routes through a controlled Chromium session")
    parser.add_argument('url')
    parser.add_argument('--mode', choices=['sitemap','homepage'])
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.mode is None:
        if not sys.stdin.isatty(): parser.error('--mode is required without a TTY')
        choice=input('Discovery [1 sitemap / 2 homepage]: ').strip()
        if choice not in ('1','2'): parser.error('choose 1 or 2')
        args.mode='sitemap' if choice=='1' else 'homepage'
    if args.out.exists(): parser.error('--out must be a NEW directory; existing evidence is preserved')
    args.out.mkdir(parents=True)
    async def execute():
        from smart_crawler.browser_session import BrowserSession
        async with BrowserSession(args.url) as browser:
            bootstrap=await browser.capture(args.url)
            if not bootstrap['ok']: raise RuntimeError('bootstrap unavailable')
            routes,absences,state=await discover(args.url,browser,args.out,mode=args.mode,bootstrap_html=bootstrap['html'])
            for name,value in [('routes.json',routes),('absences.json',absences)]:
                with (args.out/name).open('x') as f: json.dump(value,f,indent=2)
            print(f'Discovery {state}: {len(routes["routes"])} routes')
    asyncio.run(execute())


if __name__ == '__main__':
    main()
