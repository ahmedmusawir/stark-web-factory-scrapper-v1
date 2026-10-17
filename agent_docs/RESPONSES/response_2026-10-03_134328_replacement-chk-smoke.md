# Replacement CHK smoke — stopped, evidence preserved

**Outcome:** the one authorized replacement attempt exited **2** after **one intentional dispatch**. The bootstrap document returned HTTP200, then Chromium reported **`Fetch.continueRequest: Invalid InterceptionId`**. Collection stopped; no retry was made. CHK is **incomplete**.

**The same-URL classification defect did not recur.** The homepage's same-URL stylesheet was classified as incidental and returned HTTP200. No403/429 or explicit challenge was recorded. This does not establish a cause for the new protocol error or historical429s.

## What was actually obtained

| Area | Recorded outcome |
|---|---|
| Documents | One bootstrap slot used; **zero successful route captures**. Available HTML retained as failed/partial evidence: **402,358 bytes**. |
| Discovery | Failed at bootstrap; no intentional robots/sitemap read. Zero routes means discovery did not run. |
| REST | No read or object obtained. Pages, posts, media, categories, tags and users explicitly skipped by the stop rule. |
| Media | No intentional HEAD; `--no-media-head`. Ordinary rendering resources were separately observed. |
| Raw validation | Existing read-only reader/validator **exit0**: valid partial raw package, zero route outcomes. Raw hashes unchanged by validation. No Prepare pack built. |

Raw run: `outputs/CyberizeGroup/runs/2026-10-03T07-39-21Z/`. Manifest streams: discovery failed, HTML partial, REST/media skipped. Partial bootstrap HTML SHA-256: `bb85dbb190b9379a726e29197f443d9a09478db0b46ff32071cec7209f6fd411`.

## Identity, command and limits

Branch **wf-scrapper-abm**; unchanged base HEAD `3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f`, plus existing dirty/untracked work. All **58 entries** matched the reviewed inventory before launch; before/after inventories match:

`3e629379a1295ca0a76c636ab2dc361ffdb449fdf2bdc9ae10ebc5a43af6e2d5`

Exact command, through the existing bounded recorder:

```text
venv/bin/python -m recon_pipeline --project CyberizeGroup --url https://cyberizegroup.com --limit 10 --skip-prepare --no-media-head --max-operations 120 --max-seconds 1800 --max-bytes 100000000 --max-aggregate-bytes 100000000
```

UTC **2026-10-03 07:39:19.830051–07:39:35.848397**; **16.018 seconds**, including pipeline finalization within the recorded command. Stop reason: `interception_error:Error`.

- Intentional dispatches: **1 /120**, including **zero redirect hops**.
- Document slots: **1 /10**, including bootstrap.
- Time: **16.018 /1,800 seconds**.
- Final raw bytes: **565,073**.
- Aggregate persisted bytes, including recorder/evidence, temporary preservation files and this handoff: **2,743,698 /100,000,000**. External evidence: **2,178,625 /3,000,000** reserved; detailed breakdown in JSON.
- Five-second completion gap remains configured. With only one dispatch, **no inter-operation gap was exercised**. Background resources are not individually paced by that rule.

There were **66 browser request events** and **57 observed HTTP200 response events**. These include incidental/intercepted/in-flight traffic; they are not a claim of66 completed HTTP transfers. No additional probe, REST read, browser diagnostic or test-suite run was made. The final byte total includes temporary preservation files omitted from the original preflight projection; actual retained evidence fits both limits.

## What the failure evidence supports

`stage_log.txt:245` records the root stylesheet as incidental; line249 records its HTTP200. Lines368–369 record the new stop/protocol error. The `control_error` event lacks the failing Fetch/network request ID, so the exact request and underlying cause cannot be established from this log. Adjacent asynchronous events are not sufficient attribution. The small JSON handoff contains the sanitized events and original-log hash; full raw bodies/resource logs remain local.

Read-only validation command:

```text
venv/bin/python -m prepare.reader --raw /home/moose/python/stark-web-factory-scrapper-v1/outputs/CyberizeGroup/runs/2026-10-03T07-39-21Z
```

It returned `VALID RAW: 0 route outcomes`, exit0, with no raw-file changes. This is structural validation of partial evidence, not a successful smoke or independent QA PASS. All **5,136 protected prior evidence/report files** remain unchanged, including the earlier failed smoke. Product/test/dependency files remain at the reviewed identity. No Git mutation, cleanup, installation or deployment occurred.

## Next move and Prepare hold

JARVIS reviews the new interception failure and missing request attribution. **This single replacement allocation is consumed; no retry or further live allocation is authorized here.** Campaign journal, engineering log, ledger and recovery record the stopped attempt. Independent QA remains **NOT RUN**.

**Prepare remains ON HOLD.** Tony's intended stage is a **skill inside this repository**, followed by Cody/Claudy/Opy using the documented Ditto lessons to produce the Web Architect's data package. Python helpers support parsing and validation. The existing fully programmed Prepare plan requires an ABM amendment. Do not resume P1–P6, E1 or E2 under the old instructions.

## Handoff files

- **Smoke report:** [response_2026-10-03_134328_replacement-chk-smoke.md](response_2026-10-03_134328_replacement-chk-smoke.md)

- **Small JSON handoff — exact results, evidence excerpt and hashes:** [response_2026-10-03_134328_replacement-chk-smoke_handoff.json](response_2026-10-03_134328_replacement-chk-smoke_handoff.json)

- **Current checkpoint:** [RECOVERY.md](../../RECOVERY.md)

Evidence folder: `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/chk-replacement/2026-10-03_073838Z`. Raw HTML and unsanitized resource logs are kept locally; no ZIP created.

**STOPPED — CHK INCOMPLETE; PREPARE ON HOLD; INDEPENDENT QA NOT RUN.**
