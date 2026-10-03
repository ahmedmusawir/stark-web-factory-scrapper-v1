#!/usr/bin/env python3
"""Serial Crawl4AI capture into an immutable Raw Recon Package v2.

Legacy shared Markdown and run_summary outputs are retired (R8/E-01).
A browser session supplies controlled access when used by the pipeline.
"""

from pathlib import Path
import argparse
import asyncio
import importlib.metadata
import json
import platform
import random  # retained compatibility for existing test harness; not used for pacing
import hashlib
import subprocess
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
MAX_CONSECUTIVE_BLOCKED = 1
PAUSE_RANGE_S = (5, 5)  # E-05: minimum gap AFTER completion, never random

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

async def crawl_page(crawler: "AsyncWebCrawler", url: str, *, session_id: str | None = None) -> dict:
    """Crawl one URL. Returns a page record for run_summary plus the markdown (if ok).

    Failure rules: status_code >= 400, or result.success False, is a failed page.
    403/429 are recorded as error "blocked". Failed pages carry no markdown.
    """
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        page_timeout=90000,              # 90 seconds
        delay_before_return_html=3.0,    # Wait 3s after page load
        wait_for_images=True,            # Wait for all images
        session_id=session_id,
        max_retries=0,
        fallback_fetch_function=None,
    )

    fetched_at = utc_now()
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

    status = getattr(result, "redirected_status_code", None) or getattr(result, "status_code", None)
    success = bool(getattr(result, "success", False))
    record["status"] = status

    if status in BLOCKED_STATUSES:
        record["error"] = "blocked"
        return {**record, **not_fetched}

    if (status is not None and not 200 <= status < 300) or not success:
        # crawl4ai 0.9.x sets error_message (e.g. "Blocked by anti-bot protection: ...")
        record["error"] = getattr(result, "error_message", None) or f"HTTP {status}"
        return {**record, **not_fetched}

    html = getattr(result, "html", None)
    record["final_url"] = getattr(result, "redirected_url", None) or url
    record["redirect_chain"] = []
    record["fetched_at"] = fetched_at
    record["ok"] = bool(html)
    record["error"] = None if html else "no_html_attr" if html is None else "empty_body"
    # Preserve the diagnostic return API; product output never writes this Markdown.
    md = getattr(result, "markdown", None)
    markdown = (getattr(md, "fit_markdown", "") or getattr(md, "raw_markdown", "") or "").strip()
    return {**record, "markdown": markdown, "html": html, "fetched": True}


def save_markdown(*args, **kwargs):
    """Retired product surface (R8/E-01); historical outputs are never overwritten."""
    raise RuntimeError("shared Markdown output retired; use raw run HTML")


def write_summary(*args, **kwargs):
    """Retired product surface (R8/E-01)."""
    raise RuntimeError("shared run_summary output retired; use manifest.json")


MANIFEST_SCHEMA = "abm-raw-v2"
ACCESS_RUNG = "a"          # plain headless fetch, no stealth (Stealth ruling)
OUTCOMES = ("captured", "blocked", "failed", "unsupported", "skipped")


