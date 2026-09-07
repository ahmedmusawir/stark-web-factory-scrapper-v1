# DOCTRINE JOURNAL — Stark Web Factory Phase 1
## Lessons owed to the App Factory doc set

> **Purpose:** running log of doctrine gains discovered while running Web Factory Phase 1. Appended as we go. At Phase 1 close this journal is the input to a `factory-docs-update` run: Claudy reads it, sweeps the full doc set, pinpoints which docs change and how, pushes a branch. Director PRs and merges. Nobody touches main.
> **Owner:** Fable (writes) · SOL (reviews at close) · Director (rules) · Claudy (executes the doc sweep)
> **Started:** 2026-09-05 · **Version:** 0.2 · **Status:** OPEN
> **v0.2 (2026-09-05):** J-04 and J-08 corrected; J-11 to J-16 added from the bim000 QA ruling set; Parking Lot revised; §Contradictions added.

Each entry: what we learned · where it came from · which doc(s) it likely touches · ruling status.

---

## J-01 — The no-FFM entry path (brownfield / backend-only apps)

**Learned:** Not every app starts with an FFM. When there is no frontend to build first, or the app is brownfield, the entry path is: **analysis → evidence collection (recon, live run, findings) → discussion → phased plan (Plan of Record) → per-phase map → modules.** FFM is one entry vehicle, not the only one.
**Source:** Stark Web Factory (9-Phase Plan, then Phase 1 map). Also Cyber Pharma Phase 3.
**Touches:** `APP_FACTORY_BLUEPRINT.md`, `SOFTWARE_FACTORY_PLAYBOOK.md`, `FFM_PLAYBOOK.md` (scope statement: when FFM applies and when it does not).
**Status:** Director stated 2026-09-05. Needs codifying.

## J-02 — Phase map as a standing artifact

**Learned:** A large multi-phase plan is direction, not execution. Each phase, when it opens, gets its own **phase map**: the ordered list of modules, what each proves, its exit gate, and open rulings. Map is written once at phase open, versioned, updated when rulings lock. Modules are authored one at a time from the map, never all up front.
**Source:** Cyber Pharma Phase 3 sub-plan (proven) → reused as `WEB_FACTORY_P1_PHASE_MAP`.
**Touches:** `APP_FACTORY_BLUEPRINT.md`, `BIM_PLAYBOOK.md`, `HANDOFF_PACKAGE_PLAYBOOK.md`. Possibly a new short `PHASE_MAP_PLAYBOOK.md` or a section in the Blueprint.
**Status:** Practiced twice. Needs codifying.

## J-03 — Module naming law

**Learned:** `[app]-p[N]-[type][NNN]`. Examples: `web-factory-p1-bim000`, `cyber-pharma-p3-fix001`. Backend work, Next.js or Python, is **always BIM**. FIX for defect modules. PROTO for scouts/experiments. Numbering starts at 000 per phase. Branch name = module name. Zip name = module name. Folder name = module name. QA/certification branch = `qa/` + module name (see J-11).
**Source:** Director ruling 2026-09-05.
**Touches:** `BIM_PLAYBOOK.md`, `HANDOFF_PACKAGE_PLAYBOOK.md`, `ENGINEER_PLAYBOOK.md`, `APP_FACTORY_BLUEPRINT.md`.
**Status:** Ruled. Needs codifying.

## J-04 — Module pack contents, and what "freeze" means (CORRECTED v0.2)

**Learned:** Every module pack ships as a zip named after the module, containing the module folder only, with: `CLAUDE.md` (Engineer front door: seat, read order, rules, closed rulings), `<MODULE>_BRIEF.md`, `<MODULE>_ACCEPTANCE_SPEC.md`, `<MODULE>_CLAUDY_PROMPTS.md`. Pack lands in `agent_docs/ACTION/<module>/` (singular `ACTION` — verified on disk in the scraper repo 2026-09-04 and 2026-09-05; see §Contradictions C-3). Phase map stays outside the pack.
**Learned (correction 1):** the module `CLAUDE.md` is **static**. It never carries state. No "current stage" line. Status lives in the session log, `RECOVERY.md`, and the stage reports in `RESPONSES/`.
**Learned (correction 2, freeze law refined):** the earlier wording "module folder freezes at Engineer handoff" is too broad. The precise law is:

