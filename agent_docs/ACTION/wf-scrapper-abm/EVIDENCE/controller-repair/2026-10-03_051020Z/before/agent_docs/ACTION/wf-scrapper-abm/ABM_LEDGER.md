# wf-scrapper-abm — ACCEPTANCE LEDGER

> One row per AC. Engineer fills the first four columns during Block 2 (states: NOT STARTED / IN PROGRESS / IMPLEMENTED / BLOCKED). SOL and a separate QA Executor fill the last four during Block 3 (NOT RUN / PASS / FAIL / BLOCKED / PASS-PENDING-ADJUDICATION / PASS WITH NOTE / NOT APPLICABLE WITH RULING). Requirements live in `ABM_ACCEPTANCE_SPEC.md`; do not restate them here. QA test IDs are the 10x Lab groups T-01…T-24 (SOL may re-bind at QA entry). Candidate SHA is recorded once at the top when Tony commits the engineering candidate.

**Candidate SHA:** PENDING Tony implementation commit · **Base HEAD:** `3c5a0f8ce28bab8c48c0d414d51cd7c4bfadcf5f` plus dirty work, not completed implementation · **Spec:** 1.2 · **Errata:** historical E-01–E-04; new E-05–E-12, JARVIS Architect amendment under Tony’s delegated authority (2026-10-02), QA PENDING. Prospective E-13–E-19: JARVIS Architect ruling under Tony's delegated authority; M-01–M-04 approved as documentation rulings, not test results. Director GO recorded in CJ-017/E-20/E-21. C1–C6 locally implemented; final regression 131 passed, full231-file snapshot passed; CHK live incomplete on same-URL stylesheet misclassification. Stage P/E1/E2 not started; independent QA pending. IMPLEMENTED rows indicate local engineering evidence only, not campaign completion or QA PASS. Current mappings: [ruling dispositions](ABM_RULINGS_1_2.md) and [BUILD_READBACK](BUILD_READBACK.md); historical [change record](ABM_AMENDMENT_1_1.md); process: [QAM](QAM/README.md).

