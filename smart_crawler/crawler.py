#!/usr/bin/env python3
"""
Batch crawler — one markdown file per discovered URL, via crawl4ai.

Run (from repo root): python -m smart_crawler.crawler [--input PATH] [--limit N]
Reads outputs/discovered_pages.json (override with --input PATH, cap with --limit N),
writes outputs/pages/<slug>.md and outputs/run_summary.json.

Pages are fetched one at a time with a random 2-5 s pause between them. A page is
failed when status_code >= 400 or the library reports success=False; failed pages
are recorded in run_summary.json and never written as content. 403/429 count as
"blocked"; three consecutive blocked pages stop the run.

Output is crawl4ai's raw_markdown (full page incl. nav) unless fit_markdown is
non-empty; no content filter is configured yet, so expect raw_markdown (deferred).
"""

from pathlib import Path
import argparse
import asyncio
import importlib.metadata
import json
import random
import re
import sys
from datetime import datetime, timezone
from typing import Sequence

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

from discover_site.sitemap_utils import USER_AGENT  # one identity for discovery and crawl

# ---------------------------------------------------------------------------
# Constants & paths
# ---------------------------------------------------------------------------
# Anchor to the repo root so the tool works from any CWD (same approach as discover.py).
# Nothing here touches the filesystem at import time; main() creates the directories.
REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "outputs"
PAGE_DIR = OUTPUT_DIR / "pages"
SUMMARY_PATH = OUTPUT_DIR / "run_summary.json"
DEFAULT_INPUT = OUTPUT_DIR / "discovered_pages.json"
# bim001: run folders live under RUN_ROOT / <project> / runs / <run_id>. Tests redirect RUN_ROOT.
RUN_ROOT = OUTPUT_DIR

# bim001: explicit project identity (R3-A). Validated in main(), not by argparse.
PROJECT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
CANONICAL_EXAMPLE = "python -m smart_crawler.crawler --project CyberizeGroup --limit 10"
HELP_HINT = "python -m smart_crawler.crawler --help"

BLOCKED_STATUSES = {403, 429}
MAX_CONSECUTIVE_BLOCKED = 3
PAUSE_RANGE_S = (2, 5)  # uniform random pause between pages, seconds

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Convert URL to safe filename."""
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-") or "root"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_run_id(started_at: str) -> str:
    """'2026-09-06T14:30:00+00:00' -> '2026-09-06T14-30-00Z' (filesystem-safe, same instant)."""
    return started_at[:19].replace(":", "-") + "Z"


def validate_project(name: str | None) -> str | None:
    """Return None if the project name is acceptable, else 'required' or 'invalid'."""
    if name is None:
        return "required"
    if not PROJECT_RE.match(name):
        return "invalid"
    return None


def print_project_usage(kind: str, value: str | None) -> None:
    """Corrective usage for a missing/invalid --project (AC-03/04/05/06). Goes to stderr."""
    if kind == "required":
        print("❌ --project is required. Name the project this run belongs to.", file=sys.stderr)
    else:
        print(f"❌ --project is invalid: {value!r}. Allowed: letters, digits, '-' and '_'; "
              "1-64 characters; must start with a letter or digit.", file=sys.stderr)
    print(f"   Example: {CANONICAL_EXAMPLE}", file=sys.stderr)
    print(f"   Help:    {HELP_HINT}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Core crawl helpers
# ---------------------------------------------------------------------------

async def crawl_page(crawler: "AsyncWebCrawler", url: str) -> dict:
    """Crawl one URL. Returns a page record for run_summary plus the markdown (if ok).

    Failure rules: status_code >= 400, or result.success False, is a failed page.
    403/429 are recorded as error "blocked". Failed pages carry no markdown.
    """
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        page_timeout=90000,              # 90 seconds
        delay_before_return_html=3.0,    # Wait 3s after page load
        wait_for_images=True,            # Wait for all images
    )

    started = asyncio.get_event_loop().time()
    record = {"url": url, "status": None, "ok": False, "elapsed_s": 0.0, "error": None}
    markdown = ""

    try:
        result = await crawler.arun(url=url, config=run_config)
    except Exception as e:
        record["error"] = f"exception: {e}"
        record["elapsed_s"] = round(asyncio.get_event_loop().time() - started, 1)
        return {**record, "markdown": ""}

    record["elapsed_s"] = round(asyncio.get_event_loop().time() - started, 1)

    if not result:
        record["error"] = "no result object"
        return {**record, "markdown": ""}

    status = getattr(result, "status_code", None)
    success = bool(getattr(result, "success", False))
    record["status"] = status

    if status in BLOCKED_STATUSES:
        record["error"] = "blocked"
        return {**record, "markdown": ""}

    if (status is not None and status >= 400) or not success:
        # crawl4ai 0.9.x sets error_message (e.g. "Blocked by anti-bot protection: ...")
        record["error"] = getattr(result, "error_message", None) or f"HTTP {status}"
        return {**record, "markdown": ""}

    md = getattr(result, "markdown", None)
    if md is None:
        record["error"] = "no markdown in result"
        return {**record, "markdown": ""}

    # Prefer fit_markdown when present; fall back to raw_markdown (no content filter configured yet)
    fit_md = getattr(md, "fit_markdown", "") or ""
    raw_md = getattr(md, "raw_markdown", "") or ""
    markdown = (fit_md or raw_md).strip()
    if not markdown:
        record["error"] = "empty markdown"
        return {**record, "markdown": ""}

    record["ok"] = True
    return {**record, "markdown": markdown}


def save_markdown(url: str, markdown: str) -> Path | None:
    """Write one page's markdown to PAGE_DIR/<slug>.md."""
    name = slugify(url.replace("https://", "").replace("http://", ""))
    out_path = PAGE_DIR / f"{name}.md"
    try:
        out_path.write_text(markdown, encoding="utf-8")
        return out_path
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return None


