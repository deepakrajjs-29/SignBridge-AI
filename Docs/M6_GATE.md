# Phase 6 — M6 Gate Record

## Delivered
- T6.1 `backend/app/routers/stream.py`: `WS /api/v1/stream?session_id=` (status Ready/Tracking/Tracking-Lost, 45-frame rolling buffer → real GRU prediction, heartbeat, stop/tracking-lost reset, INVALID_INPUT/UNKNOWN_TYPE errors); `frontend/src/api/stream.ts` client (start/frame/heartbeat/stop + REST fallback on error).
- T6.2 `scripts/e2e_10sign.py` + `docs/M6_E2E.json`: staged 10-sign script (frozen test clips, classes 0–9) via REST with session → **10/10 correct**, DB chain (session row + 10 prediction rows), WS drop→reconnect→prediction True.
- T6.3 `configs/compat.json` (model↔preproc↔app triple + flag list + fail-fast rule); threshold/seq/fps remain env flags.

## Verification (M6 per plan)
- [x] 10-sign staged script **10/10 ≥ 90%** (M6_E2E.json; note: staged fixed script, overall frozen-test remains 0.824 per M3 debt)
- [x] `sessions → predictions` FK-linked rows verified in script output
- [x] WS reconnect recovers with fresh prediction (no ghosts)
- [x] `pytest` **15/15** (14 prior + WS flow), frontend `tsc` clean
- [x] `Session→DB` gate passes
- [ ] Compose/browser E2E (no engine on host — carried to P8 env with P5 items)

## In-pass fix worth noting
E2E harness initially double-scaled inputs (bogus 2/10) — root-caused to harness math, not model/API; fixed by sending raw npz features verbatim. Model + serving path vindicated.

Sign-off: Owner-approved via agent gate 2026-09-27 (option: "Approve M6"). Carries: compose/browser E2E (P8 env).
