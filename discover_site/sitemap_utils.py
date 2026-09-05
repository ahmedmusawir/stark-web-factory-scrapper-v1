import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

# One identity for the whole tool. Complete Chrome-shaped UA (Chrome/ + Safari/537.36 tokens)
# so crawl4ai derives a non-empty sec-ch-ua from it. The crawler imports this constant.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)

# Every discovery HTTP call goes through this session, so the UA is sent on all of them.
SESSION = requests.Session()
SESSION.headers["User-Agent"] = USER_AGENT

def fetch_sitemap_urls(base_url):
    sitemap_url = urljoin(base_url, "/sitemap.xml")
    print(f"[INFO] Checking sitemap at {sitemap_url}")

    try:
        response = SESSION.get(sitemap_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[WARNING] Failed to fetch sitemap: {e}")
        return []

    try:
        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # Check if it's a sitemap index
        sitemap_tags = root.findall(".//ns:sitemap/ns:loc", namespaces=namespace)
        if sitemap_tags:
            urls = []
            for sitemap_tag in sitemap_tags:
                child_sitemap_url = sitemap_tag.text
                print(f"[INFO] Parsing child sitemap: {child_sitemap_url}")
                try:
                    child_res = SESSION.get(child_sitemap_url, timeout=10)
                    child_res.raise_for_status()
                    child_root = ET.fromstring(child_res.content)
                    child_urls = [elem.text for elem in child_root.findall(".//ns:loc", namespaces=namespace)]
                    urls.extend(child_urls)
                except Exception as e:
                    print(f"[WARNING] Failed to fetch or parse child sitemap: {e}")
            return urls

        # Otherwise, treat it as a flat sitemap
        urls = [elem.text for elem in root.findall(".//ns:loc", namespaces=namespace)]
        return urls

    except ET.ParseError as e:
        print(f"[WARNING] Failed to parse sitemap XML: {e}")
        return []