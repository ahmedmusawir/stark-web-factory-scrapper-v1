"""Q2 T-21 native whole-flow instrument: DECIDE → COLLECT → PREPARE on a QA-owned loopback mini-site.

Builds the mini-site (home + services + contact pages, sitemap.xml,
wp/v2/types, wp/v2/pages metadata with one evidenced item and its item
endpoint) and runs the real public CLIs in order: decide recon --mode
sitemap, decide list, decide select with a QA actor (loopback fixture rows,
no --example marker because this flow does execute its plan), decide export,
collector collect (collection created UNDER THE SNAPSHOT ROOT so the
Prepare helper's confinement accepts it), and the Prepare helper into a fresh
derived directory. Dumps the prepared package for the agent authoring stage.

Per-stage oracle verification: sitemap-driven inventory rows (home, services,
plus a linked-heading candidate that is not fetched); /wp-json/wp/v2/types
requested WITHOUT _fields; individual metadata requested WITH the documented
projection and WITHOUT the 'content' field; the exported plan contains
exactly the selected pages (plus the evidenced single-item REST scope);
collected page bodies contain the known fixture texts; the collected REST
body is byte-identical to the served entity; the prepared Markdown contains
the known headings/paragraphs/list/CTA with the run record preserved. All
traffic is loopback-only (127.0.0.1 literal, OS-assigned port); owns and
closes its server. Writes JSON to argv[1].
"""
import hashlib
import json
import shutil
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, "/tmp/opencode/q2-scratch-20261016/snapshot-scoped")
from recon_pipeline import decide as dmod  # noqa: E402  (documented FIELDS projection oracle)

SCRATCH = Path("/tmp/opencode/q2-scratch-20261016")
SNAP = SCRATCH / "snapshot-scoped"
VENV = Path("/home/moose/PYTHON/stark-web-factory-scrapper-v1/venv/bin/python")
PREPARE = SNAP / "agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py"

HOME_PAGE = (
    "<html><head><title>Acme Fixture Home</title></head><body>"
    "<main><h1>Acme Fixture Home</h1>"
    "<p>Fixture home paragraph describing the workshop offering, with Ünïcode 中文 🦊 included "
    "so that rendered-body and prepared-Markdown fidelity can be checked byte-for-text.</p>"
    "<ul><li>Strategy engagement</li><li>Delivery support</li><li>Verification pass</li></ul>"
    "<a href=\"/contact\" class=\"cta\">Book the Workshop →</a> "
    "<a href=\"/services\">Explore services</a></main></body></html>")
SERVICES_PAGE = (
    "<html><head><title>Services Overview</title></head><body>"
    "<main><h1>Services Overview</h1>"
    "<h2>Strategy</h2><p>Strategy paragraph with ordinary fixture text for extraction checks.</p>"
    "<h2>Delivery</h2><p>Delivery paragraph with ordinary fixture text for extraction checks.</p>"
    "<h2>Verification</h2><p>Verification paragraph with more ordinary fixture text so that no "
    "structural heuristic refuses the page during native navigation.</p></main></body></html>")
CONTACT_PAGE = (
    "<html><head><title>Contact</title></head><body>"
    "<main><h1>Contact</h1><p>Contact page paragraph with enough ordinary text for structural "
    "heuristics; this page is linked but never selected, so it must not be fetched.</p>"
    "</main></body></html>")

