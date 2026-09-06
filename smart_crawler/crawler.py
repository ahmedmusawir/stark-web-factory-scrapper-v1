#!/usr/bin/env python3
"""
Batch crawler — one markdown file per discovered URL, via crawl4ai.

Run (from repo root): python -m smart_crawler.crawler --project NAME [--input PATH] [--limit N]
Reads outputs/discovered_pages.json (override with --input PATH, cap with --limit N),
writes outputs/pages/<slug>.md and outputs/run_summary.json (bim000 contract, unchanged), and
the bim001 run folder outputs/<project>/runs/<run_id>/{html/, manifest.json, absences.json, stage_log.txt}.
`--project NAME` is required (validated at runtime, no default).

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
import platform
import random
import re
import sys
import time
from datetime import datetime, timezone
from typing import Sequence
from urllib.parse import urlparse

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
    # Transport-only keys (popped by crawl_all before the record reaches run_summary.json):
    #   markdown - bim000 content; html - bim001 raw HTML (None when the result has none);
    #   fetched  - True once the status/success gate is passed, i.e. the server answered usefully.
    not_fetched = {"markdown": "", "html": None, "fetched": False}

    try:
        result = await crawler.arun(url=url, config=run_config)
    except Exception as e:
        record["error"] = f"exception: {e}"
        record["elapsed_s"] = round(asyncio.get_event_loop().time() - started, 1)
        return {**record, **not_fetched}

    record["elapsed_s"] = round(asyncio.get_event_loop().time() - started, 1)

    if not result:
        record["error"] = "no result object"
        return {**record, **not_fetched}

    status = getattr(result, "status_code", None)
    success = bool(getattr(result, "success", False))
    record["status"] = status

    if status in BLOCKED_STATUSES:
        record["error"] = "blocked"
        return {**record, **not_fetched}

    if (status is not None and status >= 400) or not success:
        # crawl4ai 0.9.x sets error_message (e.g. "Blocked by anti-bot protection: ...")
        record["error"] = getattr(result, "error_message", None) or f"HTTP {status}"
        return {**record, **not_fetched}

    # Fetched. Raw HTML is captured independently of markdown (AC-27); guarded because stubs
    # and future library versions may lack the attribute (AC-26 -> "unsupported").
    html = getattr(result, "html", None) or None
    fetched = {"html": html, "fetched": True}

    md = getattr(result, "markdown", None)
    if md is None:
        record["error"] = "no markdown in result"
        return {**record, "markdown": "", **fetched}

    # Prefer fit_markdown when present; fall back to raw_markdown (no content filter configured yet)
    fit_md = getattr(md, "fit_markdown", "") or ""
    raw_md = getattr(md, "raw_markdown", "") or ""
    markdown = (fit_md or raw_md).strip()
    if not markdown:
        record["error"] = "empty markdown"
        return {**record, "markdown": "", **fetched}

    record["ok"] = True
    return {**record, "markdown": markdown, **fetched}


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
# bim001 — run folder: outputs/<project>/runs/<run_id>/{html/, manifest.json, absences.json, stage_log.txt}
# ---------------------------------------------------------------------------

MANIFEST_SCHEMA = "bim001-manifest-v1"
ACCESS_RUNG = "a"          # plain headless fetch, no stealth (Stealth ruling)
OUTCOMES = ("captured", "blocked", "failed", "unsupported")


class RunFolder:
    """One crawl run's evidence folder. Nothing touches the filesystem until create()."""

    def __init__(self, project: str, started_at: str, root: Path | None = None):
        self.project = project
        self.root = root if root is not None else RUN_ROOT
        self.pages: list[dict] = []          # manifest page entries, attempt order
        self._slug_counts: dict[str, int] = {}
        self._set_started(started_at)

    def _set_started(self, started_at: str) -> None:
        self.started_at = started_at
        self.run_id = make_run_id(started_at)
        self.dir = self.root / self.project / "runs" / self.run_id
        self.html_dir = self.dir / "html"

    @property
    def run_dir_rel(self) -> str:
        return f"outputs/{self.project}/runs/{self.run_id}"

    def create(self) -> "RunFolder":
        """Create the folder. If a run with this run_id already exists (same second),
        wait for the clock to move and take the next second (I-3 ruling: never share a folder)."""
        while self.dir.exists():
            time.sleep(0.2)
            self._set_started(utc_now())
        self.html_dir.mkdir(parents=True)
        return self

    def log(self, line: str) -> None:
        with (self.dir / "stage_log.txt").open("a", encoding="utf-8") as fh:
            fh.write(f"{utc_now()} {line}\n")

    def allocate_slug(self, base: str) -> str:
        """First use -> base; later uses in the same run -> base-2, base-3, ... (R4)."""
        n = self._slug_counts.get(base, 0) + 1
        self._slug_counts[base] = n
        return base if n == 1 else f"{base}-{n}"

    def save_html(self, slug: str, html: str) -> tuple[str, int]:
        """Write html byte-for-byte (utf-8) to html/<slug>.html. Returns (relative file, byte count)."""
        data = html.encode("utf-8")
        target = self.html_dir / f"{slug}.html"
        if target.exists():
            raise FileExistsError(f"refusing to overwrite {target.name}")
        target.write_bytes(data)
        return f"html/{slug}.html", len(data)

    def record_page(self, record: dict, *, slug: str, outcome: str, reason: str | None = None,
                    html_file: str | None = None, html_bytes: int | None = None,
                    md_file: str | None = None) -> dict:
        """Manifest entry: the run_summary record's five values verbatim + six bim001 fields."""
        assert outcome in OUTCOMES, outcome
        entry = {
            "url": record["url"], "status": record["status"], "ok": record["ok"],
            "elapsed_s": record["elapsed_s"], "error": record["error"],
            "slug": slug, "outcome": outcome, "reason": reason,
            "html_file": html_file, "html_bytes": html_bytes, "md_file": md_file,
        }
        self.pages.append(entry)
        return entry

    def write_manifest(self, *, command: str, input_path: Path, input_total: int, limit: int | None,
                       input_hosts: list[str], finished_at: str, stopped_early: bool) -> Path:
        manifest = {
            "schema": MANIFEST_SCHEMA,
            "project_name": self.project,
            "run_id": self.run_id,
            "run_dir": self.run_dir_rel,
            "started_at": self.started_at,
            "finished_at": finished_at,
            "command": command,
            "input_path": str(input_path),
            "input_total": input_total,
            "limit": limit,
            "input_hosts": input_hosts,
            "access_rung": ACCESS_RUNG,
            "fallbacks_fired": [],
            "stopped_early": stopped_early,
            "crawl4ai_version": importlib.metadata.version("crawl4ai"),
            "playwright_version": importlib.metadata.version("playwright"),  # metadata lookup only (I-1 ruling)
            "python_version": platform.python_version(),
            # Mirrors of the CrawlerRunConfig literals in crawl_page (kept literal there for AC-62).
            "wait_for_images": True,
            "delay_before_return_html_s": 3.0,
            "page_timeout_ms": 90000,
            "pause_range_s": list(PAUSE_RANGE_S),
            "summary_path": "outputs/run_summary.json",
            "pages": self.pages,
        }
        assert len(manifest) == 23, len(manifest)
        path = self.dir / "manifest.json"
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return path

    def write_absences(self, absences: list[dict]) -> Path:
        path = self.dir / "absences.json"
        path.write_text(json.dumps(absences, indent=2), encoding="utf-8")
        return path


