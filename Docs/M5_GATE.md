# Phase 5 — M5 Gate Record

## Delivered
- T5.0 backend gap (P4 addendum): `session_id` on PredictBody → `log_prediction()` writes `sessions→predictions` rows; `GET /sessions`, `GET /sessions/{sid}/predictions` (404 unknown), `DELETE /history/{pid}`; `tests/test_history.py` green.
- T5.1 `src/views/Live.tsx`: camera enable/stop (getUserMedia + denial copy), 7-state machine display (Ready/Tracking/Recognized/Uncertain/No-Sign/Tracking-Lost/Error), Start (session open → DemoProvider 45×189 → `/predict`) / Speak (501-aware note) / Clear, aria-live status + 40px result.
- T5.2 `src/views/History.tsx`: session select, prediction list, per-item Delete, refresh, empty-state copy, no-raw-video notice.
- T5.3 `src/views/Vocab.tsx`: 50-class browse + search, text-to-sign convert with unsupported-words messaging; `src/views/Settings.tsx`: Bearer token store, help copy (Uncertain rule, deletion, human verification).
- T5.4 `src/views/Admin.tsx`: RBAC-gated model list + promote/rollback with audit receipt + 401 guidance; `src/App.tsx` tab nav with aria-current; `src/api/client.ts` typed client (split-auth aware); `src/landmarks.ts` provider interface (Demo now, tasks-vision in P6).

## Verification (M5 per plan, host-adapted)
- [x] `tsc --noEmit` clean (after @types/node for vitest d.ts)
- [x] `vitest run` 2/2 (DemoProvider 45×189 finite contract)
- [x] `vite build` success (dist/ emitted)
- [x] Backend `pytest` 14/14 (incl. history round-trip: predict→list→delete→404)
- [x] Static a11y: labels on all inputs, button-native controls, aria-live/alert roles, no color-only status (state names as text)
- [ ] Playwright E2E in real browser (no browser engine on host — queued to P6 env with compose)
- [ ] axe scan (no engine on host — queued to P6 env; checklist above is the interim evidence)

Sign-off: Owner-approved via agent gate 2026-09-27 (option: "Approve M5"). Carries to P6 env: Playwright E2E, axe scan.
