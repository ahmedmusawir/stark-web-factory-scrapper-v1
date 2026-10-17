# Collector-initiated closure audit

Scope: shared BrowserSession shutdown; installed libraries inspected only, never edited.

| Path | Previous closure | Current sequence |
|---|---|---|
| Normal context exit | crawler.__aexit__ before pending tasks settle | shutdown fence, bounded registered-ID abort/drain, then crawler.__aexit__ |
| event log OSError/BufferError | scheduled page.close | request_shutdown immediately fences admission and shares the drain |
| document Network.dataReceived cap | scheduled page.close | same shutdown after preserving document_response_limit |
| intentional response refusal/challenge headers | scheduled page.close | same shutdown after sticky first reason |
| Python read task cancellation | scheduled page.close | same shutdown; terminal cancelled outcome retained |
| Python read timeout | scheduled page.close | same shutdown; available partial evidence/result boundaries unchanged |
| Capture cancellation/deadline | finally/context exit; no direct close | shared __aexit__, no replacement navigation |
| browser-owned read body cap/JS deadline | AbortController/reader.cancel then result handoff | transport unchanged; later context exit uses shared shutdown |

Installed Crawl4AI AsyncWebCrawler.__aexit__/strategy.close delegates browser_manager.close; kill_session closes page and may close its context. The shared sequence executes before that owned teardown. async_crawler_strategy.py's crawl-finally close is guarded by no session_id; our capture supplies the existing persistent session_id. Screenshot/PDF helper closure is not invoked by this Capture path. Startup rollback has no registered collection interceptions. BrowserManager's expired-session cleanup is library-owned (1800s TTL); external/library-initiated page loss remains the unexpected-loss failure boundary, not a cancellation guarantee.

recon_pipeline/capture.py supervised_capture owns independent hard timers: operation deadline and max_seconds-30 global cutoff, then SIGINT with an existing 5s process grace and possible SIGKILL. This repair does not change them or the process group. The controller drain stays within min(global run deadline, shutdown start + existing finalization_reserve), retaining closure time inside that budget. Forced supervisor termination can preempt confirmation; no success or zero-traffic claim follows. A command already resolving is awaited and never retried. A late pause is denied using its actual owner; late/unavailable/failed cancellation is retained explicitly.

Only a successful Fetch.failRequest reply sets abort_confirmed. A closed-target error remains unconfirmed even when the older narrowly eligible incidental-cleanup error is nonfatal. Confirmed native incidental cancellation behavior, stopped continuation, redirect/identity controls and compact body encoding are retained. Shutdown findings are bounded (20-entry event samples; complete in-memory list bounded by the existing 10,000-entry registry). Successful drain describes registered interceptions; it does not certify cancellation of previously dispatched stream bytes, excluded resources, or unexpected external closure.