def write_summary(pages: list[dict], started_at: str, finished_at: str) -> Path:
    summary = {
        "started_at": started_at,
        "finished_at": finished_at,
        "crawl4ai_version": importlib.metadata.version("crawl4ai"),
        "pause_range_s": list(PAUSE_RANGE_S),
        "pages": pages,
    }
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return SUMMARY_PATH


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def read_urls(path: Path) -> list[str]:
    """Read every URL from the discovery JSON (dicts with "url" or bare strings). Exits 1 on error."""
    if not path.exists():
        print(f"❌ File not found: {path}")
        print("   Run discovery first: python -m discover_site.discover <url>")
        sys.exit(1)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [d["url"] if isinstance(d, dict) else str(d) for d in data if d]
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading URLs: {e}")
        sys.exit(1)


def load_urls(path: Path, limit: int | None = None) -> Sequence[str]:
    """Load URLs from the discovery JSON; keep only the first `limit` if given."""
    urls = read_urls(path)
    return urls[:limit] if limit is not None else urls


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl discovered pages to markdown + raw HTML")
    parser.add_argument("--project", default=None,
                        help="project name this run belongs to (required; validated at runtime)")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                        help=f"discovery JSON to read (default: {DEFAULT_INPUT})")
    parser.add_argument("--limit", type=int, default=None,
                        help="crawl only the first N URLs (default: all)")
    args = parser.parse_args(argv)
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be >= 1")
    return args


