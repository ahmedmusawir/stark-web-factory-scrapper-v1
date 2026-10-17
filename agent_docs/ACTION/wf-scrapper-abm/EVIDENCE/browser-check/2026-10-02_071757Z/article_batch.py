"""Three one-attempt article captures using the corrected successful wrapper.

No discovery, batch writer, direct Playwright import, retry, or alternate URL.
Invoke once with the existing venv. Each browser child has a 180s ceiling; wait 5s after cleanup between URLs.
"""
import asyncio
import collections
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from urllib.parse import urlsplit, urlunsplit

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[5]
URLS = [
    "https://cyberizegroup.com/facebook-ads-andromeda-update/",
    "https://cyberizegroup.com/garage-door-repair-ppc-agency-get-more-leads-sales-now/",
    "https://cyberizegroup.com/boost-your-dental-practice-with-a-professional-seo-company/",
]
ARTICLE_INDEX = int(sys.argv[sys.argv.index("--article") + 1]) if "--article" in sys.argv else 0
E = BASE / f"article-{ARTICLE_INDEX + 1:02d}" if "--child" in sys.argv else BASE
TARGET = URLS[ARTICLE_INDEX]
HOSTS = {"cyberizegroup.com", "www.cyberizegroup.com"}


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write(name, obj):
    with (E / name).open("x") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def safe_url(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.hostname or "", p.path,
                       "[query-redacted]" if p.query else "", ""))


def event(kind, **data):
    with (E / "browser-events.jsonl").open("a") as f:
        f.write(json.dumps({"utc": utc(), "event": kind, **data}) + "\n")



def verify_body(html, markdown):
    from bs4 import BeautifulSoup
    import html as html_module
    norm = lambda text: re.sub(r"[^\w]+", " ", html_module.unescape(text).lower()).strip()
    md_plain = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", markdown)
    md_normalized = norm(md_plain)
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.select("nav, header, footer, aside, form, script, style, noscript, [class*='related-post'], [id*='related-post']"):
        node.decompose()

    def paragraphs(node):
        found, seen = [], set()
        for p in node.find_all("p"):
            text = p.get_text(" ", strip=True)
            words = len(text.split())
            linked = sum(len(a.get_text(" ", strip=True)) for a in p.find_all("a"))
            if words >= 18 and len(text) >= 100 and linked / max(1, len(text)) < 0.4 and norm(text) not in seen:
                seen.add(norm(text))
                found.append(text)
        return found

    selected, texts = "body_fallback", []
    for selector in (".entry-content", ".post-content", ".tcb-post-content", ".thrv-post-content", "article", "main", "#content", "body"):
        candidates = [(node, paragraphs(node)) for node in soup.select(selector)]
        if candidates:
            node, rows = max(candidates, key=lambda pair: sum(len(t) for t in pair[1]))
            if len(rows) >= 3 and sum(len(t.split()) for t in rows) >= 180:
                selected, texts = selector, rows
                break
    if not texts:
        texts = paragraphs(soup)
    rows = [{"paragraph": i + 1, "words": len(text.split()), "characters": len(text),
             "present_in_markdown": norm(text) in md_normalized,
             "start_excerpt": text[:160], "end_excerpt": text[-100:]} for i, text in enumerate(texts)]
    matched = sum(p["present_in_markdown"] for p in rows)
    words = sum(p["words"] for p in rows)
    matched_words = sum(p["words"] for p in rows if p["present_in_markdown"])
    return {"outcome": "substantive_body_verified" if matched >= 3 and matched_words >= 180 else "insufficient_substantive_body",
            "selected_content_region": selected, "substantive_HTML_paragraphs": len(rows),
            "substantive_paragraph_words": words, "matched_paragraph_words": matched_words, "paragraphs_matched_in_markdown": matched,
            "unmatched_paragraph_numbers": [p["paragraph"] for p in rows if not p["present_in_markdown"]],
            "last_selected_paragraph_present_in_markdown": rows[-1]["present_in_markdown"] if rows else False,
            "paragraphs": rows, "rule": "At least 3 non-navigation, mostly non-link paragraphs of >=18 words each; >=180 words total. Match normalized paragraph text against Markdown with link destinations removed.",
            "completeness_limit": "Checks the returned rendered DOM against returned Markdown, not hidden/unloaded content or a canonical source copy."}