> **The Engineering contract freezes at handoff. Lifecycle evidence lanes may append.**

- **Contract layer (frozen at handoff):** module `CLAUDE.md`, BRIEF, ACCEPTANCE_SPEC, approved Engineer prompts and the rulings they embed. QA grades against this stable contract.
- **Evidence lanes (append-only, later seats):** `<module>/QA/` (see J-13), QA plans, findings, verdict records, retrospective material.
- If QA finds acceptance-spec wording drift, the frozen spec is **preserved** and the adjudication is recorded as an erratum alongside it. History is not rewritten. bim000 produced four such items: AC-10 (module resolution vs output anchoring), AC-41 (changelog names the deleted file), AC-45 (three of four refs existed), AC-52 (see J-08).

**Source:** bim000 packaging and QA, Director corrections 2026-09-05.
**Touches:** `HANDOFF_PACKAGE_PLAYBOOK.md`, `ENGINEER_PLAYBOOK.md`, `QA_PLAYBOOK.md`, `STARTER_KIT_HANDBOOK.md` (agent_docs layout), module-folder layout template, Lesson L1 wording wherever it appears.
**Status:** Ruled. Needs codifying. Supersedes L1's blanket wording.

## J-05 — Staged prompts inside one module

**Learned:** A module may carry more than one Engineer prompt when work must be gated (e.g. dependency upgrade isolated from behavior change). Stages run in strict order; each stage has its own stop rule and its own report; the next prompt is handed over only after the prior stage is green and committed. Acceptance spec numbers its ACs by stage.
**Source:** bim000 CP1 (upgrade) / CP2 (cleanup).
**Touches:** `BIM_PLAYBOOK.md`, `ENGINEER_PLAYBOOK.md`, `TESTING_PLAYBOOK.md` (regression gate between stages).
**Status:** Practiced. Propose as standard.

## J-06 — Controlled dependency upgrade recipe

**Learned:** Upgrade = record installed → identify current stable → review breaking surface for the APIs we touch, with file:line → pin exactly → fresh venv when package identities change → regenerate lock, freeze == lock, `pip check` → full regression + capped smoke on the unchanged code → stop rule reverts and files a finding. Keep the old venv as `venv.bak` until accepted.
**Source:** bim000 Stage 1, crawl4ai 0.6.3 → 0.9.3.
**Touches:** `ENGINEER_PLAYBOOK.md`, `TESTING_PLAYBOOK.md`, Python Track docs.
**Status:** Practiced. Propose as standard.

## J-07 — Run the tool as-is before authoring

**Learned:** Recon (static read) is not enough for brownfield tools. Before authoring the first module, run the tool as-is, capped, with a status observer, and have the Engineer analyze the output. Recon says what the code claims; the run says what it does. Two of the four bim000 additions came from the run, not the recon.
**Source:** baseline-run-002.
**Touches:** `RECON_QUESTIONNAIRE.md`, `ARCHITECT_PLAYBOOK.md`, `stark-recon` skill (add a "live run" optional step).
**Status:** Director-initiated. Propose as standard for brownfield.

## J-08 — Git: agents inspect read-only; the Director holds mutation authority (CORRECTED v0.2)

**Learned (corrected):** The v0.1 wording "Engineer never runs git" was too broad and was disproven in the field. Claudy used `git status`, `git log`, `git diff --stat`, `git branch --show-current` throughout bim000, exercising no git authority. Cody correctly observed that AC-52 as written ("No git command was run by Claudy") failed under literal grading. SOL ruled read-only inspection allowed.

> **Preferred law:** Agents may inspect git read-only. Tony retains git mutation, commit, and merge authority.

- **Allowed read-only inspection:** `status`, `diff`, `log`, `show`, `branch --show-current`, `rev-parse`, and similar non-mutating commands.
- **Director-controlled mutation:** `add`, `commit`, `merge`, `rebase`, `reset`, `checkout`/`switch` when it changes working state, branch create/delete, `cherry-pick`, `push`, force operations, any history or working-tree mutation. No exhaustive blacklist; the principle governs.
- Engineer still ends every stage with a **GIT REMINDER** block listing uncommitted paths. Director commits. Stale git reads by an agent are normal when the Director commits between prompts; the Director states the new HEAD.
- Acceptance specs must say "no mutating git command," not "no git command." bim000 AC-52 stands as the erratum example (J-04).

