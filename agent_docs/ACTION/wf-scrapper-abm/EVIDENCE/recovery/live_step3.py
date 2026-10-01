"""Recovery mission STEP 3 live driver: sitemap.xml -> page-sitemap.xml only -> pages?per_page=1 -> posts?per_page=1.
Usage (repo root): PYTHONPATH=.:<this dir> venv/bin/python live_step3.py <deadline_epoch>"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

from paced_get import PacedSession, Stopped

HERE = Path(__file__).resolve().parent
NS = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
HOSTS = {"cyberizegroup.com", "www.cyberizegroup.com"}
s = PacedSession(HERE / "live", HERE / "RECOVERY_LOG.md", deadline_epoch=float(sys.argv[1]))


def get(url, name):
    """One paced GET; a single in-scope redirect hop is followed as its own paced request."""
    r = s.get(url, name)
    if r.status_code in (301, 302, 307, 308):
        loc = r.headers.get("Location", "")
        if urlparse(loc).hostname in HOSTS:
            r = s.get(loc, name + ".hop")
    return r


try:
    r = get("https://cyberizegroup.com/sitemap.xml", "sitemap")
    if r.status_code != 200:
        raise Stopped(f"sitemap.xml status {r.status_code} — not proceeding")
    children = [e.text.strip() for e in ET.fromstring(r.content).findall(".//ns:sitemap/ns:loc", NS)]
    print("children:", children)
    page_sm = [c for c in children if c.rstrip("/").endswith("page-sitemap.xml")]
    if not page_sm:
        raise Stopped("no page-sitemap.xml child in the index")
    r = get(page_sm[0], "page-sitemap")
    if r.status_code != 200:
        raise Stopped(f"page-sitemap.xml status {r.status_code}")
    print("page-sitemap loc count:", len(ET.fromstring(r.content).findall(".//ns:url/ns:loc", NS)))
    for name in ("pages", "posts"):
        r = get(f"https://cyberizegroup.com/wp-json/wp/v2/{name}?per_page=1", f"rest-{name}")
        if r.status_code != 200:
            raise Stopped(f"{name} status {r.status_code}")
    print("STEP3 COMPLETE")
except Stopped as e:
    print("STOPPED:", e)
    sys.exit(3)