class RunFolder:
    """One crawl run's evidence folder. Nothing touches the filesystem until create()."""

    def __init__(self, project: str, started_at: str, root: Path | None = None):
        self.project = project
        self.root = root if root is not None else RUN_ROOT
        self.max_bytes = 100_000_000
        self.metadata_reserve = 5_000_000
        self.limit_hit = False
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
        for folder in ("discovery", "rest/responses", "rest/objects", "media", "screenshots"):
            (self.dir / folder).mkdir(parents=True, exist_ok=True)
        self.absences = []
        self.routes = None
        self.rest_index = {"schema": "abm-rest-index-v1", "transport": None,
            "collections": [{"type": x, "status": "skipped", "response_refs": [],
                             "per_page": 100, "total": None, "total_pages": None,
                             "fetched_objects": 0} for x in ("pages", "posts", "media", "categories", "tags", "users")],
            "responses": [], "objects": [], "fields_requested": "all; no _fields filter",
            "absences_file": "../absences.json"}
        self.rest_map = None
        self.media = {"schema": "abm-media-v1", "items": [],
                      "counts": {"items": 0, "internal": 0, "external": 0, "staging_domain": 0}}
        self.streams = {"discovery": "partial", "html": "partial", "rest": "skipped",
                        "media": "skipped", "screenshots": "empty"}
        return self

    def log(self, line: str, *, finalization=False) -> None:
        data = f"{utc_now()} {line}\n"
        if self.persisted_bytes() + len(data.encode()) > self.max_bytes - (0 if finalization else self.metadata_reserve):
            self.limit_hit = True
            raise BufferError("persisted_log_limit")
        with (self.dir / "stage_log.txt").open("a", encoding="utf-8") as fh:
            fh.write(data)

    def allocate_slug(self, base: str) -> str:
        """First use -> base; later uses in the same run -> base-2, base-3, ... (R4)."""
        n = self._slug_counts.get(base, 0) + 1
        self._slug_counts[base] = n
        return base if n == 1 else f"{base}-{n}"

    def persisted_bytes(self):
        return sum(p.stat().st_size for p in self.dir.rglob("*") if p.is_file())

    def save_bytes(self, rel, data, *, finalization=False):
        """Exclusive bounded write; reserve metadata capacity before collection writes."""
        path = self.dir / rel
        if not path.resolve().is_relative_to(self.dir.resolve()):
            raise ValueError("write escapes run")
        ceiling = self.max_bytes if finalization else self.max_bytes - self.metadata_reserve
        if self.persisted_bytes() + len(data) > ceiling:
            self.limit_hit = True
            raise BufferError("persisted_byte_limit")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as fh:
            fh.write(data)
        return path

    def save_html(self, slug: str, html: str) -> tuple[str, int]:
        """Write html byte-for-byte (utf-8) to html/<slug>.html. Returns (relative file, byte count)."""
        data = html.encode("utf-8")
        target = self.html_dir / f"{slug}.html"
        if target.exists():
            raise FileExistsError(f"refusing to overwrite {target.name}")
        self.save_bytes(f"html/{slug}.html", data)
        return f"html/{slug}.html", len(data)

    def record_page(self, record: dict, *, slug: str, outcome: str, reason: str | None = None,
                    html_file: str | None = None, html_bytes: int | None = None,
                    md_file: str | None = None) -> dict:
        """Manifest entry: the run_summary record's five values verbatim + six bim001 fields."""
        assert outcome in OUTCOMES, outcome
        entry = {
            "url": record["url"], "input_url": record.get("input_url", record["url"]),
            "final_url": record.get("final_url", record["url"] if record.get("status") else None),
            "redirect_chain": record.get("redirect_chain", []), "slug": slug,
            "status": record["status"], "outcome": outcome, "reason": reason,
            "fetched_at": record.get("fetched_at", self.started_at if record.get("status") else None),
            "elapsed_s": record["elapsed_s"], "retries": 0,
            "html_file": html_file, "block_file": record.get("block_file"),
            "html_bytes": html_bytes,
            "sha256": hashlib.sha256((self.dir / html_file).read_bytes()).hexdigest()
                      if html_file and (self.dir / html_file).is_file() else None,
            "rest_ref": None, "rest_outcome": "rest_unavailable",
        }
        self.pages.append(entry)
        return entry

    def write_json(self, rel, value):
        data = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        return self.save_bytes(rel, data, finalization=True)

    def write_manifest(self, *, command: str, input_path: Path, input_total: int, limit: int | None,
                       input_hosts: list[str], finished_at: str, stopped_early: bool) -> Path:
        # Local input path is an invocation detail, never an absolute authored reference.
        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
                                             text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            commit = "unknown"
        counts = {"routes": len(self.pages), **{o: sum(p["outcome"] == o for p in self.pages) for o in OUTCOMES},
                  "rest_objects": len(self.rest_index["objects"]),
                  "rest_mapped_routes": sum(p["rest_outcome"] == "mapped" for p in self.pages),
                  "media_items": len(self.media["items"])}
        self.streams["html"] = "complete" if counts["captured"] == counts["routes"] and not stopped_early else "partial"
        manifest = {
            "schema": MANIFEST_SCHEMA, "project_name": self.project, "run_id": self.run_id,
            "started_at": self.started_at, "finished_at": finished_at,
            "command": f"python -m smart_crawler.crawler --project {self.project}" + (f" --limit {limit}" if limit else ""),
            "input": {"url": self.pages[0]["input_url"] if self.pages else None, "mode": "routes", "limit": limit},
            "scope": {"hosts_allowed": input_hosts, "redirect_max_hops": 5, "robots_policy": "recorded_not_enforced"},
            "access": {"rung": ACCESS_RUNG, "user_agent": USER_AGENT,
                       "operation_gap_after_completion_s": 5.0, "retry_max": 0,
                       "stop_on_first_intentional_refusal": True, "automatic_restart": False,
                       "background_resources_paced": False, "page_timeout_ms": 90000,
                       "delay_before_return_html_s": 3.0, "wait_for_images": True,
                       "cache_mode": "BYPASS", "headless": True,
                       "discovery_rest_transport": "chromium_page_window_fetch"},
            "versions": {"python": platform.python_version(),
                         **{n: importlib.metadata.version(n) for n in ("crawl4ai", "playwright", "requests")},
                         "tool_commit": commit},
            "streams": self.streams, "counts": counts, "stopped_early": stopped_early,
            "fallbacks_fired": [], "pages": self.pages,
        }
        for key, value in getattr(self, "manifest_extra", {}).items():
            if isinstance(value, dict) and isinstance(manifest.get(key), dict):
                manifest[key].update(value)
            else:
                manifest[key] = value
        authored = []
        for path in sorted((self.dir / 'screenshots').rglob('*')):
            if path.is_file() and path.name != 'README.md':
                if path.is_symlink() or not path.resolve().is_relative_to(self.dir.resolve()):
                    raise ValueError('authored screenshot escapes run')
                authored.append({'file':path.relative_to(self.dir).as_posix(),
                                 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                                 'bytes':path.stat().st_size, 'authored_by':'Director'})
        if authored:
            self.streams['screenshots'] = 'authored'
            manifest['screenshots'] = authored
        routes = self.routes or {"schema": "abm-routes-v1", "mode": "routes", "sitemap_url_used": None,
            "sources": [], "routes": [{"url": p["url"], "input_urls": [p["input_url"]], "aliases": [],
                                       "source_file": None, "lastmod": None} for p in self.pages],
            "dropped": [], "counts": {"loc_total": input_total, "routes": len(self.pages), "dropped": 0}}
        rest_map = self.rest_map or {"schema": "abm-rest-map-v1",
            "by_route": {p["url"]: {"outcome": "rest_unavailable", "reason": "not_collected"} for p in self.pages},
            "unrouted_objects": [], "content_rendered_empty": []}
        for rel, obj in (("discovery/routes.json", routes), ("rest/index.json", self.rest_index),
                         ("rest/map.json", rest_map), ("media/inventory.json", self.media)):
            self.write_json(rel, obj)
        self.save_bytes("screenshots/README.md", b'Director-authored evidence slot. Drop screenshots here. The tool writes only this README into this folder; screenshot bytes are Director-authored. Files here are listed in `manifest.streams.screenshots` as `authored` with their sha256; if empty, `absences.json` carries `stream: screenshots, outcome: skipped, reason: none_supplied`.\n', finalization=True)
        return self.write_json("manifest.json", manifest)

    def write_absences(self, absences: list[dict]) -> Path:
        return self.write_json("absences.json", absences)


