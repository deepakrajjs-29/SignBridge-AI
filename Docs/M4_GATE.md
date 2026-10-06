# Phase 4 — M4 Gate Record

## Delivered (all against registered GRU `SBAI-MDL-ISL-1.0.0`, M3 debt inherited)
- T4.1 `backend/app/routers/predict.py`: `POST /predict|/recognize|/sequence` (real inference, 45-window sample/pad, 189-dim + NaN/Inf → 422, >600 frames → 413, Bearer + rate-limit, `processing_time_ms`); `/predict/image|/video` → 501 `CV_UNAVAILABLE` (MediaPipe absent on py3.14 host; py3.11 container in P8).
- T4.2 `routers/session.py`: `POST /session` → `sess_*`, `DELETE /:id` (404 unknown), `/reset` alias; `GET /classes` (50, CSV-backed); `log_prediction()` persists `sessions→predictions` rows (best-effort).
- T4.3 `routers/speech.py`: `POST /tts` → 501 `TTS_NOT_CONFIGURED` (engine wiring = P5); `POST /text-to-sign` → real DB lookup (`items` + `unsupported_words`, `supported` flag).
- T4.4 `routers/admin.py` (`/admin`): `GET /models`, `POST /promote|/rollback` (+audit rows with ip_hash, RBAC via shared-secret Bearer; JWT upgrade queued P7).
- T4.5 `scripts/retention.py`: sweep 90/180/30/30 (verified `{'sessions':0,'predictions':0,'api_logs':0}` on empty DB) + `redact()` (Bearer/password masking); `deps.py` rate limit (60/min, 429) + split auth (open `/health|/model|/classes`).
- Shared `backend/app/deps.py`: lazy model/scaler/policy load, `model_version()` from registry.

## Verification (M4 per plan)
- [x] `pytest tests/` → **13/13** (4 M1 + 9 M4 matrix: 200s incl. alias, 401/403, 422 dim + 413, 501×3, session 404 path, TTS/T2S incl. unsupported word, admin RBAC + audit, 429)
- [x] Live smoke: health ok, classes 50, model SBAI-MDL-ISL-1.0.0 45/189
- [x] Retention sweep runs clean; `TC-DB-008/TC-PRI-008` mechanics proven (policy enforcement on empty DB; aged-row purge covered by code path)
- [x] Fixed in-pass: scaler broadcast bug (500→200), rate-limit default-arg bug (429 testable)
- [ ] Deferred with record: MediaPipe image/video inference (P8 container), JWT proper (P7), PG live run (compose env, P6)

Sign-off: Owner-approved via agent gate 2026-09-27 (option: "Approve M4"). Deferred: CV inference (P8), JWT (P7), PG live (P6).
