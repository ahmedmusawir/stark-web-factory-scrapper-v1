"""Recovery-mission pacing helper (diagnostic evidence tool, not product code).

One in-flight request at a time; >= min_gap_s between a completed response and the next request;
every response saved (body bytes, headers, meta) and logged. 429 policy (Director-approved):
  first 429  -> pause everything; honor Retry-After, else wait cooldown_s; ONE retry of the same URL.
  retry 429  -> stop, BLOCKED.           any later 429 -> stop (no second cooldown cycle).
  Retry-After beyond the deadline -> stop.
Run from the repo root so discover_site is importable.
"""
import json
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

from discover_site.sitemap_utils import USER_AGENT

KEY_HEADERS = ("Content-Type", "Content-Length", "Retry-After", "X-ac", "X-WP-Total", "X-WP-TotalPages",
               "Host-Header", "Server", "Cache-Control", "Age", "Location")


class Stopped(RuntimeError):
    """Hard stop: no further live requests are allowed in this session."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class PacedSession:
    def __init__(self, out_dir, log_path, *, min_gap_s=15.0, cooldown_s=300.0, deadline_epoch=None, timeout_s=30):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = Path(log_path)
        self.min_gap_s, self.cooldown_s, self.timeout_s = min_gap_s, cooldown_s, timeout_s
        self.deadline_epoch = deadline_epoch
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.next_allowed_at = 0.0          # time.monotonic() value
        self.cooldown_used = False
        self.stopped = None                 # reason string once stopped
        self.request_count = 0

    def _log(self, line):
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        print(line, flush=True)

    def _stop(self, reason):
        self.stopped = reason
        self._log(f"- {utc_now()} **STOP** {reason}")
        raise Stopped(reason)

    def _retry_after_s(self, value):
        if not value:
            return None
        try:
            return max(0.0, float(value))
        except ValueError:
            try:
                return max(0.0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
            except (TypeError, ValueError):
                return None

    def _once(self, url, name):
        wait = self.next_allowed_at - time.monotonic()
        if wait > 0:
            self._log(f"- {utc_now()} pace wait {wait:.1f}s")
            time.sleep(wait)
        self.request_count += 1
        at, started = utc_now(), time.monotonic()
        try:
            resp = self.session.get(url, timeout=self.timeout_s, allow_redirects=False)
        except requests.RequestException as e:
            self.next_allowed_at = time.monotonic() + self.min_gap_s
            self._log(f"- {at} GET {url} -> EXCEPTION {e!r}")
            self._stop(f"network exception on {url}")
        elapsed = round(time.monotonic() - started, 2)
        self.next_allowed_at = time.monotonic() + self.min_gap_s   # gap counts from response completion
        (self.out_dir / f"{name}.body").write_bytes(resp.content)
        (self.out_dir / f"{name}.headers.json").write_text(json.dumps(dict(resp.headers), indent=2), encoding="utf-8")
        meta = {"n": self.request_count, "url": url, "at": at, "status": resp.status_code, "elapsed_s": elapsed,
                "body_bytes": len(resp.content), "requests_version": requests.__version__, "user_agent": USER_AGENT}
        (self.out_dir / f"{name}.meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        keys = {k: resp.headers[k] for k in KEY_HEADERS if k in resp.headers}
        self._log(f"- {at} #{self.request_count} GET {url} -> **{resp.status_code}** {len(resp.content)} B "
                  f"{elapsed}s {json.dumps(keys)} -> `{name}.*`")
        return resp

    def get(self, url, name):
        if self.stopped:
            raise Stopped(self.stopped)
        resp = self._once(url, name)
        if resp.status_code != 429:
            return resp
        if self.cooldown_used:
            self._stop(f"429 on {url} after the one allowed cooldown cycle — live work ends")
        self.cooldown_used = True
        retry_after = self._retry_after_s(resp.headers.get("Retry-After"))
        wait = retry_after if retry_after is not None else self.cooldown_s
        if self.deadline_epoch is not None and time.time() + wait > self.deadline_epoch:
            self._stop(f"429 on {url}; required wait {wait:.0f}s exceeds the remaining budget")
        self._log(f"- {utc_now()} first 429: ALL requests paused {wait:.0f}s "
                  f"({'Retry-After' if retry_after is not None else 'no Retry-After, default cooldown'}), then ONE retry")
        time.sleep(wait)
        self.next_allowed_at = max(self.next_allowed_at, time.monotonic())
        resp = self._once(url, name + ".retry")
        if resp.status_code == 429:
            self._stop(f"retry of {url} also 429 — BLOCKED")
        return resp
