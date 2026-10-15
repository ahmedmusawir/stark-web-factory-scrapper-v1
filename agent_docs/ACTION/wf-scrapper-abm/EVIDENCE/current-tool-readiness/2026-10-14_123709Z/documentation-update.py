from pathlib import Path
import json,re
from datetime import datetime,timezone

c=json.loads(Path('/tmp/web-recon-readiness-config.json').read_bytes());root=Path(c['root']);module=root/'agent_docs/ACTION/wf-scrapper-abm';e=Path(c['evidence'])
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:f.write(x if isinstance(x,str) else json.dumps(x,indent=2)+'\n')
notes={
1:('Retained','Lock/direct-dependency distinction, environment identity and reproducible setup; clean-install QA remains pending.'),
2:('Mixed','Validate explicit plans/URLs/IDs and actionable CLI errors. Old --project flags, exact three-line errors and test filenames belong to the retired CLI.'),
3:('Mixed','Separable stages remain: decide, collect/resume/add/refresh, then offline agent skill. The default one-command Capture+Prepare build is retired.'),
4:('Retained','New review/collection/package paths, confined saved references, no silent overwrite and preservation of prior attempts; arbitrary user-supplied output path is explicit, not old project-slug routing.'),
5:('Mixed','Explicit planned scope, sequential default5s pacing, refusals/challenges and no automatic retries remain. Custom pre-dispatch per-hop scope/five-hop/CDP cancellation machinery is retired; redirects/resources are extra browser traffic.'),
6:('Mixed','Failures, interruption, progress and cleanup must remain visible. Current resume reuses a collection and immutable attempts; old no-resume/always-new-run rule and old exit mapping are retired.'),
7:('Mixed','Bounded explicit sitemap/default discovery, stable URL IDs, dedup and provenance remain. Old tracking-query stripping/routes.json identity binding is not the DECIDE normalize rule.'),
8:('Mixed','Each approved checklist item is accounted for; HTML and REST are separately selected. Mandatory per-route REST mapping/raw-v2 pages[] accounting belongs to the old whole-site design.'),
9:('Retained','Rendered Crawl4AI HTML is saved as UTF-8 at the declared boundary with hashes, without pretending it is original compressed wire bytes.'),
10:('Retained','Do not call refusals/challenge documents or empty/failed capture successful content; detector is heuristic, not comprehensive access certification.'),
11:('Mixed','Complete selected REST entity bytes, all returned fields and hashes survive; malformed mandatory identities fail. Old object derivatives/route mapping/mandatory SEO inventory are retired. No production four-field filter is injected.'),
12:('Mixed','Only explicitly approved pagination follows advertised pages within max_pages; short-page anomalies/duplicates/count gaps stay explicit. Mandatory REST mapping of every HTML route is retired.'),
13:('Mixed','Save recon source evidence/types/counts and collection status. Whole-site robots/every-sitemap/six-collection rest/index layout is retired; no automatic collection expansion.'),
14:('Retained','Present-empty REST content remains empty and cannot erase substantive HTML. Dated complementary observations retained; no Thrive/plugin cause asserted.'),
15:('Retired design','No automatic media inventory/HEAD sweep/download. Saved page image references and explicit gaps remain available; this does not close historical media coverage defects.'),
16:('Mixed','Checklist/result/attempt records, runtime, planned timing and separate cleanup explain collection. Old manifest/stage-log/native-ID and exact supervisor counters are retired bindings.'),
17:('Mixed','Pending/completed/failed items and explicit partial/stop reasons preserve losses. Old raw-v2 absence enums and requirement to map every site route are retired.'),
18:('Retired design','Authored screenshot stream/manifest is not a current feature requirement. Agent-authored brief/interpretation is still distinguished from captured facts.'),
19:('Retained','Prepare is offline and source collections remain unchanged; new derived package construction is allowed.'),
20:('Mixed','Invalid completed references/hashes refuse preparation before output. Old F-10/raw-v2 version checks, pack.json and exit3 are retired; current helper refusal is exit2.'),
21:('Retained','Prepared page IDs, URLs, capture dates, raw/metadata/derived hashes and CSS locators trace to saved evidence; authoring/context sources are indexed.'),
22:('Retained','Separate observed source facts, agent interpretation and unknown/absent information; a helper hint is not a final reviewed classification.'),
23:('Mixed','Numbered JSON/Markdown candidate inventory and prepared selected sample remain. Mandatory whole-site site_map/content_inventory snapshots are retired.'),
24:('Mixed','Expose observed cross-source differences without fabricating a winner. Mandatory disagreements.json/F-06 three-conflict schema belongs to the retired pack.'),
25:('Mixed','Preserve returned SEO fields in raw selected REST and avoid invention. Automatic full derived SEO inventory/Yoast certification is outside current demonstrated skill scope.'),
26:('Retained','Forms/embeds are observed markup only; agent source inspection records unavailable child content, no booking/form testing or automatic iframe fetch. Exact old F-07 output schema is retired.'),
27:('Mixed','Observed facts and authored design implications must be distinguishable. Agent architect brief may state labeled implications; old automatic design JSON/rule schema is retired.'),
28:('Retired design','Automatic media classes/rules and full media_classification.json are retired; no authority to delete/promote source data.'),
29:('Mixed','Missing/failed capture and useful-content gaps remain explicit in checklist/GAPS_AND_REQUESTS. Old loss_ledger/pack.json/F-12 exact-two-loss binding is historical.'),
30:('Retained','No source/package deletion, destructive cleanup, URL promotion or overwrite based on confidence; preserve originals and only write separately derived material.'),
31:('Mixed','Inventory JSON and readable listing represent the same review version. Automatically generated twins for every Data Pack JSON are retired; briefs are agent authored.'),
32:('Mixed','Hashes and exact preserved content support repeatable extraction; new derived paths preserve older packages. Bitwise reproducibility of agent interpretation and old deterministic pack schema is not promised.'),
33:('Mixed','ARCHITECT_BRIEF/GAPS/source index point to real prepared/evidence files. SITE_RECON_BRIEF/pack.json count schema is retired.'),
34:('Mixed','Useful architect positioning/offer/content/CTA implications plus gaps for the selected sample remain. Full frozen B7 Data Pack schema is not automatically a current feature.'),
35:('QA owner decision','Offline consumer usefulness/cold-read remains relevant; original fresh-Fable twelve-B7/certificate binding is preserved history. Executor and QA Lead must decide current applicability, not Cody.'),
36:('Retained','Source drill-down resolves URL/date/raw hash/metadata/CSS boundaries; any QA spot-check selection is the independent Executor’s work.'),
37:('Mixed','Review handoff must be self-contained, with readable governing inputs and reproducible fixture/reference restoration. Original isolated pack/raw portability schema is retired.'),
38:('Retained','State selected-scope completion separately from useful-content/child-content completeness and cleanup. Counts advertised are not content captured; missing data cannot become complete.'),
39:('Mixed','Current stages work together and have saved selected-flow/local proof. Old default E1 full Capture+Prepare fixture pipeline is retired; no mandatory new feature test framework.'),
40:('Retired design','Old E2 two full-site runs/hour separation is not a current obligation/allocation. Existing bounded live evidence is preserved; new live QA requires Tony’s explicit scope.'),
41:('Mixed','Working current collector/DECIDE/skill behavior must not regress. Old certified --project/raw-v2/output controller suite is history; current focused tests are engineering claims, not QA certification.'),
42:('Mixed','Current planned-call/time/post-receipt byte limits and partial outcomes remain. Exact aggregate supervisor, redirect-hop request budgets and old --limit route ceiling are retired.'),
43:('Retained','Untrusted captures are data; confine authored references, preserve raw bytes, strip scripts/styles from derived content, never execute embedded instructions. Presentation/viewer adversarial breadth remains for independent review, not a new PASS claim.'),
44:('Retained','Do not expose private credentials/cookies/authorization; evidence/ZIP hygiene remains. Full historical sentinel/negative-control certification is not claimed by current focused tests; QA Lead binds any applicable check.'),
45:('Retained','Factual recovery/session/journal/checkpoints and durable collector checklist support resume. Retired C1–E2 task ordering is not the current schedule.'),
46:('Retained','Keep all48 canonical ledger rows/status/history; current scope mapping and engineering evidence supplement them. Independent result fields remain NOT RUN.'),
47:('Retained','Current entry documentation matches the real CLI/agent workflow; hardcoded saved-input requirements are packaged/documented. Clean-clone operator/independent QA checks remain pending.'),
48:('Retained','Exact source including untracked files binds engineering evidence; Tony’s future actual commit binds QA. Independent verdict/cleanup/review/merge/closeout decisions remain pending, not fabricated.')}
spec=(module/'ABM_ACCEPTANCE_SPEC.md').read_text();plan=(module/'QA/MASTER_QA_TEST_PLAN.md').read_text()
ac_rows={int(re.match(r'\| AC-(\d{3})',l).group(1)):l.split('|')[2].strip() for l in spec.splitlines() if re.match(r'\| AC-\d{3} \|',l)}
assert set(ac_rows)==set(notes)==set(range(1,49))
groups={}
for l in plan.splitlines():
 if re.match(r'\| T-\d{2} ',l):
  ident=re.search(r'T-\d{2}',l).group();groups[ident]=re.findall(r'AC-\d{3}',l.split('|')[2])
