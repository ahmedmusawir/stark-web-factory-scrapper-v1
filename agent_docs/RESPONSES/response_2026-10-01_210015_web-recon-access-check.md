1. **What worked and what stopped:** The diagnostic coordinator passed **22 localhost checks**. Live step 1 then returned **HTTP 429** to curl at `/sitemap_index.xml`. The shared stop was triggered immediately after retaining that response; no later live step ran. **Diagnostic complete; access investigation remains BLOCKED.**

2. **Actual external request count: ONE.** One curl GET, one HTTP response. Zero external Python requests, redirect hops, retries, REST requests, browser requests, child-sitemap requests or crawler runs. The local verification made 26 loopback requests, counted separately.

3. **What the result supports / what remains unknown:** Curl 8.5.0 with the project USER_AGENT was refused on this URL from this execution environment on October 1. It does not establish today's Python behavior, a curl/Python difference, the refusal's cause, site-wide availability, or readiness for a full crawl. The requested paired comparison could not proceed because the first response invoked the stop rule.

4. **Exact contract discrepancies:** **None established from a current page/post sample, because neither endpoint was reached.** This is unconfirmed, not a clean contract pass. Presence, missing/null distinctions, types, Yoast payload and content emptiness remain unknown for both samples.

5. **Uncommitted paths:** This mission adds `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/access-check/2026-10-01_145405Z/**`, this report and its sibling ZIP. The 11 pre-existing BIM001 report moves and intake Markdown remain untouched. **Preservation discrepancy:** the pre-existing intake ZIP was present and hashed at startup but is now absent; this mission issued no deletion or write to it. Other checked pre-existing paths retained their starting state. Exact paths and evidence follow.

**CODY — bounded access diagnostic: DONE / BLOCKED**

Engineer: Cody · Architect: JARVIS · Director: Tony. Report written 2026-10-01T21:00:15+06:00 (Asia/Dhaka). This mission is complete and stopped; P0, P1 and the ABM build remain unexecuted.

**Repository and authority**

- Repo: `/home/moose/python/stark-web-factory-scrapper-v1`.
- Branch at start and preservation check: `wf-scrapper-abm`.
- HEAD at start and preservation check: `3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f` — exact intake match.
- Mission start: `2026-10-01T14:53:41Z`; total deadline: `2026-10-01T15:23:41Z`. Live stage: `2026-10-01T14:58:16.225377Z` through `14:58:19.050237Z`, approximately 2.825 seconds. Report and packaging completed within the 30-minute mission budget.
- Current Director diagnostic instruction governs over historical role assignments and resume/build commands. Read: intake, root and ABM CLAUDE.md, RECOVERY.md, P0 and recovery reports, Contracts §2.5, and the project USER_AGENT definition. No AGENTS.md was found in the repo instruction search; ancestor instruction search was performed during the immediately preceding intake.
- No product, test-suite, dependency or frozen-contract edits; no installs; no Git mutations. The only executed checks were the new diagnostic's localhost checks. No historical recovery script was run.

Evidence base **E** = `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/access-check/2026-10-01_145405Z/`. Paths beginning E below refer to this new, exclusively created directory. All timestamps in request evidence are UTC. Reports and the ZIP preserve repo-relative paths.

**The single live request**

| Item | Recorded value |
|---|---|
| Step / client | Step 1 / curl 8.5.0, libcurl 8.5.0, OpenSSL 3.0.13 |
| Method and exact URL | `GET https://cyberizegroup.com/sitemap_index.xml` |
| UTC start | `2026-10-01T14:58:16.225590+00:00` |
| UTC end | `2026-10-01T14:58:19.049084+00:00` |
| Elapsed | `2.823493` seconds |
| Preceding pacing gap | Not applicable: first live request; no prior response in this live coordinator |
| Status | **429** |
| Content-Type | `text/html` |
| Location | Absent |
| Retry-After | Absent; no retry made |
| X-ac | `18.sin _atomic_bur MISS` |
| X-WP-Total / X-WP-TotalPages | Both absent |
| Body size | 1,168 bytes; complete, below the 2 MiB ceiling |
| Body SHA-256 | `21200fdcf2fb9fb7a01ec311ca3b49dc918347f75cf3c001f5ecd70f69e121c0` |
| TLS verification | Enabled |
| Automatic redirects / retries | Disabled / disabled |
| Curl process exit | 0: transfer completed, **not** HTTP/application success |
| Required XML check | **FAIL: HTTP_429_refusal.** Response rejected before XML parsing; it was not accepted as sitemap evidence. |