| AC ID | Engineer state | Task | Engineer evidence | QA tests | QA state | QA evidence/candidate | Final disposition |
|---|---|---|---|---|---|---|---|
| AC-001 | NOT STARTED | E1 | — | T-01 | NOT RUN | — | OPEN |
| AC-002 | IMPLEMENTED | C6 | EVIDENCE/build/2026-10-02_135008Z/C6-launch-regression/ | T-02 | NOT RUN | — | OPEN |
| AC-003 | IN PROGRESS | C6 complete / Stage P pending | EVIDENCE/build/2026-10-02_135008Z/C6-launch-regression/ | T-03 | NOT RUN | — | OPEN |
| AC-004 | IMPLEMENTED | C1 | EVIDENCE/build/2026-10-02_135008Z/C1-regression/ | T-02 | NOT RUN | — | OPEN |
| AC-005 | BLOCKED | C3 | EVIDENCE/build/2026-10-02_135008Z/CHK-live-smoke/; blocker-review/root-event-excerpt.json; local proofs retained | T-04 | NOT RUN | — | OPEN |
| AC-006 | IMPLEMENTED | C3 | EVIDENCE/build/2026-10-02_135008Z/C3-complete-regression/ | T-05 | NOT RUN | — | OPEN |
| AC-007 | IMPLEMENTED | C2 | EVIDENCE/build/2026-10-02_135008Z/C2-regression-fixed/ | T-06 | NOT RUN | — | OPEN |
| AC-008 | IMPLEMENTED | C6 | EVIDENCE/build/2026-10-02_135008Z/C6-launch-regression/ | T-06 | NOT RUN | — | OPEN |
| AC-009 | IMPLEMENTED | C1 | EVIDENCE/build/2026-10-02_135008Z/C1-regression/ | T-07 | NOT RUN | — | OPEN |
| AC-010 | IMPLEMENTED | C3 | EVIDENCE/build/2026-10-02_135008Z/C3-complete-regression/ | T-07 | NOT RUN | — | OPEN |
| AC-011 | IMPLEMENTED | C4 | EVIDENCE/build/2026-10-02_135008Z/C4-regression/ | T-08 | NOT RUN | — | OPEN |
| AC-012 | IMPLEMENTED | C4 | EVIDENCE/build/2026-10-02_135008Z/C4-regression/ | T-08 | NOT RUN | — | OPEN |
| AC-013 | IMPLEMENTED | C6 | EVIDENCE/build/2026-10-02_135008Z/C6-launch-regression/ | T-08 | NOT RUN | — | OPEN |
| AC-014 | IN PROGRESS | C4/P2 | — | T-09 | NOT RUN | — | OPEN |
| AC-015 | IMPLEMENTED | C5 | EVIDENCE/build/2026-10-02_135008Z/C5-regression/ | T-10 | NOT RUN | — | OPEN |
| AC-016 | BLOCKED | C6 | EVIDENCE/build/2026-10-02_135008Z/CHK-live-smoke/; blocker-review/root-event-excerpt.json; local proofs retained | T-11 | NOT RUN | — | OPEN |
| AC-017 | IMPLEMENTED | C3 | EVIDENCE/build/2026-10-02_135008Z/C3-complete-regression/ | T-05 | NOT RUN | — | OPEN |
| AC-018 | IMPLEMENTED | C6 | EVIDENCE/build/2026-10-02_135008Z/C6-launch-regression/ | T-11 | NOT RUN | — | OPEN |
| AC-019 | IN PROGRESS | C6 complete / Stage P pending | EVIDENCE/build/2026-10-02_135008Z/C6-launch-regression/ | T-12 | NOT RUN | — | OPEN |
| AC-020 | IN PROGRESS | C6 complete / Stage P pending | EVIDENCE/build/2026-10-02_135008Z/C6-launch-regression/ | T-12 | NOT RUN | — | OPEN |
| AC-021 | NOT STARTED | P6 | — | T-13 | NOT RUN | — | OPEN |
| AC-022 | NOT STARTED | P6 | — | T-13 | NOT RUN | — | OPEN |
| AC-023 | NOT STARTED | P2 | — | T-14 | NOT RUN | — | OPEN |
| AC-024 | NOT STARTED | P2 | — | T-09 | NOT RUN | — | OPEN |
| AC-025 | NOT STARTED | P3 | — | T-15 | NOT RUN | — | OPEN |
| AC-026 | NOT STARTED | P4 | — | T-16 | NOT RUN | — | OPEN |
| AC-027 | NOT STARTED | P4 | — | T-14 | NOT RUN | — | OPEN |
| AC-028 | NOT STARTED | P5 | — | T-10 | NOT RUN | — | OPEN |
| AC-029 | NOT STARTED | P6 | — | T-17 | NOT RUN | — | OPEN |
| AC-030 | NOT STARTED | P5 | — | T-17 | NOT RUN | — | OPEN |
| AC-031 | NOT STARTED | P6 | — | T-18 | NOT RUN | — | OPEN |
| AC-032 | NOT STARTED | P6 | — | T-18 | NOT RUN | — | OPEN |
| AC-033 | NOT STARTED | P6 | — | T-19 | NOT RUN | — | OPEN |
| AC-034 | NOT STARTED | P6 | — | T-20 | NOT RUN | — | OPEN |
| AC-035 | NOT STARTED | QA (R5) | — | T-20 | NOT RUN | — | OPEN |
| AC-036 | NOT STARTED | P6 | — | T-19 | NOT RUN | — | OPEN |
| AC-037 | NOT STARTED | P1 | — | T-19 | NOT RUN | — | OPEN |
| AC-038 | NOT STARTED | P6 | — | T-20 | NOT RUN | — | OPEN |
| AC-039 | BLOCKED | E1 | EVIDENCE/build/2026-10-02_135008Z/CHK-live-smoke/; blocker-review/root-event-excerpt.json; local proofs retained | T-21 | NOT RUN | — | OPEN |
| AC-040 | NOT STARTED | E2 | — | T-21 | NOT RUN | — | OPEN |
| AC-041 | BLOCKED | C1/E1 | EVIDENCE/build/2026-10-02_135008Z/CHK-live-smoke/; blocker-review/root-event-excerpt.json; local proofs retained | T-22 | NOT RUN | — | OPEN |
| AC-042 | BLOCKED | C3/E2 | EVIDENCE/build/2026-10-02_135008Z/CHK-live-smoke/; blocker-review/root-event-excerpt.json; local proofs retained | T-22 | NOT RUN | — | OPEN |
| AC-043 | NOT STARTED | E1 | — | T-23 | NOT RUN | — | OPEN |
| AC-044 | NOT STARTED | E1 | — | T-23 | NOT RUN | — | OPEN |
| AC-045 | NOT STARTED | all | — | T-24 | NOT RUN | — | OPEN |
| AC-046 | NOT STARTED | E2 | — | T-24 | NOT RUN | — | OPEN |
| AC-047 | NOT STARTED | E1 | — | T-01 | NOT RUN | — | OPEN |
| AC-048 | NOT STARTED | closeout | — | T-24 | NOT RUN | — | OPEN |