def build_absences(pages: list[dict], attempted: Sequence[str], all_urls: Sequence[str]) -> list[dict]:
    """Every input URL not captured: attempted-and-absent first (attempt order), then skipped (input order)."""
    absences = [{"url": p["url"], "outcome": p["outcome"], "reason": p["reason"]}
                for p in pages if p["outcome"] != "captured"]
    absences += [{"url": u, "outcome": "skipped", "reason": "stop_rule"} for u in attempted[len(pages):]]
    absences += [{"url": u, "outcome": "skipped", "reason": "limit"} for u in all_urls[len(attempted):]]
    return absences


def input_hosts(urls: Sequence[str]) -> list[str]:
    return sorted({urlparse(u).netloc for u in urls})

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


def record_capture(run: RunFolder, page: dict, url: str, html: str | None, fetched: bool,
                   md_saved: bool) -> dict:
    """bim001: decide the page's outcome, save its HTML if captured, and record it in the run folder.

    blocked (403/429) > failed (fetch failed) > unsupported (fetched, no html) > captured / write failure.
    md_file names the markdown file bim000 actually wrote (I-2 ruling), or None.
    """
    base = slugify(url.replace("https://", "").replace("http://", ""))
    md_file = f"pages/{base}.md" if md_saved else None
    html_file = html_bytes = None
    slug = base

    if page["error"] == "blocked":
        outcome, reason = "blocked", "blocked"
    elif not fetched:
        outcome, reason = "failed", page["error"] or "fetch failed"
    elif not html:
        outcome, reason = "unsupported", "no html in result"
    else:
        slug = run.allocate_slug(base)
        try:
            html_file, html_bytes = run.save_html(slug, html)
            outcome, reason = "captured", None
        except Exception as e:  # AC-28: a write failure is a failure, not a crash
            outcome, reason = "failed", f"write failed: {e}"

    entry = run.record_page(page, slug=slug, outcome=outcome, reason=reason,
                            html_file=html_file, html_bytes=html_bytes, md_file=md_file)
    run.log(f"{outcome} {url}" + (f" ({reason})" if reason and outcome != "blocked" else ""))
    return entry