HOME_TEXTS = ["Acme Fixture Home", "Book the Workshop", "Ünïcode 中文 🦊", "Strategy engagement"]
SERVICES_TEXTS = ["Services Overview", "Strategy", "Delivery", "Verification"]
FIELDS = dmod.FIELDS


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
            ctype, body, extra = self.server.routes[path]
            status = 200
        else:
            ctype, body, extra, status = "text/plain; charset=utf-8", b"missing", {}, 404
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        for key, value in extra.items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def start_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    origin = f"http://127.0.0.1:{server.server_port}"
    pages_meta = json.dumps([{"id": 7, "link": origin + "/services",
                              "title": {"rendered": "Services Overview"},
                              "type": "page", "date": "2026-10-01T10:00:00"}]).encode("utf-8")
    item7 = json.dumps({"id": 7, "link": origin + "/services",
                        "title": {"rendered": "Services Overview"},
                        "type": "page", "date": "2026-10-01T10:00:00"}).encode("utf-8")
    types = json.dumps({"page": {"name": "Pages", "rest_base": "pages",
                                 "rest_namespace": "wp/v2"}}).encode("utf-8")
    sitemap = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
               "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"
               f"<url><loc>{origin}/</loc></url>"
               f"<url><loc>{origin}/services</loc></url>"
               "</urlset>").encode("utf-8")
    server.routes = {
        "/": ("text/html; charset=utf-8", HOME_PAGE.encode("utf-8"), {}),
        "/services": ("text/html; charset=utf-8", SERVICES_PAGE.encode("utf-8"), {}),
        "/contact": ("text/html; charset=utf-8", CONTACT_PAGE.encode("utf-8"), {}),
        "/sitemap.xml": ("application/xml", sitemap, {}),
        "/wp-json/wp/v2/types": ("application/json", types, {}),
        "/wp-json/wp/v2/pages": ("application/json", pages_meta,
                                 {"x-wp-total": "1", "x-wp-totalpages": "1"}),
        "/wp-json/wp/v2/pages/7": ("application/json", item7, {}),
    }
    server.events = []
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, origin