UTC start/end and elapsed bracket the client subprocess/transfer, including launch and completion handling. The shared pacing clock starts after subprocess/response completion, so it is conservative. No live inter-request pacing gap was exercised because there was no second live request.

Exact USER_AGENT used (same constant is used by both clients in local checks):

`Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36`

Primary evidence: E`live/01_step1_curl/metadata.json`, E`live/events.jsonl`, E`live/STOP.json`, E`live-result.json`. Raw response bytes are retained **locally only** at E`live/01_step1_curl/response.body`; no body content is printed in this report or included in the ZIP.

**Sequence disposition**

| Step | Intended action | Result |
|---|---|---|
| 1 | Curl `/sitemap_index.xml`, require 200 + sitemap XML | 429 → global sticky stop |
| 2 | Python identical URL / USER_AGENT | NOT RUN: preceding step failed |
| 3 | Python `/sitemap.xml`, no automatic redirects | NOT RUN |
| 4 | Separately counted permitted redirect hop, only if step 3 qualifies | NOT RUN; no redirect encountered |
| 5 | Python pages collection, `per_page=1` | NOT RUN |
| 6 | Python posts collection, `per_page=1` | NOT RUN |

The `/wp-json/` root was never requested. No alternate client was tried after refusal. The one external HTTP response confirms one actual HTTP request; request count is not inferred merely from a failed connection attempt.

**Local verification — current evidence, not historical product tests**

Installed versions recorded before live traffic: venv Python **3.12.3**, requests **2.32.3**, curl **8.5.0**. E`versions.json` records full version strings and the USER_AGENT. No installation or package change was performed.

The first sandboxed fixture startup was blocked while creating a localhost socket, before any check or request could run. This setup limitation is retained in E`local-setup-blocked.json`; its empty `local/` directory was retained. The authorized localhost-only verification then ran with the required execution permission. All behavior checks below passed before the single live invocation; E`local-check-results.json` pins the SHA-256 of the exact coordinator used live.

| # | Local check | Result |
|---|---|---|
| 1 | 15-second response-completion pacing across curl and Python | PASS |
| 2 | sticky 429 stops both clients: curl | PASS |
| 3 | no automatic redirect follow: curl | PASS |
| 4 | unexpected redirect stops without external hop: curl | PASS |
| 5 | streaming 2 MiB ceiling: curl | PASS |
| 6 | hard wall timeout: curl | PASS |
| 7 | sticky 429 stops both clients: python | PASS |
| 8 | no automatic redirect follow: python | PASS |
| 9 | unexpected redirect stops without external hop: python | PASS |
| 10 | streaming 2 MiB ceiling: python | PASS |
| 11 | hard wall timeout: python | PASS |
| 12 | six-request shared budget refuses seventh dispatch | PASS |
| 13 | stage and total mission deadlines before dispatch | PASS |
| 14 | deadline rechecked after pacing wait | PASS |
| 15 | stop condition /forbid | PASS |
| 16 | stop condition /challenge | PASS |
| 17 | stop condition /bad | PASS |
| 18 | empty REST collection is a data gap | PASS |
| 19 | external destinations rejected before subprocess dispatch | PASS |
| 20 | exclusive evidence directory; existing bytes unchanged | PASS |
| 21 | cookies/auth not sent; sensitive response headers not persisted | PASS |
| 22 | concurrent callers serialized to one in-flight request | PASS |

