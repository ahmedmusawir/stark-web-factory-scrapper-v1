# T-24 package checker adjudications (exact locations only)

| Location | Pattern | Classification |
|---|---|---|
| `Q2_2026-10-16_142632/helpers/t23_untrusted_privacy.py:300` | credential_assignment | Synthetic T-23 leak-control fixture string (`SYNTH-FAKE-KEY-t23`) authored by the Executor; not a credential. |
| `records/agent_docs/RESPONSES/response_2026-10-16_152740_q2-executor-handoff.md:216` | credential_assignment | Same synthetic control string quoted in the predecessor's T-23 design text. |
| `Q2_2026-10-16_142632/offline/t16_result.json:23` | google_api_key | The public page's own Google Maps embed parameter quoted from verified fixture bytes (handoff §3.3). Shipped faithfully; redacted from authored text. |
| `Q2_2026-10-16_142632/offline/t12_t16_t18_run.txt:26` | google_api_key | Same single value (equality-checked against t16_result.json and the saved public page body, value not printed) in Opy's tee'd T-16 transcript line. |

No other hit exists in the package pre-scan. Any additional or moved hit fails the checker (stale/unadjudicated). No real secret or private state was found; STOP-PRIVACY not triggered.
