# BIM-000 Retrospective — web-factory-p1-bim000

> Closed 2026-09-05. SOL Gate Q: PASS. Certified `qa/web-factory-p1-bim000` @ `81099eedb0b7072ceaa8ee20ebaf336466a369bb`. Written by Claudy (Engineer) at close-out; lesson candidates live in WEB_FACTORY_P1_DOCTRINE_JOURNAL and are not repeated here.

## What worked
- **Recon before authoring.** The 2026-09-04 recon and run-002 analysis gave the brief exact file:line targets; every Stage 2 chunk landed on a known defect, none were discovered mid-build.
- **Controlled Crawl4AI upgrade as its own stage.** 0.6.3 → 0.9.3 with a fresh venv, exact pin, lock regenerated, pytest + live smoke before any code changed. Zero API breakage on our surface; the new anti-bot detector turned out to help status validation rather than fight it.
- **Discovery → crawler handoff.** `--input`/`--limit` replaced the shell one-liner; the two-command flow ran clean for Claudy and independently for Cody with no manual step.
- **Chunked delivery.** Seven commit-sized chunks with pytest after each; the Director could stage per chunk.
- **Independent QA execution agent.** Cody reproduced every claim from disk instead of reading the report, and found the one real gap.

## What fought back
- **AC-21 empty input.** "Written every run" was tested for 10 pages and for the blocked-stop path, not for `[]`. The early `return` skipped `write_summary()`, leaving stale evidence. Caught by Cody, not by the Engineer's own tests. Fix: 4 lines + 1 regression test.
- **Grep-shaped ACs vs honest docs.** AC-41's "0 hits" collided with the CHANGELOG line recording the deletion; AC-45 counted four refs where three existed; AC-10's "run from /tmp" needs `PYTHONPATH` because the package is not installed. All adjudicated PASS WITH NOTE; the intent held, the literal check did not.
- **Report naming.** The CP2 template slug `stage2-prep` misnamed the completion report; renamed to `stage2-complete`.
- **Plan Mode compression.** The AC-21 mission specified the exact behavior; Claudy treated it as the approved plan rather than stopping for a separate approval. Worked here; worth a doctrine line on when a fully specified mission counts as approval.

## Numbers
crawl4ai 0.6.3 → 0.9.3 · tests 6 → 14 · smoke 10/10 all 200 (three independent runs) · pause 2–5 s · UA Chrome/140 with non-empty `sec-ch-ua` · 1 QA defect, 1 rework cycle, 0 open blockers.

## Carry into bim001
- Enumerate degenerate inputs (empty / missing / malformed) for every "always" AC before declaring green.
- Keep the two-command flow and `run_summary.json` as the contract bim001 builds raw-HTML capture on.
- `wait_for_images=True` and `fit_markdown` (F1) remain deferred decisions.
