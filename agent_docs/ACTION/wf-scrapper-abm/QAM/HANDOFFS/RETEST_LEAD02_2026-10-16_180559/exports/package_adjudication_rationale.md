# Package adjudication rationale — LEAD-02 retest

One exact-location adjudication:

- `RETEST_LEAD02_2026-10-16_180559/helpers/t23_untrusted_privacy_retest.py` line 304, `credential_assignment` — the T-23 instrument's own deliberately synthetic leak-control value (`qa-t23` control material), identical in class to the location adjudicated in the historical Q2 package (`Q2_…/helpers/t23_untrusted_privacy.py` line 300). It exists to prove the checker detects planted credential shapes; it is not a real credential. The matched value is not reproduced here.
