# Tony's exact Git steps — Gate Q closeout and integration (Tony only; prepared 2026-10-17T11:48:34+06:00; nothing executed by Cody)

Guards are read-only checks; STOP at any unexpected value, divergence or conflict. No blanket staging, force, reset, stash or branch deletion. Do not switch branches while the checkout is dirty.

```bash
# ── Preconditions (read-only; stop if any guard fails) ───────────────────────
cd /home/moose/PYTHON/stark-web-factory-scrapper-v1
git rev-parse --abbrev-ref HEAD            # expect: qa/wf-scrapper-abm
git rev-parse HEAD                         # expect: 9b9e6cc4936b7209cae77fc92f58628dde3965bd
git diff --cached --name-only              # expect: empty (nothing pre-staged)
git status --porcelain --untracked-files=all   # review: only the paths listed below + nothing unexpected
git diff --quiet 0f98bcf095781a3ac7a231c276199224dc531f11 -- recon_pipeline tests agent_docs/SKILLS prepare discover_site smart_crawler requirements.txt requirements.lock pytest.ini && echo "product bytes == certified candidate"

# ── 1. Explicit-path staging of the pending QA (LEAD-04 cleanup) and closeout records ──
git add agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/RETEST_LEAD02_2026-10-16_180559/WRITER_SEAT.md \
        agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/RETEST_LEAD02_2026-10-16_180559/cleanup/ \
        agent_docs/RESPONSES/response_2026-10-17_102830_lead04-cleanup-verification.md \
        agent_docs/SESSIONS/session_2026-10-17.md \
        agent_docs/ACTION/wf-scrapper-abm/QAM/CERTIFICATES/WebFactory_GATE_Q_Certificate_2026-10-17.md \
        agent_docs/ACTION/wf-scrapper-abm/QAM/HANDOFFS/ARCHITECT_CLOSEOUT_GATEQ_2026-10-17_114606/ \
        agent_docs/RESPONSES/response_2026-10-17_114834_gateq-architect-closeout.md \
        agent_docs/ACTION/wf-scrapper-abm/QAM/STATE.md \
        agent_docs/ACTION/wf-scrapper-abm/QAM/README.md \
        agent_docs/ACTION/wf-scrapper-abm/AGENTS.md \
        AGENTS.md CLAUDE.md RECOVERY.md CHANGELOG.md
git status --porcelain                     # review: staged set == intended; no product/test path staged
git diff --cached --stat -- recon_pipeline tests agent_docs/SKILLS requirements.txt requirements.lock pytest.ini   # expect: empty

# ── 2. Closeout commit + push of the QA branch ───────────────────────────────
git commit -m "Gate Q closeout: install JARVIS certificate, LEAD-04 cleanup records, Architect closeout handoff (candidate 0f98bcf, source52 6f35cf8d)"
git push origin qa/wf-scrapper-abm
git status --porcelain --untracked-files=all   # expect: empty before any branch switch; if NOT empty, STOP here

# ── 3. Integration route: qa/wf-scrapper-abm → wf-scrapper-abm (ff-only) → main (--no-ff) ──
# Guards: feature and main must still be at their verified tips; otherwise STOP.
git rev-parse wf-scrapper-abm              # expect: 8fbcff289fde5149be0c0631b08e8a5fbcb3faa4
git rev-parse main                         # expect: 73f96dbcf307e22cd30f7bc8066015f5e5e3f1d4
git ls-remote origin main wf-scrapper-abm  # expect: same two hashes (no divergence on the remote)

git checkout wf-scrapper-abm
git merge --ff-only qa/wf-scrapper-abm     # feature branch catches up to the certified QA tip; STOP if not fast-forwardable
git push origin wf-scrapper-abm

git checkout main
git merge --no-ff wf-scrapper-abm -m "Integrate wf-scrapper-abm: DECIDE→COLLECT→PREPARE module, Gate Q PASS (candidate 0f98bcf, certificate 6ecb6310)"
# STOP on any conflict: do not resolve ad hoc; report and leave the merge for a decision.
git push origin main

# ── 4. Local-main synchronization + post-checks ──────────────────────────────
git fetch origin
git status -sb                             # expect: ## main...origin/main (no ahead/behind)
git log --oneline -3 main
git rev-parse main origin/main             # expect: identical
git checkout qa/wf-scrapper-abm            # optional: return to the QA branch for continued record keeping
```
