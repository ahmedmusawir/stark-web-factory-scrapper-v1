# Shared QA execution instructions

Revision 1.2 · 2026-10-02. Authority: JARVIS Architect amendment under Tony’s delegated authority. QA Lead SOL; independent Executor session binding pending. Follow [README workflow](README.md), [MANIFEST](MANIFEST.md), [STATE](STATE.md), canonical [master plan](../QA/MASTER_QA_TEST_PLAN.md) and [acceptance/errata](../ABM_ACCEPTANCE_SPEC.md). Preserved [QA playbook](../REFERENCES/QA_PLAYBOOK.md) provides verdict vocabulary; this pilot supersedes its generic one-command/operator-at-a-time procedure and any later-cleanup order. No deployment/Gate D work.

## Q1 — inspect and bind; no Q2 execution before plan decision

Verify repo, branch, actual candidate commit and dirty state read-only. Candidate must exist after Tony’s engineering commit; base HEAD plus dirty changes are not a commit identity for the completed build. Record Python, dependency/browser versions, effective config, environment/machine and output ownership without secrets. Independently inspect implementation and evidence against all 48 ACs, not just engineer claims.

Complete each T-01–T-24 concrete binding in the canonical plan: exact command, fixture identity/hash, assertions/expected outcome, mocked boundary, safe environment, expected artifacts, network budget and stop conditions, dependencies and known gaps. Use existing QA journal/ledger, not duplicate plans. Historical engineering diagnostics do not automatically satisfy candidate-bound independent QA. Identify proposed reuse of CHK/E2 evidence; SOL decides, recording candidate compatibility and limitations. No automatic extra full runs. Package Q1 once with requested SOL plan decision; wait for that decision before Q2.

## Q2 — continuous approved execution

Run the approved campaign, collect timestamped command/exit/expected/actual evidence, record ordinary failures and continue unaffected safe checks. Stop dependent/unsafe paths; first intentional document/discovery/REST/media 403/429 or explicit challenge ends live collection with preserved partials/skips and no restart/retry/switch. Five seconds after each intentional operation completes; browser background resources observed separately. No blanket background-POST shutdown, clicks, fills or form submissions. Follow pre-dispatch scope/five-hop redirects and external-media no-probe rules. Do not change transport or security settings to obtain a pass.

Findings go to SOL for adjudication. JARVIS explicitly authorizes product-repair scope; Cody repairs as Engineer on the forward QA branch with one active writer. Tony commits; Executor re-pins and runs impacted checks plus required regression. Disposable QA-helper corrections stay within QA scope, logged separately with before/after evidence, never disguised as product fixes. SOL decides which prior evidence carries forward. Do not automatically rerun costly unaffected collections.

## Cleanup, certificate and later obligations

Inventory proposed deletions, why disposable, retained cited evidence and reproduction dependencies. Tony alone performs authorized destructive cleanup; Executor rechecks candidate identity/dirty state and reference integrity afterward. SOL accepts cleanup before final Gate Q. Documentation-only cleanup does not require full QA rerun; behavior changes require impact retest.

SOL alone issues the exact certificate text with candidate/contract/plan identities, coverage, limitations, evidence and cleanup acceptance. No prewritten PASS or certificate exists. JARVIS closeout carries the certificate verbatim and links its retained path/hash; no paraphrased promotion. Fresh-Fable cold-read is separate from later Astra/fresh-Fable code reviews. Preserve review dispositions, RRM if required, re-pin/retest for later product changes and Tony’s final integration identity.

Every checkpoint package follows [HANDOFFS](HANDOFFS/README.md). Packaging is instruction-driven: there is no claimed validator/exporter. Preserve evidence, exclude secrets/cookies/raw bulk payloads where not needed, and disclose exclusions. Update pilot measurements separately from the product verdict.

## Rulings 1.2 binding addendum

Apply [current dispositions](../ABM_RULINGS_1_2.md) and candidate-bound [BUILD_READBACK](../BUILD_READBACK.md): lock comparison with explicit tooling exclusions; distinct complete/partial/malformed variants; integrity-first snapshot hashes; E-16 exact leak scan/exemptions and isolated control; authored-output boundary checks. Before proposing engineering evidence reuse, independently compare its dirty source inventory to Tony's committed bytes/modes and document all differences. CHK raw-only smoke uses --skip-prepare; E2 full integration remains two runs, no automatic QA pair. SOL retains final reuse/plan decision.
