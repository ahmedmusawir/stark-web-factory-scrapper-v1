"""P0 Part D REST probe (R6). Three GETs, 3 s apart, project USER_AGENT, global requests.
Saves raw body bytes + headers per request. Run from the repo root."""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from discover_site.sitemap_utils import USER_AGENT

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
PROBES = [
    ("root", "https://cyberizegroup.com/wp-json/"),
    ("pages", "https://cyberizegroup.com/wp-json/wp/v2/pages?per_page=1"),
    ("posts", "https://cyberizegroup.com/wp-json/wp/v2/posts?per_page=1"),
]

meta = {"requests_version": requests.__version__, "python": sys.version.split()[0],
        "user_agent": USER_AGENT, "probes": []}
for i, (name, url) in enumerate(PROBES):
    if i:
        time.sleep(3)
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    started = time.monotonic()
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    except requests.RequestException as e:
        meta["probes"].append({"name": name, "url": url, "at": at, "error": repr(e)})
        continue
    (OUT / f"{name}.body.json").write_bytes(resp.content)
    (OUT / f"{name}.headers.json").write_text(json.dumps(dict(resp.headers), indent=2), encoding="utf-8")
    meta["probes"].append({
        "name": name, "url": url, "at": at, "status": resp.status_code,
        "final_url": resp.url, "history": [h.status_code for h in resp.history],
        "elapsed_s": round(time.monotonic() - started, 2), "body_bytes": len(resp.content),
        "content_type": resp.headers.get("Content-Type"),
        "x_wp_total": resp.headers.get("X-WP-Total"),
        "x_wp_totalpages": resp.headers.get("X-WP-TotalPages"),
    })
(OUT / "probe_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print(json.dumps(meta, indent=2))