**Source:** bim000 AC-52, independent Cody PRE-Q, SOL ruling 2026-09-05.
**Touches:** `ENGINEER_PLAYBOOK.md`, `QA_PLAYBOOK.md`, acceptance-spec template, module `CLAUDE.md` template.
**Status:** Ruled by SOL, Director-endorsed. Codify. Supersedes v0.1 J-08.

## J-09 — RESPONSES/OLD archive convention

**Learned:** Director may move closed-module response files into `agent_docs/RESPONSES/OLD/`. New responses always land in `agent_docs/RESPONSES/`. Layout table in the repo `CLAUDE.md` must carry the `OLD/` row.
**Source:** Director ruling R-C, 2026-09-05.
**Touches:** repo-root `CLAUDE.md` template, `ENGINEER_PLAYBOOK.md`.
**Status:** Ruled.

## J-10 — Humanized summaries are an Architect duty

**Learned:** Every dense report the Architect drops gets a plain-language version and a short to-do, unprompted. Director is audio-first; SOL should not have to translate.
**Source:** Director feedback 2026-09-05.
**Touches:** `ARCHITECT_PLAYBOOK.md`.
**Status:** Standing instruction.

---

## J-11 — One forward-only certification line per module (QA branch model)

**Learned:** The prior habit (carried from Cyber Pharma) treated QA branches as disposable and never mergeable, with copy-back rituals. bim000 exposed that as unnecessary complexity. Director ruling:

> **Normal module flow is forward only.** `main → <module> → qa/<module> → main → <next module> → qa/<next module> → main`

1. Engineering builds the candidate on `[app]-p[N]-bim[NNN]`.
2. Director creates `qa/[app]-p[N]-bim[NNN]` from the completed candidate.
3. From that moment the QA branch is the **active certification line**. The original BIM branch is the historical Engineering handoff point, no longer active.
4. **QA-driven rework stays on the QA line.** Cody captures evidence → SOL adjudicates → Claudy fixes **on the QA branch** → Engineering regression → Cody retests independently → SOL re-adjudicates. The seat changes; the branch does not. No bouncing back to the BIM branch because the Engineer is the one repairing.
5. On PASS and close-out, the **QA branch merges to main**. The next module starts from the newly certified main.
6. No second disposable QA branch, no qa-probe branch, no cert branch. One Engineering branch. One QA branch. Forward to main.

**Readability benefit:** the pair `web-factory-p1-bim000` / `qa/web-factory-p1-bim000` tells the lifecycle by name. No branch-cleanup bureaucracy for aesthetics; retention/deletion stays a separate operational choice.

**Source:** bim000 QA, Director ruling 2026-09-05.
**Touches:** `QA_PLAYBOOK.md`, `BIM_PLAYBOOK.md`, `ENGINEER_PLAYBOOK.md`, `APP_FACTORY_BLUEPRINT.md`, `SOFTWARE_FACTORY_PLAYBOOK.md`, `TESTING_PLAYBOOK.md`.
**Status:** Ruled. Codify. **Supersedes** the "QA branch is disposable by default with three guardrails (script harvest, tested-identity record, fixes via FIX loop)" doctrine — see §Contradictions C-1.

## J-12 — Seat separation is the safety boundary, not branch separation

**Learned:** Branch separation represents **lifecycle stage**. Seat separation preserves **independent authority**. Do not confuse the two. Sharing one QA branch across seats is safe because authority stays split:

| Seat | Does | Does not |
|---|---|---|
| **Cody / QA execution** | independently tests, probes, runs commands, challenges Engineering claims, gathers evidence, writes QA reports, identifies defects | repair product code · adjudicate own evidence · issue SOL's Gate Q unless explicitly occupying that seat |
| **SOL / QA Lead** | defines and reviews QA strategy, adjudicates evidence, classifies findings, rules PASS / FAIL / BLOCKED / follow-up, owns Gate Q per Factory authority | write product code |
| **Claudy / Engineer** | repairs approved defects only, adds regression protection, reruns Engineering verification | self-certify QA |
| **Director / Tony** | git authority, approves changes, commits and merges, accepts or rejects risk, merges the certified branch | — |