Local verification used real curl and requests transports against a temporary `127.0.0.1` fixture server, with explicit local URL allowlists and no external DNS/HTTP dependency. External-looking fixture strings were payload/redirect test data, never fetched. The shared pacing check used the actual **15-second** interval after a delayed response. Timeout checks used a shortened local transfer cap; live policy fixes it at 30 seconds. Body-cap checks used the actual 2 MiB ceiling. Other local cases used reduced pacing to exercise control flow without unnecessary waits. These checks establish the specified diagnostic behavior under their fixtures; they do not prove live browser/crawler behavior or contract readiness.

Evidence: E`local-check-results.json`, E`local-server-log.json`, E`local-*/**/metadata.json`, E`local-*/**/events.jsonl`, and E`local_checks.py`. All local raw fixture bodies are also excluded from the ZIP.

**Coordinator safeguards**

The new E`coordinator.py` serializes both clients through one lock and one pacing clock. It reserves transfer time against stage and mission deadlines before dispatch and rechecks after waits; the live stage is capped at 600 seconds, the mission at the fixed 30-minute deadline, the request budget at six, and each transfer at 30 seconds. A parent process monitors streamed output and terminates the client process group on deadline/body-limit failure. Evidence directories and files use exclusive creation, and the live-start marker prevents a second live invocation in the same evidence directory.

Curl uses its normal verified TLS transport, disables curl configuration loading, proxies, retries and automatic redirects. Requests uses verified TLS with environment proxy/netrc lookup disabled, no retry adapter, no automatic redirects, and a fresh session for each request. Neither client sends cookies or credentials. These are request-local settings; no machine/security configuration was changed. Only the six named response header fields are retained. Bodies are never written to terminal output.

**Contracts §2.5: exact evidence boundary**

Authority: `agent_docs/ACTION/wf-scrapper-abm/ABM_CONTRACTS.md:155–168`. Both desired page/post samples are absent because live work stopped at step 1. **A missing sample is not evidence that a field is missing or null.** The comparison artifact E`contract-comparison.json` is an empty object because there were no eligible successful collections.

| Contract field | Page sample | Post sample | Presence / null / type finding |
|---|---|---|---|
| `id` | Not sampled | Not sampled | Unknown |
| `type` | Not sampled | Not sampled | Unknown |
| `link` | Not sampled | Not sampled | Unknown |
| `slug` | Not sampled | Not sampled | Unknown |
| `status` | Not sampled | Not sampled | Unknown |
| `date` | Not sampled | Not sampled | Unknown |
| `modified` | Not sampled | Not sampled | Unknown |
| `title.rendered` | Not sampled | Not sampled | Unknown |
| `excerpt.rendered` | Not sampled | Not sampled | Unknown |
| `content.rendered` | Not sampled | Not sampled | Unknown |
| `author` | Not sampled | Not sampled | Unknown |
| `featured_media` | Not sampled | Not sampled | Unknown |
| `categories` | Not sampled | Not sampled | Unknown |
| `tags` | Not sampled | Not sampled | Unknown |
| `yoast_head_json` | Not sampled | Not sampled | Unknown |
| `yoast_head` | Not sampled | Not sampled | Unknown |

Yoast nested fields (`title`, `description`, `robots`, `canonical`, `og_*`, `twitter_*`, `schema`, `article_*`) are unobserved. `content.rendered` emptiness after markup stripping is **not evaluated**, not false. No empty collection was observed either: the collection endpoints were never requested. The helper supports first-object presence/type inspection and separately distinguishes missing versus present-null, but that path did not execute on live data.

Only `yoast_head_json` object and `yoast_head` string have explicit types in §2.5. For other fields, the helper labels its type expectations as diagnostic expectations rather than inventing a formally declared type contract. No field-name/type erratum can be justified by this live result alone. No sample-level observation is generalized to the whole site.