assert len(groups)==24
scope='''# Current tool operating scope — DECIDE → COLLECT → PREPARE

2026-10-14 · engineering readiness binding. Authority: Tony’s October7 simplification and subsequent DECIDE/COLLECT/Prepare approvals; JARVIS-approved Shot1 and Tony’s Shot2 readiness instruction. This records current scope, not an independent QA plan, certificate, final closeout or adoption of the interim playbook.

## Practical definition of done

- DECIDE uses an explicitly chosen sitemap or bounded default-link mode; it saves stable IDs, numbered JSON/Markdown review, source locators/hashes, metadata unknowns and coverage limits. Public types use unfiltered `wp/v2/types`; collection metadata uses projection. Recon does not execute full collection.
- Tony’s HTML/REST inclusions/exclusions bind to the exact saved inventory version; unknown rows/IDs fail. Unmentioned rows remain undecided. One selected REST item never grants whole-collection permission. Export is offline and produces the existing explicit collector plan.
- COLLECT runs selected HTML and REST reads sequentially through installed Crawl4AI. Default pacing is five seconds after a planned call completes; ordinary redirects/background resources add traffic. No automatic retry/fallback. First access refusal/rate limit/challenge stops later planned calls and retains progress.
- A successful result is saved and hashed before checklist completion. Resume skips only valid completed results; interrupted/failed/missing outputs remain eligible for explicit invocation. Add queues exact new URLs; refresh is explicit and preserves previous attempts. Opt-in REST pagination follows approved page bounds and reports short pages, duplicates and count discrepancies honestly.
- PREPARE is an offline agent-assisted skill, not one automatic pack builder. Validate saved references/hashes, inspect raw boundaries/classification, keep useful headings/paragraphs/lists/links/CTAs, separate navigation/footer, and author source-linked ARCHITECT_BRIEF/GAPS_AND_REQUESTS with facts distinguished from interpretation. Unknown embeds/images/hidden content remain explicit gaps.
- Engineering readiness requires unchanged source identity, combined focused verification, read-only accepted-package content checks and reproducible fixtures. Independent QA is separate and remains NOT RUN until a committed candidate, Executor Q1 and QA Lead plan decision precede Q2.

## Active entry points and transport

| Stage | Current entry | Governing detail |
|---|---|---|
| DECIDE | `venv/bin/python -m recon_pipeline.decide` (`recon`, `import`, `list`, `select`, `export`) | [DECIDE.md](DECIDE.md) |
| COLLECT | `venv/bin/python -m recon_pipeline` (`collect`, `resume`, `add`, `refresh`) | [COLLECTOR_SIMPLIFICATION.md](COLLECTOR_SIMPLIFICATION.md) |
| PREPARE | Agent follows [SKILL.md](../../SKILLS/web-recon-prepare/SKILL.md); helper `venv/bin/python agent_docs/SKILLS/web-recon-prepare/scripts/prepare_saved.py --collection SAVED --out NEW` | Helper performs validation/extraction only; agent completes reviewed brief/gaps/index |
| Readiness / later QA | [RECOVERY](../../../RECOVERY.md), [QAM](QAM/README.md) | Cody Engineer; SOL QA Lead; separate Executor session pending; Tony alone controls Git |

HTML uses rendered Crawl4AI UTF-8; selected REST uses ordinary Chromium navigation and native `after_goto Response.body()` decoded entity bytes. No requests/curl substitution or custom CDP BrowserSession on this active path. Existing USER_AGENT/cache/image wait/90-second navigation/three-second HTML delay are retained. REST has30-second outer ceiling. Response cap10MiB is checked after body receipt, not a wire/memory streaming guarantee. Work deadline includes setup/pacing; ordinary cleanup has a separate10-second timeout. Persistence budget is the simple collector’s estimate, not the old exact supervisor bound. No arbitrary new live authorization arises here.

## Growth Call: required agent review, unchanged helper

The helper currently mistakes `.tcb-post-content #tve_editor` for proof of an article. Growth Call contains an embedded booking document with no saved native main copy/forms/labels. The accepted reviewed output corrects its derived type and documents the missing child content; initial helper output stays preserved. Mandatory source inspection handles this known limitation. No helper repair, automatic iframe collection or booking/form testing is authorized by Shot2. An empty helper extraction is not a finished architect package.

## Historical acceptance crosswalk — applicability, not results

Original [AC-001–AC-048](ABM_ACCEPTANCE_SPEC.md) and [T-01–T-24](QA/MASTER_QA_TEST_PLAN.md) remain intact with original literal checks/history. [Ledger](ABM_LEDGER.md) is not overwritten. The table identifies the current principle and any retired implementation binding. “Retired design” means no automatic current build/live obligation; it does not mean historical PASS, waived, resolved or certified. Mixed rows retain only the expressly described current behavior; any QA coverage/criterion/closing disposition is for the independent Executor and QA Lead, with JARVIS/Tony scope authority. This is engineering handoff context, not Cody-authored Q1/Q2 executable instructions.

| Original ID / title | Applicability | Current principle versus retired binding | Historical QA group |
|---|---|---|---|
'''
rows=[]
for n in range(1,49):
 ident=f'AC-{n:03d}';kind,note=notes[n];test_ids=[t for t,acs in groups.items() if ident in acs]
 rows.append({'id':ident,'title':ac_rows[n],'applicability':kind,'current_and_retired_binding':note,'historical_qa_groups':test_ids,'qa':'NOT RUN','historical_result_changed':False})
 scope+=f'| {ident} — {ac_rows[n]} | {kind} | {note} | {", ".join(test_ids)} |\n'