async def capture():
    # Isolate library database/log/temp writes; preserve HOME and browser lookup.
    os.environ["CRAWL4_AI_BASE_DIRECTORY"] = str(E / "runtime")
    os.environ["TMPDIR"] = str(E / "tmp")
    (E / "tmp").mkdir(exist_ok=False)
    sys.path.insert(0, str(ROOT))
    from smart_crawler.crawler import crawl_page, USER_AGENT
    from crawl4ai import AsyncWebCrawler, BrowserConfig

    config = BrowserConfig(headless=True, user_agent=USER_AGENT)
    assert not config.enable_stealth and not config.proxy and not config.proxy_config
    state = {"target": TARGET, "started_utc": utc(), "stop": None,
             "main_responses": [], "final_url": None, "title": None,
             "refusals": [], "request_events": [], "responses": [],
             "pre_dispatch_aborts": [], "observed_redirect_chain": [],
             "html_bytes": 0, "markdown_characters": 0, "substantive_article": False,
             "article_validation": {"outcome": "not_completed"},
             "article_number": ARTICLE_INDEX + 1}
    browser = None
    primary_page = None
    stopped = asyncio.Event()
    monitors = []
    tasks = set()

    def spawn(coro):
        task = asyncio.create_task(coro)
        tasks.add(task)
        task.add_done_callback(tasks.discard)
        return task

    async def close_browser():
        try:
            if browser:
                await browser.close()
        except Exception as exc:
            event("close_error", exception=type(exc).__name__)

    def stop(reason, **detail):
        if not state["stop"]:
            state["stop"] = {"utc": utc(), "reason": reason, **detail}
            event("stop", **state["stop"])
            stopped.set()
            spawn(close_browser())

    def describe(request):
        try:
            main = request.is_navigation_request() and request.frame == primary_page.main_frame
        except Exception:
            main = False
        return {"url": safe_url(request.url), "method": request.method,
                "resource_type": request.resource_type, "main_document": main}

    def request_seen(request):
        row = {**describe(request), "after_stop": stopped.is_set()}
        state["request_events"].append(row)
        event("request_observed", **row)

    def response_seen(response):
        row = {**describe(response.request), "status": response.status,
               "after_stop": stopped.is_set()}
        # Explicit allowlist: never retain cookie/auth or arbitrary headers.
        headers = response.headers
        row["headers"] = {k: safe_url(v) if k == "location" else v
                          for k, v in headers.items()
                          if k in {"content-type", "location", "retry-after", "x-ac", "cf-mitigated"}}
        state["responses"].append(row)
        event("response_observed", **row)
        if row["main_document"]:
            state["main_responses"].append(row)
        if response.status in (403, 429):
            state["refusals"].append(row)
            stop("HTTP_refusal", resource=row)
        elif headers.get("cf-mitigated", "").lower() == "challenge":
            stop("explicit_challenge_header", resource=row)

    async def inspect_dom(page):
        try:
            title = await page.title()
            state["title"] = title
            state["final_url"] = safe_url(page.url)
            text = (await page.locator("body").inner_text(timeout=500)).lower()
            if (re.search(r"^(just a moment|attention required|access denied|verify you are human)", title, re.I)
                or any(s in text[:12000] for s in ("verify you are human", "checking your browser before accessing",
                       "performing security verification", "enable javascript and cookies to continue"))):
                stop("explicit_challenge_DOM", resource={"url": safe_url(page.url), "main_document": True})
        except Exception:
            pass  # DOM may not exist yet, or the refusal stop already closed it.

    async def monitor(page):
        while not stopped.is_set():
            await inspect_dom(page)
            await asyncio.sleep(0.25)

    async def created(page, context, config, **kwargs):
        nonlocal browser, primary_page
        primary_page = page
        browser = context.browser
        assert config.max_retries == 0 and config.fallback_fetch_function is None
        assert not any((config.magic, config.simulate_user, config.override_navigator,
                        config.check_robots_txt, config.scan_full_page, config.js_code))
        actual = {k: getattr(config, k) for k in
                  ("page_timeout", "delay_before_return_html", "wait_for_images", "wait_until",
                   "max_retries", "magic", "simulate_user", "override_navigator", "check_robots_txt")}
        actual["cache_mode"] = config.cache_mode.name
        assert actual["cache_mode"] == "BYPASS"
        assert (config.page_timeout, config.delay_before_return_html, config.wait_for_images) == (90000, 3.0, True)
        write("actual-configuration.json", {"run": actual,
              "browser": {"headless": True, "user_agent": USER_AGENT,
                          "browser_type": "chromium", "actual_browser_version": browser.version,
                          "ignore_https_errors": browser_config.ignore_https_errors,
                          "enable_stealth": browser_config.enable_stealth, "proxy_configured": False},
              "python": sys.version, "versions": {p: importlib.metadata.version(p)
                 for p in ("crawl4ai", "playwright", "requests")}})
        context.on("request", request_seen)
        context.on("response", response_seen)
        context.on("requestfailed", lambda r: event("request_failed", **describe(r), after_stop=stopped.is_set()))
        context.on("serviceworker", lambda w: stop("unexpected_service_worker", resource={"url": safe_url(w.url)}))

        # Context routing covers first popup navigations; CDP below covers every
        # main-page redirect hop (ordinary Playwright routing does not).
        async def route_guard(route):
            request = route.request
            reason = None
            if stopped.is_set():
                reason = "sticky_stop"
            elif request.is_navigation_request() and request.frame.parent_frame is None:
                if request.frame != page.main_frame:
                    reason = "extra_top_level_page"
                elif urlsplit(request.url).hostname not in HOSTS or urlsplit(request.url).scheme != "https":
                    reason = "unexpected_top_level_destination"
            if reason:
                row = {**describe(request), "reason": reason}
                state["pre_dispatch_aborts"].append(row)
                event("route_aborted", **row)
                await route.abort()
                if reason != "sticky_stop":
                    stop(reason, resource=row)
            else:
                await route.continue_()
        await context.route("**/*", route_guard)

        cdp = await context.new_cdp_session(page)
        main_frame_id = (await cdp.send("Page.getFrameTree"))["frameTree"]["frame"]["id"]
        authorized_document_ids = set()

        async def paused(params):
            try:
                request = params["request"]
                url = request["url"]
                is_main = params["frameId"] == main_frame_id and params["resourceType"] == "Document"
                reason = "sticky_stop" if stopped.is_set() else None
                if is_main and not reason:
                    p = urlsplit(url)
                    parent = params.get("redirectedRequestId")
                    if p.hostname not in HOSTS or p.scheme != "https" or p.username or p.password:
                        reason = "unexpected_top_level_destination"
                    elif authorized_document_ids and parent not in authorized_document_ids:
                        reason = "second_top_level_navigation"
                    elif not authorized_document_ids and url != TARGET:
                        reason = "unexpected_initial_target"
                    if not reason:
                        authorized_document_ids.add(params["requestId"])
                        state["observed_redirect_chain"].append({"url": safe_url(url), "redirected": bool(parent)})
                if "/cdn-cgi/challenge-platform/" in url or "challenges.cloudflare.com" == urlsplit(url).hostname:
                    reason = "explicit_challenge_request"
                if reason:
                    row = {"url": safe_url(url), "main_document": is_main, "reason": reason}
                    state["pre_dispatch_aborts"].append(row)
                    event("cdp_aborted", **row)
                    await cdp.send("Fetch.failRequest", {"requestId": params["requestId"], "errorReason": "Aborted"})
                    if reason != "sticky_stop":
                        stop(reason, resource=row)
                else:
                    await cdp.send("Fetch.continueRequest", {"requestId": params["requestId"]})
            except Exception as exc:
                if not stopped.is_set():
                    stop("interception_error", exception=type(exc).__name__)
        cdp.on("Fetch.requestPaused", lambda p: spawn(paused(p)))
        await cdp.send("Fetch.enable", {"patterns": [{"urlPattern": "*", "requestStage": "Request"}]})
        event("controls_installed", redirect_interception="Chromium Fetch", initial_navigation_budget=1)
        monitors.append(asyncio.create_task(monitor(page)))
        return page

    async def before_goto(page, context, url, config, **kwargs):
        if stopped.is_set() or url != TARGET:
            raise RuntimeError("Diagnostic navigation guard")
        event("top_level_navigation_start", url=TARGET)
        return page

    browser_config = config
    result = None
    asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, lambda: stop("watchdog_175s"))
    try:
        async with AsyncWebCrawler(config=browser_config, base_directory=str(E / "runtime")) as crawler:
            crawler.crawler_strategy.set_hook("on_page_context_created", created)
            crawler.crawler_strategy.set_hook("before_goto", before_goto)
            result = await crawl_page(crawler, TARGET)  # Exactly one existing product call.
            if primary_page and not primary_page.is_closed():
                await inspect_dom(primary_page)
            if result:
                for key, name in (("html", "returned.html"), ("markdown", "returned.md")):
                    content = result.pop(key, None)
                    if content:
                        data = content.encode("utf-8")
                        with (E / name).open("xb") as f:
                            f.write(data)
                        state[key + "_sha256"] = hashlib.sha256(data).hexdigest()
                        state[key + "_bytes"] = len(data)
                        state["html_bytes" if key == "html" else "markdown_characters"] = len(data) if key == "html" else len(content)
                # Exception messages can contain page data: retain only local log.
                state["product_result"] = {k: v for k, v in result.items() if k != "error"}
                state["product_error_present"] = bool(result.get("error"))
                page_ok = bool(not stopped.is_set() and result.get("ok") and
                               state["main_responses"] and state["main_responses"][-1]["status"] == 200)
                if page_ok and (E / "returned.html").exists() and (E / "returned.md").exists():
                    verification = verify_body((E / "returned.html").read_text(), (E / "returned.md").read_text())
                    state["article_validation"] = verification
                    write("content-validation.json", verification)
                    event("article_validated", outcome=verification["outcome"], paragraphs=verification["substantive_HTML_paragraphs"])
                    state["substantive_article"] = verification["outcome"] == "substantive_body_verified"
                else:
                    state["article_validation"] = {"outcome": "failed_or_interrupted", "stop": state["stop"]}
                state["capture_finished_utc"] = utc()

    except Exception as exc:
        state["exception_type"] = type(exc).__name__
        event("capture_exception", exception=type(exc).__name__)
    finally:
        for task in monitors:
            task.cancel()
        if tasks:
            await asyncio.wait(list(tasks), timeout=2)
        state["ended_utc"] = utc()
        state["request_counts_by_host"] = dict(collections.Counter(urlsplit(r["url"]).hostname for r in state["request_events"]))
        state["request_counts_by_resource_type"] = dict(collections.Counter(r["resource_type"] for r in state["request_events"]))
        state["response_status_counts"] = dict(collections.Counter(str(r["status"]) for r in state["responses"]))
        state["responses_after_stop"] = sum(r["after_stop"] for r in state["responses"])
        write("result.json", state)
        event("capture_finished", substantive_article=state["substantive_article"], stop=state["stop"])