def build_absences(pages: list[dict], attempted: Sequence[str], all_urls: Sequence[str]) -> list[dict]:
    absences = [{"stream": "html", "ref": p["url"], "outcome": p["outcome"],
                 "reason": p["reason"], "at": utc_now()} for p in pages if p["outcome"] != "captured"]
    known = {p["url"] for p in pages}
    absences += [{"stream": "html", "ref": u, "outcome": "skipped",
                  "reason": "stop_rule" if u in attempted else "limit", "at": utc_now()}
                 for u in all_urls if u not in known]
    return absences


def input_hosts(urls: Sequence[str]) -> list[str]:
    """Sorted unique hostnames of the input URLs (hostname, not netloc: no ports; None skipped)."""
    return sorted({h for h in (urlparse(u).hostname for u in urls) if h})

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
        if isinstance(data, dict) and data.get("schema") == "abm-routes-v1":
            data = data["routes"]
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
                        help="explicit legacy URL JSON; otherwise use latest project discovery/routes.json")
    parser.add_argument("--limit", type=int, default=None,
                        help="crawl only the first N URLs (default: all)")
    parser.add_argument("--max-bytes", type=int, default=100_000_000,
                        help="persisted raw ceiling; includes reserved final metadata")
    parser.add_argument("--routes", type=Path, help="explicit discovery/routes.json")
    supplied=list(argv) if argv is not None else sys.argv[1:]
    args = parser.parse_args(supplied)
    args.input_explicit=any(x=='--input' or x.startswith('--input=') for x in supplied)
    if args.max_bytes < 6_000_000:
        parser.error("--max-bytes must be >= 6000000 to reserve final metadata")
    if args.routes:
        args.input = args.routes
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be >= 1")
    return args


