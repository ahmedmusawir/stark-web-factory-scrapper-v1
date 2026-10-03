"""Useful blog extraction, then one conditional browser-session REST read.

No discovery, batch writer, direct Playwright import, retry, or alternate URL.
Invoke once with the existing venv. Parent supervises its browser child for 180s.
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

E = Path(__file__).resolve().parent
ROOT = E.parents[5]
TARGET = "https://cyberizegroup.com/blog/"
REST = "https://cyberizegroup.com/wp-json/wp/v2/posts?per_page=1&_fields=id,link,title,content"
HOSTS = {"cyberizegroup.com", "www.cyberizegroup.com"}


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write(name, obj):
    with (E / name).open("x") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def safe_url(url):
    if url == REST:
        return REST  # Exact authorized public query, no sensitive parameters.
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.hostname or "", p.path,
                       "[query-redacted]" if p.query else "", ""))


def event(kind, **data):
    with (E / "browser-events.jsonl").open("a") as f:
        f.write(json.dumps({"utc": utc(), "event": kind, **data}) + "\n")



def verify_articles(html, markdown):
    from bs4 import BeautifulSoup
    import html as html_module
    from urllib.parse import urljoin
    normalize = lambda text: re.sub(r"[^a-z0-9]+", " ", html_module.unescape(text).lower()).strip()
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.select("header, footer, nav, script, style"):
        node.decompose()
    md_normalized = normalize(markdown)
    matches = []
    seen = set()
    for heading in soup.find_all(["h2", "h3", "h4"]):
        title = heading.get_text(" ", strip=True)
        if len(title) < 12 or len(title.split()) < 3:
            continue
        link = heading.find("a", href=True)
        if link is None and heading.parent and heading.parent.name == "a":
            link = heading.parent
        if link is None:
            continue
        url = urljoin(TARGET, link.get("href", ""))
        parsed = urlsplit(url)
        if parsed.hostname not in HOSTS or parsed.path.rstrip("/") in {"", "/blog", "/contact", "/contact-us"}:
            continue
        if any(part in parsed.path for part in ("/category/", "/tag/", "/page/", "/wp-")):
            continue
        in_md = normalize(title) in md_normalized and url.rstrip("/") in markdown
        if in_md and url not in seen:
            seen.add(url)
            matches.append({"heading": title, "link": url, "html_heading_tag": heading.name,
                            "heading_and_link_present_in_markdown": True})
    return {"outcome": "success" if len(matches) >= 2 else "insufficient_article_evidence",
            "rule": "At least two distinct same-site article links nested in h2/h3/h4 (or wrapping headings), with both title and URL also in saved Markdown; exclude navigation and category/tag pagination links.",
            "matching_article_count": len(matches), "articles": matches}


def verify_post(post):
    from bs4 import BeautifulSoup
    if not isinstance(post, dict):
        return {"valid": False, "reason": "record_not_object"}
    title = post.get("title")
    content = post.get("content")
    rendered_title = title.get("rendered") if isinstance(title, dict) else None
    rendered_content = content.get("rendered") if isinstance(content, dict) else None
    plain_title = BeautifulSoup(rendered_title, "html.parser").get_text(" ", strip=True) if isinstance(rendered_title, str) else ""
    plain_content = BeautifulSoup(rendered_content, "html.parser").get_text(" ", strip=True) if isinstance(rendered_content, str) else ""
    valid_id = type(post.get("id")) is int and post["id"] > 0
    valid_link = isinstance(post.get("link"), str) and urlsplit(post["link"]).scheme in {"http", "https"} and urlsplit(post["link"]).hostname in HOSTS
    return {"valid": bool(valid_id and valid_link and plain_title and plain_content),
            "missing_fields": [key for key in ("id", "link", "title", "content") if key not in post],
            "null_fields": [key for key in ("id", "link", "title", "content") if key in post and post[key] is None],
            "id": post.get("id"), "link": post.get("link"), "title_text": plain_title,
            "id_valid": valid_id, "link_valid": valid_link,
            "title_rendered_type": type(rendered_title).__name__, "content_rendered_type": type(rendered_content).__name__,
            "content_rendered_characters": len(rendered_content) if isinstance(rendered_content, str) else None,
            "content_text_characters": len(plain_content), "content_empty_after_stripping_markup": not bool(plain_content)}


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
             "html_bytes": 0, "markdown_characters": 0, "actual_blog": False,
             "page_extraction": {"outcome": "not_completed"},
             "rest_extraction": {"outcome": "not_attempted", "url": REST},
             "rest_authorized": False, "rest_requests_dispatched": 0}
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
            if request.url == REST and not reason:
                if not state["rest_authorized"] or state["rest_requests_dispatched"]:
                    reason = "unauthorized_or_duplicate_REST_request"
                else:
                    state["rest_requests_dispatched"] += 1
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
                        state["html_bytes" if key == "html" else "markdown_characters"] = len(data) if key == "html" else len(content)
                # Exception messages can contain page data: retain only local log.
                state["product_result"] = {k: v for k, v in result.items() if k != "error"}
                state["product_error_present"] = bool(result.get("error"))
                page_ok = bool(not stopped.is_set() and result.get("ok") and
                               state["main_responses"] and state["main_responses"][-1]["status"] == 200)
                if page_ok and (E / "returned.html").exists() and (E / "returned.md").exists():
                    verification = verify_articles((E / "returned.html").read_text(), (E / "returned.md").read_text())
                    state["page_extraction"] = verification
                    write("article-verification.json", verification)
                    event("page_extraction_verified", outcome=verification["outcome"], article_count=verification["matching_article_count"])
                    state["actual_blog"] = verification["outcome"] == "success"
                else:
                    state["page_extraction"] = {"outcome": "failed_or_interrupted", "stop": state["stop"]}
                if state["actual_blog"] and not stopped.is_set():
                    gap_start = time.monotonic()
                    state["rest_extraction"]["wait_started_utc"] = utc()
                    await asyncio.sleep(5)
                    gap = time.monotonic() - gap_start
                    if stopped.is_set():
                        state["rest_extraction"]["outcome"] = "not_attempted_stop_during_wait"
                    elif not primary_page or primary_page.is_closed():
                        state["rest_extraction"]["outcome"] = "not_attempted_original_page_unavailable"
                    else:
                        state["rest_authorized"] = True
                        rest = state["rest_extraction"]
                        rest.update({"outcome": "started", "started_utc": utc(), "preceding_wait_seconds": gap,
                                     "transport": "window.fetch via page.evaluate in the SAME Chromium page and BrowserContext used by crawl_page",
                                     "method": "GET", "redirect_mode": "error", "timeout_ms": 30000})
                        event("REST_start", url=REST, preceding_wait_seconds=gap, transport=rest["transport"])
                        try:
                            response = await primary_page.evaluate("""async url => {
                                const r = await fetch(url, {method: 'GET', redirect: 'error',
                                    headers: {'Accept': 'application/json'}, signal: AbortSignal.timeout(30000)});
                                const bytes = Array.from(new Uint8Array(await r.arrayBuffer()));
                                return {status: r.status, url: r.url, redirected: r.redirected,
                                    content_type: r.headers.get('content-type'), body: bytes};
                            }""", REST)
                            body = bytes(response.pop("body"))
                            with (E / "rest-response.body").open("xb") as f:
                                f.write(body)
                            rest.update(response)
                            rest.update({"body_bytes": len(body), "body_sha256": hashlib.sha256(body).hexdigest(), "body_file": "rest-response.body"})
                            text = body.decode("utf-8", errors="replace")
                            if re.search(r"<title[^>]*>\s*(just a moment|attention required|access denied)", text, re.I):
                                stop("explicit_REST_challenge", resource={"url": REST, "main_document": False})
                            try:
                                collection = json.loads(body)
                                rest["is_collection"] = isinstance(collection, list)
                                rest["record_count"] = len(collection) if isinstance(collection, list) else None
                                checks = []
                                if isinstance(collection, list):
                                    for post in collection:
                                        checks.append(verify_post(post))
                                rest["records"] = checks
                                rest["outcome"] = ("success" if response["status"] == 200 and checks and all(p["valid"] for p in checks) and not stopped.is_set()
                                                   else "empty_collection" if response["status"] == 200 and collection == [] and not stopped.is_set()
                                                   else "failed_validation_or_stopped")
                            except (ValueError, TypeError):
                                rest["outcome"] = "non_JSON_response"
                        except Exception as exc:
                            rest["outcome"] = "interrupted_or_transport_error"
                            rest["exception_type"] = type(exc).__name__
                            rows = [r for r in state["responses"] if r["url"] == REST]
                            if rows:
                                rest["status"] = rows[-1]["status"]
                                rest["headers"] = rows[-1]["headers"]
                            rest["body_saved"] = False
                        rest["ended_utc"] = utc()
                        event("REST_finished", outcome=rest["outcome"], status=rest.get("status"))
                        write("rest-result.json", rest)
                write("page-result.json", {"outcome": state["page_extraction"], "title": state["title"], "url": state["final_url"],
                                          "html_bytes": state["html_bytes"], "markdown_characters": state["markdown_characters"]})
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
        event("capture_finished", actual_blog=state["actual_blog"], stop=state["stop"])


def supervise():
    assert subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() == "wf-scrapper-abm"
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == "3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f"
    write("RUN_ONCE.json", {"utc": utc(), "target": TARGET, "ceiling_seconds": 180})
    started = time.monotonic()
    owned = {}
    with (E / "browser-output.local.log").open("xb") as log:
        child = subprocess.Popen([sys.executable, "-B", __file__, "--child"], cwd=ROOT,
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


if __name__ == "__main__":
    if "--child" in sys.argv:
        asyncio.run(capture())
    else:
        supervise()