def supervise():
    assert subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() == "wf-scrapper-abm"
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == "3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f"
    write("RUN_ONCE.json", {"utc": utc(), "target": TARGET, "ceiling_seconds": 180})
    started = time.monotonic()
    owned = {}
    with (E / "browser-output.local.log").open("xb") as log:
        child = subprocess.Popen([sys.executable, "-B", __file__, "--child", "--article", str(ARTICLE_INDEX)], cwd=ROOT,
                                 stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        sent_term = False
        while child.poll() is None:
            # Track only this child's descendants, including detached Chromium.
            procs = {}
            for p in Path('/proc').glob('[0-9]*/stat'):
                try:
                    fields = p.read_text().rsplit(')', 1)[1].split()
                    procs[int(p.parent.name)] = (int(fields[1]), fields[19])
                except (OSError, ValueError, IndexError):
                    pass
            roots = {child.pid} | set(owned)
            while True:
                found = {pid for pid, (parent, stamp) in procs.items() if parent in roots}
                if found <= roots:
                    break
                roots |= found
            owned.update({pid: procs[pid][1] for pid in roots if pid in procs})
            elapsed = time.monotonic() - started
            if elapsed >= 175 and not sent_term:
                child.send_signal(signal.SIGTERM)
                sent_term = True
            if elapsed >= 179.5:
                break
            time.sleep(0.1)
        killed = []
        for pid, stamp in owned.items():
            try:
                fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
                if fields[19] == stamp:
                    os.kill(pid, signal.SIGKILL)
                    killed.append(pid)
            except (OSError, ValueError, IndexError):
                pass
        child.wait(timeout=1)
    write("supervisor.json", {"ended_utc": utc(), "elapsed_seconds": time.monotonic()-started,
                              "child_exit": child.returncode, "term_at_175s": sent_term,
                              "remaining_owned_processes_killed": killed, "ceiling_seconds": 180})


def batch():
    global E, TARGET, ARTICLE_INDEX
    E = BASE
    write("BATCH_ONCE.json", {"started_utc": utc(), "urls": URLS, "attempts_per_url": 1, "gap_seconds": 5})
    entries = []
    previous_finished = None
    for ARTICLE_INDEX, TARGET in enumerate(URLS):
        preceding_gap = None
        if previous_finished is not None:
            time.sleep(5)
            preceding_gap = time.monotonic() - previous_finished
        E = BASE / f"article-{ARTICLE_INDEX + 1:02d}"
        E.mkdir(exist_ok=False)
        supervise()
        previous_finished = time.monotonic()
        result_file = E / "result.json"
        result = json.loads(result_file.read_text()) if result_file.exists() else None
        entries.append({"article": ARTICLE_INDEX + 1, "url": TARGET,
                        "preceding_gap_after_previous_process_seconds": preceding_gap,
                        "result_file": str(result_file.relative_to(BASE)),
                        "stop": result.get("stop") if result else {"reason": "missing_child_result"},
                        "validation": result.get("article_validation", {}).get("outcome") if result else None})
        if not result or result.get("stop"):
            break
    E = BASE
    write("batch-result.json", {"finished_utc": utc(), "attempted": len(entries),
          "not_attempted": URLS[len(entries):], "articles": entries,
          "stop": entries[-1]["stop"] if entries else None, "REST_requests_by_diagnostic": 0})


if __name__ == "__main__":
    if "--child" in sys.argv:
        asyncio.run(capture())
    else:
        batch()