def run_cli(args, timeout=300):
    proc = subprocess.run([str(VENV), *args], cwd=SNAP, capture_output=True, text=True,
                           timeout=timeout)
    return {"argv": args, "exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def main() -> int:
    server, origin = start_server()
    result = {"port_record": {"bind": "127.0.0.1", "port": server.server_port, "origin": origin},
              "fields_projection_oracle": FIELDS}
    try:
        work = SCRATCH / "t21"
        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
        recon_dir = work / "recon"
        r1 = run_cli(["-m", "recon_pipeline.decide", "recon", "--mode", "sitemap",
                      "--url", origin + "/", "--sitemap", origin + "/sitemap.xml",
                      "--out", str(recon_dir)])
        result["stage1_recon"] = r1
        inv_file = recon_dir / "inventory.json"
        inventory = json.loads(inv_file.read_bytes()) if inv_file.is_file() else {"items": []}
        items = inventory.get("items", [])
        by_url = {x.get("url"): x for x in items}
        home_row, services_row = by_url.get(origin + "/"), by_url.get(origin + "/services")
        contact_row = by_url.get(origin + "/contact")
        result["stage1_inventory"] = {
            "sealed_files": sorted(p.name for p in recon_dir.rglob("*")) if recon_dir.is_dir() else [],
            "items": items,
            "home_row": home_row, "services_row": services_row, "contact_linked_candidate": contact_row,
        }
        r2 = run_cli(["-m", "recon_pipeline.decide", "list", "--inventory", str(inv_file)])
        result["stage2_list"] = r2

        select_args = ["-m", "recon_pipeline.decide", "select", "--inventory", str(inv_file),
                       "--out", str(work / "decision.json"),
                       "--by", "Opy — Q2 QA (T-21 fixture flow)"]
        if home_row:
            select_args += ["--include-html", home_row["id"]]
        if services_row:
            select_args += ["--include-html", services_row["id"]]
        rest_scope_expected = None
        if services_row and services_row.get("rest_items"):
            select_args += ["--include-rest", services_row["id"]]
            rest_scope_expected = services_row["rest_items"]
        result["rest_scope_expected"] = rest_scope_expected
        r3 = run_cli(select_args)
        result["stage3_select"] = r3
        decision = json.loads((work / "decision.json").read_bytes()) \
            if (work / "decision.json").is_file() else {}
        result["stage3_decision"] = decision

        r4 = run_cli(["-m", "recon_pipeline.decide", "export", "--inventory", str(inv_file),
                      "--decision", str(work / "decision.json"), "--out", str(work / "plan.json")])
        result["stage4_export"] = r4
        plan = json.loads((work / "plan.json").read_bytes()) if (work / "plan.json").is_file() else {}
        plan_review = json.loads((work / "plan.review.json").read_bytes()) \
            if (work / "plan.review.json").is_file() else None
        result["stage4_plan"] = {"plan": plan, "plan_review": plan_review}

        coll = SNAP / "outputs/collections/qa-t21-flow"
        if coll.exists():
            shutil.rmtree(coll)
        r5 = run_cli(["-m", "recon_pipeline", "collect", "--collection", str(coll),
                      "--plan", str(work / "plan.json")], timeout=300)
        result["stage5_collect"] = r5
        checklist = json.loads((coll / "checklist.json").read_bytes()) \
            if (coll / "checklist.json").is_file() else {}
        result["stage5_checklist"] = {
            "items": [{"id": x.get("id"), "kind": x.get("kind"), "url": x.get("url"),
                       "status": x.get("status"), "error": x.get("error")}
                      for x in checklist.get("items", [])],
            "runs": checklist.get("runs"),
        }
        saved = {}
        rest_byte_identical = None
        page_texts_ok = {}
        for it in checklist.get("items", []):
            ref = it.get("result") or {}
            if not ref:
                continue
            meta = json.loads((coll / ref["file"]).read_bytes())
            body = (coll / meta["body_file"]).read_bytes()
            saved[it["id"]] = {"url": meta.get("url"), "kind": meta.get("kind"),
                               "ok": meta.get("ok"), "error": meta.get("error"),
                               "body_complete": meta.get("body_complete"),
                               "sha256": meta.get("sha256"), "bytes": meta.get("bytes"),
                               "status": meta.get("status"), "transport": meta.get("transport"),
                               "coverage_scope": meta.get("coverage_scope"),
                               "coverage_note": meta.get("coverage_note"),
                               "header_keys": sorted((meta.get("headers") or {}).keys())}
            if it.get("kind") == "page":
                text = body.decode("utf-8", "replace")
                wanted = HOME_TEXTS if str(meta.get("url", "")).endswith("/") else SERVICES_TEXTS
                page_texts_ok[it["id"]] = {w: (w in text) for w in wanted}
            if it.get("kind") == "rest":
                path = urlsplit(meta.get("url", "")).path
                served = server.routes.get(path, (None, b"", None))[1]
                rest_byte_identical = bool(served) and sha(body) == sha(served)
                saved[it["id"]]["rest_body_sha256"] = sha(body)
                saved[it["id"]]["served_entity_sha256"] = sha(served) if served else None
        result["stage5_saved_results"] = saved
        result["stage5_page_texts_oracle"] = page_texts_ok
        result["stage5_rest_bytes_identical"] = rest_byte_identical

        out = SNAP / "outputs/prepared/qa-t21-prepared"
        if out.exists():
            shutil.rmtree(out)
        r6 = run_cli([str(PREPARE), "--collection", str(coll), "--out", str(out)])
        result["stage6_prepare"] = r6
        index = json.loads((out / "SOURCE_INDEX.json").read_bytes()) \
            if (out / "SOURCE_INDEX.json").is_file() else None
        prepared_pages = {p.name: p.read_text(encoding="utf-8")
                          for p in sorted((out / "pages").glob("*.md"))} \
            if (out / "pages").is_dir() else {}
        boiler = (out / "BOILERPLATE.md").read_text(encoding="utf-8") \
            if (out / "BOILERPLATE.md").is_file() else None
        result["prepared_dump"] = {
            "out_created": out.exists(),
            "package_files": sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file()),
            "index": index, "pages": prepared_pages, "boilerplate": boiler,
        }
        prepared_home_md = next((t for t in prepared_pages.values()
                                 if "Acme Fixture Home" in t), "")
        prepared_services_md = next((t for t in prepared_pages.values()
                                     if "Services Overview" in t), "")
        result["prepared_text_oracle"] = {
            "home_md_has": {w: (w in prepared_home_md) for w in HOME_TEXTS} if prepared_home_md else None,
            "services_md_has": {w: (w in prepared_services_md) for w in SERVICES_TEXTS}
            if prepared_services_md else None,
        }

        events = server.events
        result["server_events"] = events
        types_events = [e for e in events if e["path"] == "/wp-json/wp/v2/types"]
        meta_events = [e for e in events if e["path"] == "/wp-json/wp/v2/pages" and e["query"]]
        proj_values = [parse_qs(e["query"]).get("_fields", [""])[0] for e in meta_events]
        result["decide_request_shapes"] = {
            "types_requests": len(types_events),
            "types_without_fields": bool(types_events)
            and all("_fields" not in e["query"] for e in types_events),
            "metadata_requests": len(meta_events),
            "metadata_queries": [e["query"] for e in meta_events],
            "projection_matches_fields": any(v == FIELDS for v in proj_values),
            "content_not_projected": all("content" not in v for v in proj_values),
        }
        known = set(server.routes) | {"/favicon.ico"}
        result["traffic_oracle"] = {
            "contact_fetched": any(e["path"] == "/contact" for e in events),
            "unexpected_paths": sorted({e["path"] for e in events} - known),
            "all_loopback_by_construction": True,
        }

        result["assessment"] = {
            "recon_exit_zero": r1["exit"] == 0,
            "inventory_has_home_and_services": bool(home_row and services_row),
            "linked_contact_candidate_not_fetched": not result["traffic_oracle"]["contact_fetched"],
            "types_without_fields": result["decide_request_shapes"]["types_without_fields"],
            "metadata_projection_ok": (result["decide_request_shapes"]["projection_matches_fields"]
                                       and result["decide_request_shapes"]["content_not_projected"]),
            "select_export_exit_zero": r3["exit"] == 0 and r4["exit"] == 0,
            "plan_pages_exact": sorted(plan.get("pages") or []) == sorted([origin + "/", origin + "/services"]),
            "plan_has_rest_scope": bool(plan.get("rest")),
            "collect_exit_zero": r5["exit"] == 0,
            "all_items_completed": bool(checklist.get("items"))
            and all(x.get("status") == "completed" for x in checklist.get("items", [])),
            "page_bodies_contain_oracle": bool(page_texts_ok)
            and all(all(v.values()) for v in page_texts_ok.values()),
            "rest_bytes_identical": rest_byte_identical,
            "prepare_exit_zero": r6["exit"] == 0,
            "prepared_md_contains_oracle": (
                bool(result["prepared_text_oracle"]["home_md_has"])
                and all(result["prepared_text_oracle"]["home_md_has"].values())
                and all(result["prepared_text_oracle"]["services_md_has"].values())),
        }
    finally:
        server.shutdown()
        server.server_close()

    out_path = Path(sys.argv[1])
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    a = result["assessment"]
    print("recon exit:", a and result["stage1_recon"]["exit"],
          "| inventory rows:", len(result["stage1_inventory"]["items"]),
          "| home+services:", a["inventory_has_home_and_services"],
          "| contact candidate (not fetched):", a["linked_contact_candidate_not_fetched"])
    print("types without _fields:", a["types_without_fields"],
          "| metadata projection ok:", a["metadata_projection_ok"])
    print("select/export exit zero:", a["select_export_exit_zero"],
          "| plan pages exact:", a["plan_pages_exact"], "| plan has rest scope:", a["plan_has_rest_scope"])
    print("collect exit:", result["stage5_collect"]["exit"],
          "| all completed:", a["all_items_completed"],
          "| page oracle:", a["page_bodies_contain_oracle"],
          "| rest bytes identical:", a["rest_bytes_identical"])
    print("prepare exit:", result["stage6_prepare"]["exit"],
          "| prepared md oracle:", a["prepared_md_contains_oracle"])
    print("unexpected paths:", result["traffic_oracle"]["unexpected_paths"])
    print("assessment:", json.dumps(a))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())