**Source:** Director ruling 2026-09-05.
**Touches:** `QA_PLAYBOOK.md`, `APP_FACTORY_BLUEPRINT.md` (seat table), `ENGINEER_PLAYBOOK.md`.
**Status:** Ruled. Codify.

## J-13 — QA work lives inside the module: workspace, retention, provenance

**Learned (workspace):** QA-only helpers belong to the module whose claims they verify: `<active module folder>/QA/`. Allowed contents: one-off probe scripts, temporary harnesses, diagnostic and check scripts, evidence generators, command transcripts, logs, screenshots where appropriate, captured evidence, safe-to-retain test data, QA notes. These are **Factory control-plane artifacts**, not application or runtime code, and must never become an application dependency. Canonical parent path is `agent_docs/ACTION/<module>/QA/` (singular `ACTION`, verified on disk; see C-3).

**Learned (retention):** No routine QA cleanup ceremony. Replace "QA makes debris → clean branch → copy selected files → throw branch away" with "Cody keeps QA artifacts contained in the module QA area → they stay as module history." The module is operationally disposable but historically valuable: posterity, evidence, worked examples, retrospectives, doctrine mining, future agents learning how a module was verified. At module close, only a **bounded QA hygiene check**: no helper escaped its QA location · no secrets / credentials / PHI / protected data captured · no giant accidental artifacts in git · runtime code does not import QA helpers · any environment mutation restored · required regression green. Checks pass → artifacts stay. Not a deletion campaign.

**Learned (provenance):** When Cody creates QA-specific artifacts, he keeps a lightweight `QA_WORK_JOURNAL.md` in the module QA area, recording per artifact: path · purpose · which QA question it answered · permanent evidence vs helper · any environment/state mutation performed · restoration required, if any. KISS: creates nothing → no journal ceremony; creates helpers → record as he goes. Purpose is provenance for SOL and future agents, not bureaucracy, not cleanup.

**Source:** bim000 QA, Director ruling 2026-09-05.
**Touches:** `QA_PLAYBOOK.md`, `HANDOFF_PACKAGE_PLAYBOOK.md`, module-folder layout template, `STARTER_KIT_HANDBOOK.md`, module `CLAUDE.md` template (QA lane noted as append-only).
**Status:** Ruled. Codify.

## J-14 — Source/history retention is not production-runtime inclusion

**Learned:** The production boundary is: **`agent_docs/` and Factory module artifacts are not runtime dependencies and must not be required by production code.** That is a different question from whether they live in source control. We may preserve `agent_docs/` in the repository for history while ensuring deployment packaging neither depends on nor unnecessarily ships Factory control-plane material.
**Do not codify** a claim that `agent_docs/` is always deleted from source control before production unless existing Factory doctrine and actual deployment practice prove it. Recorded here as a **candidate doctrine point**, not a ruling.
**Source:** Director note 2026-09-05, arising from J-13.
**Touches:** `APP_FACTORY_BLUEPRINT.md`, `STARTER_KIT_HANDBOOK.md`, `next-deploy-generate` skill (Dockerfile / `.dockerignore` guidance), DevOps operating model.
**Status:** Candidate. Needs Director ruling and a check against current deployment practice before codifying.

## J-15 — QA execution-agent pattern (Cody as SOL's worker)

**Learned:** Before Cody, SOL designed QA commands and the Director ran them one by one. That remains right where Director observation or judgment is required, especially user-visible/frontend acceptance. For **machine-verifiable BIMs** (backend, Python, database), Cody acts as SOL's execution worker:

`SOL defines/challenges verification → Cody executes commands, tests, probes and packages evidence → SOL adjudicates → Claudy repairs approved defects → Cody retests → SOL Gate Q → Tony release/merge`

