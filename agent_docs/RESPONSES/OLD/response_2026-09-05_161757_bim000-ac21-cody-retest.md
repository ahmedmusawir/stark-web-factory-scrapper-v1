# BIM-000 AC-21 Cody Retest

Date: 2026-09-05. Independent verification of the empty-input repair only; no Gate Q verdict or AC-54 grading.

- **Specimen - PASS.** Branch `qa/web-factory-p1-bim000`; HEAD exactly `dcfb1ea225da41fef3192fa78299ec20362cf8a7`; working tree clean before execution.
- **Repair scope - PASS.** Compared against `9d40ca5a9303d0a93074bf1c8470ad877409dec8`. The only application change is inside `main()`'s empty-input branch: call the existing summary writer with an empty page list and current timestamps, then return. The non-empty crawl path is unchanged. Other changes are one regression test and PRE-Q/rework/session/recovery evidence.
- **Independent AC-21 probe - PASS.** In a separate Python process, created valid `empty.json` containing `[]` and pre-seeded a temporary `outputs/run_summary.json` with a `STALE-CODY-RETEST` page and a 1999 timestamp. Invoked the real `crawler.main()` with `--input`, redirecting only summary/page output paths to the temporary directory. Real argument parsing, input loading and summary writing ran unchanged. A Python call-profile guard monitored `run`, `crawl_all` and `crawl_page`: zero calls occurred. Process exited 0; no page directory was created.
- **Replacement evidence - PASS.** Read and parsed the resulting file; asserted the exact required key set, `pages == []`, no stale marker or timestamp, timestamps within the probe interval, installed Crawl4AI version equality, and pause range `[2, 5]`. Result:

```json
{
  "started_at": "2026-09-05T10:17:57+00:00",
  "finished_at": "2026-09-05T10:17:57+00:00",
  "crawl4ai_version": "0.9.3",
  "pause_range_s": [2, 5],
  "pages": []
}
```

- **Full regression - PASS.** `venv/bin/pytest -q` -> `14 passed in 2.57s` (exit 0).
- **Drift - PASS.** No unexpected implementation drift or unrelated Phase 1 features. Cody made no product fix, commit, merge or branch change. Only this retest report was added; probe files were temporary. No live crawl rerun was needed.
- **Blockers:** None for this retest. The original empty-input/stale-summary failure is closed. Prior PRE-Q process observations, including AC-52, remain for Tony/SOL; this retest does not regrade them.

**READY FOR SOL VERDICT**