scope+='''
## Findings and independent handoff boundary

Preserve OPEN historical media1661/1753 discrepancy, two unconfirmed late shutdown aborts, stopped-run homepage bootstrap/route mismatch and supervisor-counter gap. They belong to the retained retired-path evidence and are not current controller repair tasks or retrospective passes. Broader optional SEO/media/custom-type coverage, image/deferred completeness, native crash breadth and clean-install/operator checks remain limited/unverified; absence is not success. Current review packages preserve separately dated REST-empty/HTML-present observations and advertised versus sampled counts.

After engineering handoff Tony chooses the candidate files/commit and QA branch. A separate Executor verifies the committed specimen and environment, performs Q1 recon/planning, and proposes the candidate-bound plan. SOL approves/amends before Q2. No current QA plan approval or certificate is issued here. Cleanup/destructive actions remain Tony’s; closeout and final playbook adoption are deferred. Existing old review/certification obligations stay recorded for owner disposition rather than silently waived.
'''
save(module/'CURRENT_TOOL_SCOPE.md',scope)
save(e/'acceptance-crosswalk.json',{'kind':'Engineering scope mapping, not independent QA test plan or result','authority':'JARVIS-approved Shot1; Tony Shot2','rows':rows,'historical_groups':groups,'original_ids_preserved':True,'qa':'NOT RUN'})

