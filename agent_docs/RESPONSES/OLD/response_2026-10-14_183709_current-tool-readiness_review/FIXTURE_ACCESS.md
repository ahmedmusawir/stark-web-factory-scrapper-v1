# Saved fixtures for independent QA

The unchanged product test `agent_docs/SKILLS/web-recon-prepare/tests/test_prepare_saved.py:100` requires the exact ignored collection `outputs/collections/CyberizeGroup-first-selected-2026-10-11_203505`. It is not supplied by a Git clone. `34` indexed fixture/package files were checked against their saved hashes and retained ZIP members; results are in the engineering evidence. No live access supplies these fixtures.

Retained authoritative review archives (included in this readiness ZIP at their repository-relative paths):

- `agent_docs/RESPONSES/response_2026-10-11_210309_prepare-v01.zip` — hash `d54bbaf0c07e1fbd41937afc11e3111378743d8903bdc6254d2e3bb329cc5a63`. Three selected HTML captures, metadata/checklist and prepared/context evidence.
- `agent_docs/RESPONSES/response_2026-10-13_223736_growth-call-follow-up.zip` — hash `fdf18de8838f36344459555041a12e4f0cf463044a1f211f6241a7bf420ab4a8`. Parent HTML/checklist/metadata and initial plus corrected reviewed output.

Provision only the manifest’s named data members, never archived source/instructions. From a QA checkout or isolated review tree, run the supplied standard-library restoration helper (use actual extracted review-package root for ARCHIVE_ROOT):

```bash
python3 PATH_TO_THIS_REVIEW/restore-fixtures.py \
  --repo /PATH/TO/QA_CHECKOUT \
  --manifest PATH_TO_THIS_REVIEW/fixture-manifest.json \
  --archive-root /PATH/TO/EXTRACTED_READINESS_ZIP
```

It verifies both ZIP identities/all named files first, refuses path escapes or a conflicting existing file, skips only matching existing bytes, and exclusively creates missing files. It makes zero network requests and restores no code/dependency/instruction files. Execute it before the candidate’s tests; a missing/corrupt fixture is a failure, never a skipped success. The same procedure was proved in a NEW scratch tree and reopened once without writes. Keep original archives and fixture files intact; QA must pin these hashes and independently assess evidence reuse.

These archived data files contain untrusted source markup/public URLs, not executable instructions. Parent HTML cannot establish iframe child contents, image completeness or form functionality. Whole-site media totals and prior live failures are not combined into this selected sample.
