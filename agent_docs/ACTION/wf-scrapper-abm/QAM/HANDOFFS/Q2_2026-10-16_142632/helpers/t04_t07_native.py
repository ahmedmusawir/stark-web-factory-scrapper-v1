"""Q2 T-04 + T-07 native instrument: real Crawl4AI/Chromium loopback run.

T-04: two planned documents collected through the public CLI with the DEFAULT
gap (no --gap override; the resolved gap is recorded from the run record).
Native monotonic timing: the collector's own request records must show
requests[1].start - requests[0].completion >= 5.0s, corroborated by the
QA-owned loopback server's arrival observations. An unlinked, unselected
route is the no-request oracle (a linked subresource is not); background
browser traffic (subresource image, favicon) is recorded separately from the
planned-call count. 429/challenge stop and the JSON-quoted challenge negative
are cited from the T-22 regression native evidence.

T-07: one planned document performs a controlled DOM mutation at parse time.
The collector's saved UTF-8 body and hash must differ from the server's
original response bytes (rendered HTML vs original bytes), contain the mutated
DOM state and the Unicode, and an independent Playwright Chromium observation
of the same page must confirm the rendered state (serialization differences
recorded honestly — not a circular comparison to the product's own digest).
Empty-body/401/403/429 and false-positive challenge controls are cited from
the regression.

Evidence note: SELECTED_COLLECTOR_EVIDENCE deposition is a suite-harness
mechanism (tests/test_selected_collector.py line 228), not product behavior;
this QA run records its own server event log and the checklist run record.
Owns and closes its server and browser. Zero external requests (127.0.0.1
literal only). Writes JSON to argv[1].
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRATCH = Path("/tmp/opencode/q2-scratch-20261016")
SNAP = SCRATCH / "snapshot-scoped"
VENV = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python")
LANE = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1/agent_docs/ACTION/"
            "wf-scrapper-abm/QAM/HANDOFFS/Q2_2026-10-16_142632")

PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d4944415478da63fccf00f60300030301003bce9ad5"
    "0000000049454e44ae426082")

MUT_PAGE = (
    "<html><head><title>Native Fixture</title></head><body>"
    "<main><h1>Native Heading Ünïcode 中文 🦊</h1>"
    "<div id=\"target\">OriginalText</div>"
    "<p>Fixture paragraph one for rendered comparison.</p>"
    "<ul><li>Alpha item</li><li>Beta item</li></ul>"
    "<a href=\"/linked-unselected\">Visit the linked page</a>"
    "<img src=\"/pixel.png\" alt=\"pixel\"></main>"
    "<script>document.getElementById('target').textContent='MutatedText-বাংলা-🦊';</script>"
    "</body></html>")
PLAIN_PAGE = (
    "<html><head><title>Second Document</title></head><body>"
    "<main><h1>Second Document</h1>"
    "<p>This second planned document carries several paragraphs of ordinary fixture text so that "
    "it looks like an ordinary content page to library-level structural checks. It exists to "
    "measure the default pacing gap between two planned calls in a native browser run.</p>"
    "<p>The text includes a list of service areas: strategy, delivery, verification and "
    "packaging. Each paragraph adds visible characters so the rendered document is not minimal "
    "and no structural heuristic refuses the page before the pacing measurement completes.</p>"
    "<ul><li>Strategy paragraph one</li><li>Delivery paragraph two</li>"
    "<li>Verification paragraph three</li><li>Packaging paragraph four</li></ul>"
    "<p>Closing paragraph with enough ordinary words to complete a realistic document body for "
    "the structural heuristics of the browser automation library in use during collection.</p>"
    "</main></body></html>")
LINKED_PAGE = ("<html><body><main><h1>Linked Unselected</h1>"
               "<p>Linked from doc-mut but not in the plan.</p></main></body></html>")
UNLINKED_PAGE = ("<html><body><main><h1>Never Linked</h1>"
                 "<p>Unlinked oracle route, not in the plan.</p></main></body></html>")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path, _, query = self.path.partition("?")
        self.server.events.append({
            "arrival": time.monotonic(), "arrival_epoch": time.time(),
            "method": self.command, "path": path, "query": query,
            "user_agent": self.headers.get("user-agent", ""),
            "accept": self.headers.get("accept", ""),
        })
        if path in self.server.routes:
            ctype, body = self.server.routes[path]
            status = 200
        else:
            ctype, body, status = "text/plain; charset=utf-8", b"missing", 404
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def start_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.routes = {
        "/doc-mut": ("text/html; charset=utf-8", MUT_PAGE.encode("utf-8")),
        "/doc-b": ("text/html; charset=utf-8", PLAIN_PAGE.encode("utf-8")),
        "/linked-unselected": ("text/html; charset=utf-8", LINKED_PAGE.encode("utf-8")),
        "/unlinked-unselected": ("text/html; charset=utf-8", UNLINKED_PAGE.encode("utf-8")),
        "/pixel.png": ("image/png", PNG_1PX),
    }
    server.events = []
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"


def main() -> int:
    result = {"bindings": {
        "t04": "two planned documents, default gap (no override), native monotonic timing, unlinked-route oracle",
        "t07": "DOM-mutation rendered-vs-original-bytes plus independent Playwright observation",
        "evidence_note": ("SELECTED_COLLECTOR_EVIDENCE deposition is a suite-harness mechanism "
                          "(tests/test_selected_collector.py line 228), not product behavior; this "
                          "QA run records its own server event log and the checklist run record as "
                          "native evidence"),
        "g3_correction": ("run 1 misread the checklist path guard (collection directory is not a "
                          "file), producing an empty parse while the underlying run was valid "
                          "(native gap 5.006s recorded in the checklist, preserved as "
                          "t04_t07_result.run1.json / t04-t07-checklist.run1.json); /doc-b was "
                          "refused by the Crawl4AI structural check ('minimal_text on small page', "
                          "121 bytes / 32 visible chars) and the collector preserved the failure "
                          "honestly (page_capture_failed, exit 2 partial, no fabricated success) — "
                          "retained as a T-07 honest-failure observation; fixture enriched for this "
                          "corrected run"),
    }}
    server, origin = start_server()
    result["port_record"] = {"bind": "127.0.0.1", "port": server.server_port, "origin": origin}
    try:
        work = SCRATCH / "t04-native"
        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
        coll = work / "collection"
        plan = {"pages": [origin + "/doc-mut", origin + "/doc-b"], "rest": []}
        plan_path = work / "plan.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        t0 = time.monotonic()
        proc = subprocess.run(
            [str(VENV), "-m", "recon_pipeline", "collect",
             "--collection", str(coll), "--plan", str(plan_path)],
            cwd=SNAP, env=env, capture_output=True, text=True, timeout=240)
        result["cli"] = {"exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr,
                         "wall_elapsed_s": round(time.monotonic() - t0, 2)}

        checklist_file = coll / "checklist.json"
        checklist = json.loads(checklist_file.read_bytes()) if checklist_file.is_file() else {}
        run_rec = (checklist.get("runs") or [{}])[-1]
        reqs = run_rec.get("requests") or []
        result["run_record"] = run_rec
        collector_gap = None
        if len(reqs) >= 2 and "completion" in reqs[0] and "start" in reqs[1]:
            collector_gap = reqs[1]["start"] - reqs[0]["completion"]
        events = server.events
        result["server_events"] = events

        def arrivals(path):
            return [e["arrival"] for e in events if e["path"] == path]

        a_mut, a_b = arrivals("/doc-mut"), arrivals("/doc-b")
        server_gap = (min(a_b) - max(a_mut)) if a_mut and a_b else None
        result["t04_pacing"] = {
            "resolved_gap_seconds": run_rec.get("gap_seconds"),
            "gap_override_passed": False,
            "planned_calls_recorded": len(reqs),
            "collector_native_gap_s": collector_gap,
            "collector_gap_pass_5s": collector_gap is not None and collector_gap >= 5.0,
            "server_observed_gap_s": server_gap,
            "server_gap_pass_5s": server_gap is not None and server_gap >= 5.0,
            "preceding_completion_consistent": (
                len(reqs) >= 2 and reqs[1].get("preceding_completion") == reqs[0].get("completion")),
            "unlinked_route_requested": bool(arrivals("/unlinked-unselected")),
            "unlinked_route_oracle_pass": not arrivals("/unlinked-unselected"),
            "linked_unselected_requested": bool(arrivals("/linked-unselected")),
            "background_traffic": {
                "pixel_png_requests": len(arrivals("/pixel.png")),
                "favicon_requests": len(arrivals("/favicon.ico")),
                "browser_traffic_counter": run_rec.get("browser_traffic"),
                "note": ("subresource/favicon requests are browser background traffic, recorded "
                         "in the server log and traffic counter, not in the planned-call records"),
            },
            "planned_calls_exactly_two": len(reqs) == 2,
        }

        saved = {}
        mut_body = None
        for it in checklist.get("items", []):
            ref = it.get("result") or {}
            if not ref:
                continue
            meta = json.loads((coll / ref["file"]).read_bytes())
            body = (coll / meta["body_file"]).read_bytes()
            saved[it["id"]] = {
                "url": meta.get("url"), "kind": meta.get("kind"), "ok": meta.get("ok"),
                "error": meta.get("error"), "body_complete": meta.get("body_complete"),
                "bytes": meta.get("bytes"), "sha256": meta.get("sha256"),
                "status": meta.get("status"), "transport": meta.get("transport"),
                "header_keys": sorted((meta.get("headers") or {}).keys()),
                "saved_at": meta.get("saved_at"), "library_success": meta.get("library_success"),
            }
            if str(meta.get("url", "")).endswith("/doc-mut"):
                mut_body = body
        result["saved_results"] = saved

        rendered = None
        render_error = None
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(origin + "/doc-mut")
                page.wait_for_timeout(600)
                rendered = page.content()
                browser.close()
        except Exception as exc:  # observation failure is recorded, not fatal
            render_error = type(exc).__name__ + ": " + str(exc)[:300]

        original = MUT_PAGE.encode("utf-8")
        if mut_body is not None:
            text = mut_body.decode("utf-8", "replace")
            t07 = {
                "original_payload_sha256": sha(original),
                "saved_body_sha256": sha(mut_body),
                "rendered_differs_from_original_bytes": sha(mut_body) != sha(original),
                "mutation_in_saved_body": "MutatedText-বাংলা-🦊" in text,
                "original_text_absent_from_saved": "OriginalText" not in text,
                "unicode_preserved": "Ünïcode 中文 🦊" in text,
                "rendered_vs_bytes_recorded": "saved page body is rendered HTML (post-mutation), not the original response bytes",
            }
            if rendered is not None:
                t07["independent_playwright_observation"] = {
                    "content_sha256": sha(rendered.encode("utf-8")),
                    "byte_identical_to_saved": rendered.encode("utf-8") == mut_body,
                    "mutation_in_independent_observation": "MutatedText-বাংলা-🦊" in rendered,
                    "serialization_note": ("page.content() serialization from a separate Chromium "
                                           "session; byte differences, if any, are recorded rather "
                                           "than treated as failure"),
                }
            result["t07_fidelity"] = t07
        else:
            result["t07_fidelity"] = {"error": "doc-mut item not found in saved results"}
        if render_error:
            result["t07_fidelity"]["playwright_error"] = render_error

        result["t11_records"] = {
            "runtime": run_rec.get("runtime"),
            "cleanup_messages": run_rec.get("cleanup_messages"),
            "collection_outcome": run_rec.get("collection_outcome"),
            "stop_reason": run_rec.get("stop_reason"),
            "elapsed_s": run_rec.get("elapsed_s"),
            "observed_user_agent_first_page": next(
                (e["user_agent"] for e in events if e["path"] == "/doc-mut"), None),
            "user_agent_matches_runtime_record": (
                next((e["user_agent"] for e in events if e["path"] == "/doc-mut"), "")
                == (run_rec.get("runtime") or {}).get("user_agent", "")),
        }

        result["assessment"] = {
            "collect_exit_zero": proc.returncode == 0,
            "both_items_completed": all(x.get("status") == "completed"
                                        for x in checklist.get("items", [])),
            "t04_pass": (result["t04_pacing"]["collector_gap_pass_5s"]
                         and result["t04_pacing"]["server_gap_pass_5s"]
                         and result["t04_pacing"]["unlinked_route_oracle_pass"]
                         and result["t04_pacing"]["planned_calls_exactly_two"]),
            "t07_pass": (isinstance(result.get("t07_fidelity"), dict)
                         and result["t07_fidelity"].get("rendered_differs_from_original_bytes")
                         and result["t07_fidelity"].get("mutation_in_saved_body")
                         and result["t07_fidelity"].get("original_text_absent_from_saved")
                         and result["t07_fidelity"].get("unicode_preserved")),
        }
    finally:
        server.shutdown()
        server.server_close()

    (LANE / "native").mkdir(parents=True, exist_ok=True)
    shutil.copy2(coll / "checklist.json", LANE / "native" / "t04-t07-checklist.json")
    out_path = Path(sys.argv[1])
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    t4, t7 = result["t04_pacing"], result.get("t07_fidelity", {})
    print("collect exit:", result["cli"]["exit"], "| wall:", result["cli"]["wall_elapsed_s"], "s")
    print("resolved gap:", t4["resolved_gap_seconds"], "| collector native gap:",
          t4["collector_native_gap_s"], "pass:", t4["collector_gap_pass_5s"],
          "| server gap:", t4["server_observed_gap_s"], "pass:", t4["server_gap_pass_5s"])
    print("planned calls recorded:", t4["planned_calls_recorded"],
          "| unlinked oracle pass:", t4["unlinked_route_oracle_pass"],
          "| linked-unselected requested:", t4["linked_unselected_requested"],
          "| pixel (background):", t4["background_traffic"]["pixel_png_requests"])
    print("UA matches runtime record:", result["t11_records"]["user_agent_matches_runtime_record"])
    if "original_payload_sha256" in t7:
        print("T-07 rendered!=original:", t7["rendered_differs_from_original_bytes"],
              "| mutation saved:", t7["mutation_in_saved_body"],
              "| original absent:", t7["original_text_absent_from_saved"],
              "| unicode:", t7["unicode_preserved"])
        obs = t7.get("independent_playwright_observation")
        if obs:
            print("independent observation: mutation:", obs["mutation_in_independent_observation"],
                  "| byte-identical to saved:", obs["byte_identical_to_saved"])
    print("assessment:", json.dumps(result["assessment"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())