prefixes={
'CLAUDE.md':'''## Active Web Recon tool / Shot2 readiness — 2026-10-14

Read [current-tool scope](agent_docs/ACTION/wf-scrapper-abm/CURRENT_TOOL_SCOPE.md) and [RECOVERY](RECOVERY.md) first. DECIDE → explicit resumable COLLECT → offline agent-assisted PREPARE is the active direction. Tony authorizes this bounded engineering-readiness pass: documentation, retained fixture checks, three focused local modules and saved-package verification. No further planning approval is needed for that scope. No product/helper repair, external collection, dependencies/Git, independent QA or final playbook/closeout. Cody Engineer; JARVIS Architect; Tony Director. SOL remains QA Lead, separate Executor binding pending. Growth classification is handled by required agent source review, not a claimed helper fix. The dated older commands/authorizations below are preserved history and do not restart that campaign.

''',
'README.md':'''# Active tool — DECIDE → COLLECT → PREPARE

Current engineering readiness and historical acceptance mapping: [CURRENT_TOOL_SCOPE.md](agent_docs/ACTION/wf-scrapper-abm/CURRENT_TOOL_SCOPE.md). Start with [RECOVERY](RECOVERY.md) for the latest results and candidate handoff.

- **DECIDE:** `venv/bin/python -m recon_pipeline.decide` discovers bounded candidates, saves immutable numbered review and exact human HTML/REST choices, then exports a plan. [Usage](agent_docs/ACTION/wf-scrapper-abm/DECIDE.md).
- **COLLECT:** `venv/bin/python -m recon_pipeline collect --plan PLAN.json --collection NEW_DIR --gap 5 --max-requests N --max-seconds S --max-bytes B`; `resume --collection DIR` skips hash-valid completed items; `add --collection DIR --plan ADDITIONS.json` queues explicit additions offline; `refresh --collection DIR --id ID` queues replacement while retaining old attempts. Resume/collection require approved target scope/bounds. [Details](agent_docs/ACTION/wf-scrapper-abm/COLLECTOR_SIMPLIFICATION.md).
- **PREPARE:** give the preparation agent a saved collection and [skill](agent_docs/SKILLS/web-recon-prepare/SKILL.md). Its offline helper extracts and validates; the agent inspects raw boundaries, corrects classifications and authors the source-linked brief/gaps. Growth Call’s known preliminary type error remains handled by that review; no automatic iframe capture.

Shot2 uses only local tests/saved evidence. Independent QA NOT RUN. The dated original README sections below preserve earlier tool/campaign/install history; old Capture+Prepare commands/output guarantees are not the current tool. Existing requirements lock/direct pins remain unchanged; clean-install proof remains pending.

''',
}
for filename in ['AGENTS.md','CLAUDE.md']:
 prefixes[f'agent_docs/ACTION/wf-scrapper-abm/{filename}']='''## Current tool / authorized engineering readiness — 2026-10-14

Read [CURRENT_TOOL_SCOPE.md](CURRENT_TOOL_SCOPE.md) and [RECOVERY](../../../RECOVERY.md). Cody is Engineer. JARVIS approved Shot1; Tony authorizes Shot2 documentation, fixture/reference verification and the three focused local modules. Use current DECIDE/explicit COLLECT/offline agent PREPARE, preserve dirty work/history, and keep QA independent. No product/helper repair, external requests, dependencies/Git or final playbook/closeout. Growth preliminary classification is a known agent-reviewed limitation. Current results and handoff are in RECOVERY; the earlier campaign instructions below are historical, not authorization to resume C1–E2/controller work.

'''
for filename in ['ABM_ACCEPTANCE_SPEC.md','ABM_CONTRACTS.md','ABM_BRIEF.md','ABM_BUILD_INSTRUCTIONS.md','ABM_LEDGER.md']:
 prefixes[f'agent_docs/ACTION/wf-scrapper-abm/{filename}']='''## Current-tool scope pointer — 2026-10-14

Active DECIDE → COLLECT → agent-assisted PREPARE is governed by [CURRENT_TOOL_SCOPE.md](CURRENT_TOOL_SCOPE.md), October7 simplification and subsequent approvals. Its crosswalk retains all48 original acceptance IDs/history and separates applicable principles from retired design bindings. Original literal criteria/statuses/authorizations below are preserved; they are not an executable current-tool build/QA plan, new live allocation or historical PASS/waiver. Independent QA NOT RUN; current engineering evidence is linked from [RECOVERY](../../../RECOVERY.md). No original result rows are rewritten by this readiness pass.

'''
for filename in ['DECIDE.md','COLLECTOR_SIMPLIFICATION.md']:
 prefixes[f'agent_docs/ACTION/wf-scrapper-abm/{filename}']='''## Current operating pointer — 2026-10-14

[CURRENT_TOOL_SCOPE.md](CURRENT_TOOL_SCOPE.md) records the complete current DECIDE → COLLECT → offline agent PREPARE scope and readiness/QA boundaries. The behavior/commands below remain useful where marked current; older task-only “Prepare future/not implemented” and proposed live-check statements are dated history, superseded by accepted Prepare v0.1 and subsequent task records. They authorize no new live request. Current WordPress types are unfiltered; individual metadata stays projected. Independent QA NOT RUN. See [RECOVERY](../../../RECOVERY.md).

'''
for filename in ['README.md','MASTER_QA_TEST_PLAN.md']:
 prefixes[f'agent_docs/ACTION/wf-scrapper-abm/QA/{filename}']='''## Current-tool QA readiness pointer — 2026-10-14

Read [current scope/crosswalk](../CURRENT_TOOL_SCOPE.md), [QAM state](../QAM/STATE.md) and [RECOVERY](../../../../RECOVERY.md). Cody’s Shot2 evidence is engineering verification only. This preserved canonical plan retains its24 groups/48 mappings/history; its old controller/pack commands are not the current candidate-bound executable plan. A separate Executor must independently inspect Tony’s actual committed candidate and propose Q1 bindings for current applicable scope; SOL approves/amends before Q2. This pointer is not a QA plan authored or approved by Cody. No independent QA has run; no old criterion/finding is passed/waived/closed. Final closeout/playbook remain deferred.

'''
for filename in ['README.md','MANIFEST.md','STATE.md','EXECUTION_INSTRUCTIONS.md']:
 prefix='''## Active current-tool readiness — 2026-10-14

**ENGINEERING READINESS IN PROGRESS; independent QA NOT RUN.** Current [scope/crosswalk](../CURRENT_TOOL_SCOPE.md) supersedes retired controller/whole-pack executable instructions for this tool, preserving their history/results below. Read [RECOVERY](../../../../RECOVERY.md) for factual current evidence. Old candidate/checkpoint/live-allocation text below is historical, not a current pin or authority to restart.

**Next seats:** Cody completes the factual engineering handoff; Tony alone commits the candidate/creates QA branch. Separate Executor Q1 pins the actual commit, inspects readiness and authors candidate-bound recon/plan. SOL QA Lead approves/amends before Q2. Cody neither authors nor approves that independent plan and cannot certify his work. Session bindings and QA plan identity/approval remain PENDING. No new live allocation, cleanup, final closeout or playbook adoption.

'''
 if filename=='MANIFEST.md':prefix+=f'''Precommit specimen: branch `wf-scrapper-abm`, base HEAD `{c['head']}`, plus exact dirty/untracked source52 `{c['source_sha256']}`. This is not the later implementation commit. The readiness report/checklist and fixture restoration identity will be linked from RECOVERY. Future Executor must independently bind committed source and supplied immutable saved fixtures; any engineering reuse remains SOL’s decision.

'''
 prefixes[f'agent_docs/ACTION/wf-scrapper-abm/QAM/{filename}']=prefix
for path,prefix in prefixes.items():
 p=root/path
 with p.open('rb') as f:old=f.read()
 if not (e/'before'/path).exists():save(e/'before'/path,old.decode())
 p.write_bytes(prefix.encode()+old)
save(e/'documentation-changes.json',{'created':['agent_docs/ACTION/wf-scrapper-abm/CURRENT_TOOL_SCOPE.md'],'prefixed_history_preserved':list(prefixes),'original_ac_rows_preserved':48,'original_qa_groups_preserved':24,'qa_plan_authored_or_approved':False})
print(json.dumps({'doc_prefixes':len(prefixes),'mapping_rows':len(rows),'qa_groups_preserved':len(groups),'product_changes':[],'state':'engineering verification still in progress'},indent=2))