async def crawl_all(urls: Sequence[str], crawler: "AsyncWebCrawler") -> tuple[list[dict], bool]:
    """Crawl URLs sequentially with an already-open crawler.

    Returns (page records, stopped_early). Stops after MAX_CONSECUTIVE_BLOCKED
    consecutive 403/429 pages. Prints one status line per page.
    """
    pages: list[dict] = []
    consecutive_blocked = 0
    total = len(urls)

    for i, url in enumerate(urls, 1):
        if i > 1:
            pause = random.uniform(*PAUSE_RANGE_S)
            print(f"⏸ pause {pause:.1f}s")
            await asyncio.sleep(pause)
        page = await crawl_page(crawler, url)
        markdown = page.pop("markdown")

        if page["ok"]:
            consecutive_blocked = 0
            saved = save_markdown(url, markdown)
            if saved is None:
                page["ok"] = False
                page["error"] = "write failed"
            print(f"[{i}/{total}] {page['status']} ok {page['elapsed_s']}s {url}"
                  + (f" -> {saved.name} ({len(markdown):,} chars)" if saved else ""))
        else:
            label = "BLOCKED" if page["error"] == "blocked" else "FAILED"
            print(f"[{i}/{total}] {page['status']} {label} {page['elapsed_s']}s {url} — {page['error']}")
            if page["error"] == "blocked":
                consecutive_blocked += 1
            else:
                consecutive_blocked = 0

        pages.append(page)

        if consecutive_blocked >= MAX_CONSECUTIVE_BLOCKED:
            print(f"\n⛔ {MAX_CONSECUTIVE_BLOCKED} consecutive blocked pages (403/429) — stopping run. "
                  f"{total - i} URL(s) not attempted.")
            return pages, True

    return pages, False


async def run(urls: Sequence[str]) -> tuple[list[dict], bool]:
    browser_config = BrowserConfig(headless=True, user_agent=USER_AGENT)
    async with AsyncWebCrawler(config=browser_config) as crawler:
        return await crawl_all(urls, crawler)


def main() -> None:
    """Main entry point."""
    args = parse_args()

    problem = validate_project(args.project)
    if problem:
        print_project_usage(problem, args.project)
        sys.exit(2)

    urls = list(load_urls(args.input, args.limit))

    if not urls:
        # Still a run: write a truthful summary (pages=[]) so no stale prior-run file survives.
        print("⚠️  No URLs found in file — nothing to crawl")
        now = utc_now()
        print(f"🧾 Summary: {write_summary([], now, now)}")
        return

    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    version = importlib.metadata.version("crawl4ai")
    est_min = len(urls) * (7 + sum(PAUSE_RANGE_S) / 2) / 60  # ~7 s/page observed + mean pause

    print("\n" + "=" * 80)
    print(f"Batch crawler — crawl4ai {version}")
    print("=" * 80)
    print(f"\nReady to crawl {len(urls)} URL(s)")
    print(f"From: {args.input}")
    print(f"To:   {PAGE_DIR}")
    print(f"Pause between pages: {PAUSE_RANGE_S[0]}-{PAUSE_RANGE_S[1]} s (random)")
    print(f"Estimated time: ~{est_min:.1f} min")

    print("\nFirst 5 URLs:")
    for u in urls[:5]:
        print(f"  • {u}")
    if len(urls) > 5:
        print(f"  ... and {len(urls) - 5} more")
    print()

    started_at = utc_now()
    pages, stopped_early = asyncio.run(run(urls))
    finished_at = utc_now()
    summary_path = write_summary(pages, started_at, finished_at)

    successful = sum(1 for p in pages if p["ok"])
    failed = len(pages) - successful
    blocked = sum(1 for p in pages if p["error"] == "blocked")

    print("\n" + "="*80)
    print("✅ CRAWL COMPLETE" if not stopped_early else "⛔ CRAWL STOPPED EARLY")
    print("="*80)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}  (blocked: {blocked})")
    print(f"📁 Files saved to: {PAGE_DIR}")
    print(f"🧾 Summary: {summary_path}")

    if successful > 0:
        saved = [PAGE_DIR / f"{slugify(p['url'].replace('https://','').replace('http://',''))}.md" for p in pages if p["ok"]]
        total_size = sum(p.stat().st_size for p in saved if p.exists())
        print(f"\n📊 Quality Stats:")
        print(f"   Total size: {total_size / 1024 / 1024:.1f} MB")
        print(f"   Average per file: {total_size / successful / 1024:.1f} KB")
        print(f"   Success rate: {(successful / len(urls)) * 100:.1f}%")

    if stopped_early:
        sys.exit(2)


if __name__ == "__main__":
    main()
