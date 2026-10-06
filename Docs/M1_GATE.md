# Phase 1 — M1 Gate Record

## Delivered
- T1.1 `backend/app/main.py`: `GET /health`, `GET /api/v1/model` (stub signbridge-lstm-v1, 45/189), `GET /api/v1/classes` (CSV-backed), request-ID middleware, error envelope. Tests: `tests/test_api_stub.py` (3 passed).
- T1.2 `backend/app/models.py` (10 tables: 9 Doc-08 + sign_assets, incl. `sessions.user_id` FK) + `database/seed_m1.py` (verified: classes=50 assets=50 models=1, SQLite-local `signbridge_m1.db`, PG-ready via DATABASE_URL) + `database/migrations/README.md` (Alembic lands P4; M1 round-trip = re-runnable drop/create). Tests: `tests/test_db_m1.py` (1 passed).
- T1.3 `frontend/` shell: `index.html`, `src/main.tsx`, `src/App.tsx` (landing + system-status + camera-permission placeholder), `src/api/client.ts`, `tsconfig.json`; `tsc --noEmit` clean; 139 npm packages installed.
- T1.4 `docker/Dockerfile.backend` (py3.11-slim), `docker/Dockerfile.frontend` (node20+nginx), `docker/docker-compose.yml` (db/backend/frontend + healthchecks). Docker engine unavailable on this host — compose validated statically, containers to be run in P6/P8 environment.

## Verification (M1 per plan)
- [x] `pytest tests/` → 4 passed (3 API + 1 DB)
- [x] Live uvicorn smoke → `health: ok | classes: 50 | first: ISL_001`, `model: SBAI-MDL-ISL-1.0.0 45 189` (LIVE_SMOKE_OK)
- [x] Seed asserts classes=50/assets=50; re-runnable (upgrade/downgrade equivalent for M1)
- [x] `tsc --noEmit` clean
- [x] `GET /api/v1/classes` count == 50 (live + TestClient)
- [ ] Docker compose up (blocked: no engine on host — carried to P6 env)
- [ ] Playwright landing smoke (deferred: needs served frontend — P5)

## Environment notes
- Host Python 3.14.6 (plan pins 3.11 in containers — `Dockerfile.backend` uses `python:3.11-slim`; local runs are for verification only).
- `signbridge_m1.db` (SQLite) is a local verification artifact, gitignored-equivalent; prod uses PG per compose.

Sign-off: Owner-approved via agent gate 2026-09-27 (option: "Approve M1"). Open carries to P6 env: compose up, Playwright smoke.