def resolve_routes_input(args):
    """Preserve explicit legacy --input while defaulting the entry point to v2."""
    if args.routes or args.input_explicit:
        return args.input
    available=sorted((RUN_ROOT/args.project/'runs').glob('*/discovery/routes.json'))
    if not available:
        print('No discovery/routes.json for --project '+args.project+'. Run the Capture pipeline first or supply --routes.',file=sys.stderr)
        raise SystemExit(1)
    return available[-1]


def record_capture(run: RunFolder, page: dict, url: str, html: str | None, fetched: bool,
                   md_saved: bool = False) -> dict:
    """HTML capture is independent of Markdown. E-01/R8, E-09 route accounting."""
    base = slugify(url.replace("https://", "").replace("http://", ""))
    html_file = html_bytes = None
    slug = run.allocate_slug(base)
    if page["error"] == "blocked":
        outcome, reason = "blocked", "blocked"
    elif page["error"] == "redirect_out_of_scope":
        outcome, reason = "unsupported", "redirect_out_of_scope"
    elif not fetched:
        outcome, reason = "failed", page["error"] or "fetch failed"
    elif not html:
        outcome, reason = "unsupported", "no_html_attr" if html is None else "empty_body"
    else:
        try:
            html_file, html_bytes = run.save_html(slug, html)
            outcome, reason = "captured", None
        except Exception as exc:
            outcome, reason = "failed", f"write failed: {exc}"
    if outcome == "blocked":
        body = page.pop("block_html", None)
        if body:
            folder = run.html_dir / "_blocked"
            folder.mkdir(exist_ok=True)
            path = folder / (slug + ".html")
            run.save_bytes(path.relative_to(run.dir), body.encode("utf-8"))
            page["block_file"] = path.relative_to(run.dir).as_posix()
            run.log(f"html block_evidence {page['block_file']} sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
        else:
            run.log(f"html block_evidence_unavailable {url} browser interrupted before body retention")
    entry = run.record_page(page, slug=slug, outcome=outcome, reason=reason,
                            html_file=html_file, html_bytes=html_bytes)
    run.log(f"html intentional {outcome} {url}" + (f" ({reason})" if reason else ""))
    return entry


async def crawl_all(urls: Sequence[str], crawler: "AsyncWebCrawler",
                    run: RunFolder | None = None, *, session=None) -> tuple[list[dict], bool]:
    """One attempt per document. First refusal stops; later outcomes are skipped."""
    pages = []
    stopped = False
    for i, url in enumerate(urls):
        if stopped:
            if run:
                run.record_page({"url": url, "status": None, "elapsed_s": 0},
                                slug=run.allocate_slug(slugify(url.replace("https://", "").replace("http://", ""))),
                                outcome="skipped", reason="stop_rule")
            continue
        if i and session is None:
            if run:
                run.log("access pause 5.0s after operation completion")
            await asyncio.sleep(5.0)
        if session is not None:
            from smart_crawler.browser_session import CollectionStopped
            try:
                page = await session.capture(url)
            except CollectionStopped as exc:
                stopped = True
                if run:
                    run.record_page({"url":url,"status":None,"elapsed_s":0},
                                    slug=run.allocate_slug(slugify(url.replace("https://", "").replace("http://", ""))),
                                    outcome="skipped",reason="stop_rule")
                    run.log(f"access stop {exc}")
                continue
        else:
            page = await crawl_page(crawler, url)
        html, fetched = page.pop("html"), page.pop("fetched")
        page.pop("markdown")
        if run:
            record_capture(run, page, url, html, fetched)
        pages.append(page)
        if session is not None:
            session.last_completion = time.monotonic()
        if page["error"] == "blocked" or (session is not None and session.stop_reason) or (run is not None and run.limit_hit):
            stopped = True
            print("First intentional refusal — stopping run")
            if run:
                run.log("access stop rule: first intentional refusal")
    return pages, stopped


async def run(urls: Sequence[str], run_folder: RunFolder | None = None) -> tuple[list[dict], bool]:
    from smart_crawler.browser_session import BrowserSession
    # Stage C3: explicit routes run through the same controlled session as discovery.
    async with BrowserSession(urls[0], log=lambda row: run_folder.log("browser " + json.dumps(row)) if run_folder else None) as session:
        return await crawl_all(urls, session.crawler, run_folder, session=session)


def main() -> None:
    """Main entry point."""
    args = parse_args()

    problem = validate_project(args.project)
    if problem:
        print_project_usage(problem, args.project)
        sys.exit(2)

    args.input=resolve_routes_input(args)
    all_urls = read_urls(args.input)                       # input_total counts everything (AC-33)
    urls = all_urls[:args.limit] if args.limit is not None else all_urls
    run_folder = RunFolder(args.project, utc_now()).create()
    run_folder.max_bytes = args.max_bytes
    run_folder.log(f"run start project={args.project} run_id={run_folder.run_id} input_total={len(all_urls)} limit={args.limit}")
    stopped_early = False
    interrupted = False
    if urls:
        try:
            _, stopped_early = asyncio.run(run(urls, run_folder))
        except KeyboardInterrupt:
            interrupted = stopped_early = True
            run_folder.log("access SIGINT: finalizing preserved partial evidence")
            completed = {p["url"] for p in run_folder.pages}
            for url in urls:
                if url not in completed:
                    run_folder.record_page({"url":url,"status":None,"elapsed_s":0},
                        slug=run_folder.allocate_slug(slugify(url.replace("https://", "").replace("http://", ""))),
                        outcome="skipped",reason="stop_rule")
    else:
        print("No URLs found — empty raw run")
    for url in all_urls[len(urls):]:
        run_folder.record_page({"url": url, "status": None, "elapsed_s": 0},
            slug=run_folder.allocate_slug(slugify(url.replace("https://", "").replace("http://", ""))),
            outcome="skipped", reason="limit")
    absent = build_absences(run_folder.pages, urls, all_urls)
    absent += [{"stream": stream, "ref": ref, "outcome": "skipped", "reason": reason, "at": utc_now()}
               for stream, ref, reason in [("discovery", "robots.txt", "not_collected"),
                  *[("rest", x, "not_collected") for x in ("pages", "posts", "media", "categories", "tags", "users")],
                  ("media", "inventory", "not_collected"), ("screenshots", "screenshots", "none_supplied")]]
    run_folder.write_absences(absent)
    from smart_crawler.browser_session import BrowserSession
    allowed=sorted(BrowserSession(all_urls[0]).hosts) if all_urls else []
    run_folder.write_manifest(command="", input_path=args.input, input_total=len(all_urls), limit=args.limit,
                              input_hosts=allowed, finished_at=utc_now(), stopped_early=stopped_early)
    run_folder.log(f"run end captured={sum(p['outcome'] == 'captured' for p in run_folder.pages)} stopped_early={stopped_early}")
    print(f"Raw run: {run_folder.dir}")
    if interrupted:
        sys.exit(130)
    if stopped_early:
        sys.exit(2)


if __name__ == "__main__":
    main()