**Supported conclusion and unknowns**

The current curl request was refused with HTTP 429 and an edge header containing `_atomic_bur`. That header and the refusal alone do not prove a burst-rate cause, source-IP block, TLS fingerprint discrimination, site resource exhaustion, persistence duration, or a site-wide failure. No different source, network, client identity or browser was tested. Historical Python refusals do not fill the missing current Python observation.

**Next move:** JARVIS can use this refusal evidence to propose the next bounded investigation or request site-owner evidence through Tony. Another client request, retry, access-policy change or recovery/build action requires a new instruction. This mission performs no such action and does not certify the site ready for a full crawl.

**Working-tree changes and preservation**

Initial status, captured before diagnostic files were created:

```text
 D agent_docs/RESPONSES/BIM001_GATE_Q_RECORD_2026-09-07.md
 D agent_docs/RESPONSES/BIM001_chunk1_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_chunk2_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_chunk3_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_chunk4_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_chunk5_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_chunk6_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_closeout_2026-09-07.md
 D agent_docs/RESPONSES/BIM001_complete_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_handoff-read_2026-09-06.md
 D agent_docs/RESPONSES/BIM001_plan_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_GATE_Q_RECORD_2026-09-07.md
?? agent_docs/RESPONSES/OLD/BIM001_chunk1_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_chunk2_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_chunk3_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_chunk4_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_chunk5_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_chunk6_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_closeout_2026-09-07.md
?? agent_docs/RESPONSES/OLD/BIM001_complete_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_handoff-read_2026-09-06.md
?? agent_docs/RESPONSES/OLD/BIM001_plan_2026-09-06.md
?? agent_docs/RESPONSES/response_2026-10-01_204419_web-recon-architect-intake.md
?? agent_docs/RESPONSES/response_2026-10-01_204419_web-recon-architect-intake.zip
```

Those 11 tracked deletions paired with 11 untracked `RESPONSES/OLD/` destinations were already present at entry. This diagnostic neither performed nor reversed them. The intake Markdown's bytes are unchanged.

Preservation check examined **1088** previously recorded file states/hashes (tracked files except `.env*`, plus response artifacts). **1,087 retained their original state.** The single discrepancy is:

- Path: `agent_docs/RESPONSES/response_2026-10-01_204419_web-recon-architect-intake.zip`.
- At startup: present, SHA-256 `2daec3d59be7e3f0ce09d416e2751b397f18f52e22e7952c0a7908efc10afb67`.
- At final check: absent from that path; no matching intake ZIP found under `agent_docs/RESPONSES/`.
- This mission's commands contain no removal or rewrite of that ZIP. The actor/reason for its disappearance is unknown. It was not recreated or restored over the current workspace. The preservation result is explicitly **not an all-files-unchanged pass**.

Preservation evidence: E`preflight.json`, E`preservation-check.json`; current paths captured in E`working-tree-status.txt` before writing these two final deliverables. Newly created uncommitted paths:

- `agent_docs/ACTION/wf-scrapper-abm/EVIDENCE/access-check/2026-10-01_145405Z/**` — helper, local checks/results, metadata, logs and local-only bodies.
- `agent_docs/RESPONSES/response_2026-10-01_210015_web-recon-access-check.md`.
- `agent_docs/RESPONSES/response_2026-10-01_210015_web-recon-access-check.zip`.

**Deliverables and retention**

The sibling ZIP contains this report, coordinator, local-check helper/results, version/preflight/preservation records, sanitized request metadata and logs. All member paths are repo-relative. Raw bodies, `.env*`, credentials, real cookies, unselected response headers, dependencies and earlier campaign evidence are excluded. The test helper includes only its synthetic localhost cookie fixture; no real cookie value was recorded or shared. Body references in metadata intentionally point to local-only files.

**Completion:** 22 local checks passed; one external request made; first 429 stopped the mission; report and ZIP delivered. No P0, P1 or ABM build resumed.