async def crawl_all(urls: Sequence[str], crawler: "AsyncWebCrawler",
                    run: RunFolder | None = None) -> tuple[list[dict], bool]:
    """Crawl URLs sequentially with an already-open crawler.

    Returns (page records, stopped_early). Stops after MAX_CONSECUTIVE_BLOCKED
    consecutive 403/429 pages. Prints one status line per page.
    bim001: when `run` is given, each page's raw HTML is captured into the run folder
    and recorded in its manifest; without it, behavior is exactly bim000.
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
        html = page.pop("html")
        fetched = page.pop("fetched")
        saved = None

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

        if run is not None:
            record_capture(run, page, url, html, fetched, md_saved=saved is not None)
        pages.append(page)

        if consecutive_blocked >= MAX_CONSECUTIVE_BLOCKED:
            print(f"\n⛔ {MAX_CONSECUTIVE_BLOCKED} consecutive blocked pages (403/429) — stopping run. "
                  f"{total - i} URL(s) not attempted.")
            if run is not None:
                run.log(f"stop rule: {MAX_CONSECUTIVE_BLOCKED} consecutive blocked pages, {total - i} URL(s) not attempted")
            return pages, True

    return pages, False


async def run(urls: Sequence[str], run_folder: RunFolder | None = None) -> tuple[list[dict], bool]:
    browser_config = BrowserConfig(headless=True, user_agent=USER_AGENT)
    async with AsyncWebCrawler(config=browser_config) as crawler:
        return await crawl_all(urls, crawler, run_folder)


def main() -> None:
    """Main entry point."""
    args = parse_args()

    problem = validate_project(args.project)
    if problem:
        print_project_usage(problem, args.project)
        sys.exit(2)

    all_urls = read_urls(args.input)                       # input_total counts everything (AC-33)
    urls = all_urls[:args.limit] if args.limit is not None else all_urls
    command = "python -m smart_crawler.crawler " + " ".join(sys.argv[1:])   # canonical form (I-4)

    # bim001: the run folder exists on every path that gets past validation (AC-13, AC-37).
    run_folder = RunFolder(args.project, utc_now()).create()
    started_at = run_folder.started_at                     # create() may have moved to the next second (I-3)
    run_folder.log(f"run start project={args.project} run_id={run_folder.run_id} input_total={len(all_urls)} limit={args.limit}")

    def close_run(pages: list[dict], finished_at: str, stopped_early: bool) -> tuple[Path, Path]:
        summary_path = write_summary(pages, started_at, finished_at)
        manifest_path = run_folder.write_manifest(
            command=command, input_path=args.input.resolve(), input_total=len(all_urls),
            limit=args.limit, input_hosts=input_hosts(all_urls),
            finished_at=finished_at, stopped_early=stopped_early)
        absences = build_absences(run_folder.pages, urls, all_urls)
        run_folder.write_absences(absences)
        captured = sum(1 for p in run_folder.pages if p["outcome"] == "captured")
        run_folder.log(f"run end captured={captured} absent={len(absences)} stopped_early={stopped_early}")
        return summary_path, manifest_path

    if not urls:
        # Still a run: write a truthful summary (pages=[]) so no stale prior-run file survives.
        print("⚠️  No URLs found in file — nothing to crawl")
        summary_path, manifest_path = close_run([], utc_now(), False)
        print(f"🧾 Summary: {summary_path}")
        print(f"📁 Run folder: {run_folder.dir}")
        return

    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    version = importlib.metadata.version("crawl4ai")
    est_min = len(urls) * (7 + sum(PAUSE_RANGE_S) / 2) / 60  # ~7 s/page observed + mean pause

    print("\n" + "=" * 80)
    print(f"Batch crawler — crawl4ai {version}")
    print("=" * 80)
    print(f"\nProject: {args.project}   run_id: {run_folder.run_id}")
    print(f"Ready to crawl {len(urls)} of {len(all_urls)} URL(s)")
    print(f"From: {args.input}")
    print(f"To:   {PAGE_DIR}  (markdown)")
    print(f"      {run_folder.dir}  (html/, manifest.json, absences.json, stage_log.txt)")
    print(f"Pause between pages: {PAUSE_RANGE_S[0]}-{PAUSE_RANGE_S[1]} s (random)")
    print(f"Estimated time: ~{est_min:.1f} min")

    print("\nFirst 5 URLs:")
    for u in urls[:5]:
        print(f"  • {u}")
    if len(urls) > 5:
        print(f"  ... and {len(urls) - 5} more")
    print()

    pages, stopped_early = asyncio.run(run(urls, run_folder))
    summary_path, manifest_path = close_run(pages, utc_now(), stopped_early)

    successful = sum(1 for p in pages if p["ok"])
    failed = len(pages) - successful
    blocked = sum(1 for p in pages if p["error"] == "blocked")
    captured = sum(1 for p in run_folder.pages if p["outcome"] == "captured")

    print("\n" + "="*80)
    print("✅ CRAWL COMPLETE" if not stopped_early else "⛔ CRAWL STOPPED EARLY")
    print("="*80)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}  (blocked: {blocked})")
    print(f"🧾 HTML captured: {captured} of {len(pages)} attempted; {len(all_urls) - len(pages)} not attempted")
    print(f"📁 Markdown: {PAGE_DIR}")
    print(f"📁 Run folder: {run_folder.dir}")
    print(f"🧾 Summary: {summary_path}")
    print(f"🧾 Manifest: {manifest_path}")

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
