"""Offline proof of paced_get.py against a 127.0.0.1 http.server. Short gaps/cooldowns for the test only.
Run from repo root: PYTHONPATH=.:<this dir> venv/bin/python <this file> <scratch dir>"""
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from paced_get import PacedSession, Stopped

HITS = []            # (monotonic, path)
SCRIPT = {}          # path -> list of (status, headers) consumed per hit; last one repeats


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        HITS.append((time.monotonic(), self.path))
        plan = SCRIPT[self.path]
        status, headers = plan.pop(0) if len(plan) > 1 else plan[0]
        body = f"{status} {self.path}".encode()
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


srv = HTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_port}"
scratch = Path(sys.argv[1])
GAP, COOL = 1.0, 2.0


def session(tag, **kw):
    return PacedSession(scratch / tag, scratch / f"{tag}.log.md", min_gap_s=GAP, cooldown_s=COOL, **kw)


# T1: 200 then 200 — second request starts >= GAP after the first completed; files saved byte-for-byte.
SCRIPT.update({"/a": [(200, {})], "/b": [(200, {})]})
s = session("t1")
s.get(base + "/a", "a"); s.get(base + "/b", "b")
gap = HITS[-1][0] - HITS[-2][0]
assert gap >= GAP, gap
assert (scratch / "t1/a.body").read_bytes() == b"200 /a"
print(f"T1 PASS gap={gap:.2f}s >= {GAP}")

# T2: 429 with Retry-After: 2 -> waits ~2 s (not COOL), one retry -> 200. A LATER 429 -> hard stop, no 2nd cycle.
SCRIPT.update({"/ra": [(429, {"Retry-After": "2"}), (200, {})], "/later": [(429, {})]})
s = session("t2"); n0 = len(HITS); t0 = time.monotonic()
r = s.get(base + "/ra", "ra")
assert r.status_code == 200 and len(HITS) - n0 == 2
waited = HITS[-1][0] - HITS[-2][0]
assert 2.0 <= waited < 2.0 + GAP + 1, waited
try:
    s.get(base + "/later", "later"); raise SystemExit("T2 FAIL: no stop")
except Stopped as e:
    assert len(HITS) - n0 == 3, "later 429 must not be retried"
n_before = len(HITS)
try:
    s.get(base + "/a", "blocked-after-stop"); raise SystemExit("T2 FAIL: request after stop")
except Stopped:
    assert len(HITS) == n_before, "no request may leave after a stop"
print(f"T2 PASS Retry-After honored ({waited:.2f}s), one retry, later 429 -> stop, stop is sticky")

# T3: 429 without Retry-After -> default cooldown, ONE retry, still 429 -> BLOCKED.
SCRIPT.update({"/nora": [(429, {})]})
s = session("t3"); n0 = len(HITS)
try:
    s.get(base + "/nora", "nora"); raise SystemExit("T3 FAIL: no stop")
except Stopped as e:
    assert "BLOCKED" in str(e) and len(HITS) - n0 == 2
    waited = HITS[-1][0] - HITS[-2][0]
    assert waited >= COOL, waited
print(f"T3 PASS cooldown {waited:.2f}s >= {COOL}, exactly one retry, BLOCKED")

# T4: Retry-After beyond the deadline -> stop without waiting or retrying.
SCRIPT.update({"/long": [(429, {"Retry-After": "9999"})]})
s = session("t4", deadline_epoch=time.time() + 5); n0 = len(HITS); t0 = time.monotonic()
try:
    s.get(base + "/long", "long"); raise SystemExit("T4 FAIL")
except Stopped as e:
    assert "exceeds" in str(e) and len(HITS) - n0 == 1 and time.monotonic() - t0 < 2
print("T4 PASS Retry-After beyond budget -> immediate stop, no retry")
print("ALL PASS")