This removes mechanical terminal work from the Director without weakening QA independence. **Cody's recommendation is not SOL's verdict.** Execution can be delegated; judgment stays with the QA Lead; release authority stays with the Director. Frontend / experiential QA remains human-assisted where visual judgment matters; future browser automation may shrink the mechanical part.
**Source:** bim000 QA, 2026-09-05.
**Touches:** `QA_PLAYBOOK.md`, `TESTING_PLAYBOOK.md`, `ENGINEER_PLAYBOOK.md`, `BIM_PLAYBOOK.md`, `APP_FACTORY_BLUEPRINT.md` (seat roster: Cody added as QA execution seat, model a variable).
**Status:** Practiced on bim000. Director-endorsed. Codify.

## J-16 — Acceptance-spec wording must be gradable literally

**Learned:** Independent QA grades the spec as written. bim000 produced four ACs where the intent was met but the literal text was not (AC-10, AC-41, AC-45, AC-52). Lesson for the Architect: write ACs whose literal check equals the intent. Examples: "no *mutating* git command" not "no git command"; "output lands at repo root" not "runs from any CWD"; count-verification at write time for "the four references" (recon counts drift by the time QA runs). When drift is found anyway, erratum, not rewrite (J-04).
**Source:** bim000 Cody PRE-Q, 2026-09-05.
**Touches:** `ARCHITECT_PLAYBOOK.md`, acceptance-spec template, `QA_PLAYBOOK.md` (erratum procedure). Also feeds `factory-docs-update` v0.4 candidate "count-verification-at-write-time."
**Status:** Lesson. Propose as Architect standard.

---

## Contradictions with existing doctrine (not resolved here; Director rules at sweep time)

- **C-1 — QA branch disposability.** Existing doctrine: "QA branch is disposable by default with three guardrails (script harvest, tested-identity record, fixes via FIX loop)." J-11 and J-13 replace it: one forward-only `qa/<module>` branch, merged to main; helpers retained in the module QA area; QA-driven fixes on the QA branch. **Director has ruled the new model.** The sweep must retire the old wording wherever it lives (likely `QA_PLAYBOOK.md`, `BIM_PLAYBOOK.md`).
- **C-2 — Lesson L1 wording.** "Module folders freeze at Engineer handoff; mid-module file mutation is a doctrine failure." J-04 refines: contract layer freezes, evidence lanes append. L1's intent survives; its blanket wording does not. Sweep must reword L1 everywhere it is cited.
- **C-3 — `ACTION` vs `ACTIONS`.** Disk in the scraper repo: `agent_docs/ACTION/` (singular). Conversational references use `ACTIONS`. **No path change made.** Whether the Factory doc set or other repos use the plural is unverified. Logged as a drift item for the sweep: verify across doc set and live repos, then rule one canonical spelling.
- **C-4 — "QA cadence fires once at module close."** Not contradicted by J-11/J-15, but the PRE-Q step Cody ran on bim000 (independent grading before SOL's verdict) is a sub-step inside that single cadence, not a second cadence. Sweep should say so explicitly to avoid a reading that QA now fires twice.

---

## Questions that require Director ruling

- **Q-1 (J-14):** Confirm the source/history vs runtime boundary as doctrine, and confirm current deployment practice (does `next-deploy-generate` exclude `agent_docs/` from the image today?). Until confirmed, J-14 stays a candidate.
- **Q-2 (C-3):** Canonical spelling, `ACTION` or `ACTIONS`, once the sweep reports where each appears.
- **Q-3 (J-11):** Who creates `qa/<module>`: Director only (git authority), or may SOL request and Director execute as a standing step? Assumed Director-only per J-08; confirm.

---

## Parking lot (unresolved only)

- Transitive-dependency policy: banned packages arriving as transitives (LiteLLM via crawl4ai). Ruling R-A tolerates for this case. May need a general rule.
- Where the phase map lives in a repo (root? `agent_docs/`?). Not yet ruled.
- Whether PROTO modules get acceptance specs or just a question + kill criteria.
- Whether `QA_WORK_JOURNAL.md` (J-13) gets a template in the starter kit or stays freeform.

*Removed in v0.2 (now ruled):* none of the v0.1 parking items were ruled by this set; all three carry forward.

---

*Append below this line as Phase 1 proceeds. Close at Phase 1 retrospective. Then hand to `factory-docs-update`.*
