# Audit Fixes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix every Critical/High/Medium audit finding and the accepted Low batch, leaving `pytest` (SQLite + Postgres), `vitest`, `tsc`, container HTTP smoke, and a browser pass green.

**Architecture:** Prod-honesty first (env, container, metrics, DB lifecycle, retention, backup), then runtime robustness (threads, WS, errors, No-Sign), then integrity/auth (sessions, persistence, validation, registry, rollback, limits, dead tables), then client hardening, delivery hygiene, and a final verification mirroring the 2026-10-06 gate.

**Tech Stack:** FastAPI + SQLAlchemy + TensorFlow/Keras, React + Vite + TS + Vitest, SQLite (dev) + Postgres 16 (prod/CI), Docker Compose, Prometheus (new: `prometheus_client`, `python-dotenv` only).

**Spec:** 2026-10-06 deep technical audit (chat history). Pinned values copied verbatim: guarded endpoints Bearer-split; open `GET /health|/model|/classes`; `SEQ_LEN=45`, `FEAT_DIM=189`, threshold `0.4`; WS strict `?token=` → 4401; envelope `{success:false,error:{code,message,details},request_id}` on raised 401/403/429; unknown-route 404s stay Starlette-plain; `prediction_id=""` for session-less predicts (do not invent IDs); 501 stubs frozen to P5/P8; `active_model`/`previous_model`/`history` registry keys owned by promote Thick.

## Global Constraints
- Inference math, 45-frame windowing, threshold default `0.4`, `SEQ_LEN`/`FEAT_DIM` unchanged; train/serve feature parity (hands.parity.json) must keep passing.
- New production dependencies allowed ONLY `prometheus_client` + `python-dotenv`, each with `requirements.txt` + `Docs/10` updates in the same task.
- 501 stubs (`/tts`, `/predict/image`, `/predict/video`) stay 501; contracts documented only.
- Frontend default API base stays `http://localhost:8000` (`VITE_API_BASE` override intact); auth split unchanged (WS strict stays).
- No test may depend on a live server; Postgres tests must run on `tmp_path` or CI service, never the dev DB file.

## Review Focus
- Training registration preserves `active_model` (Task 15 test pins it).
- Anonymous and wrong-token WS handshakes get 4401 (existing tests pin it; Task 9 suite must stay green).
- All-blank frames yield `No-Sign`, never a confident label (Task 11 tests pin it).
- `text-to-sign "%"` and `"___"` yield `unsupported`, never a spurious match (Task 14 tests pin it).
- Promote→rollback round-trips `active_model` (Task 16 tests pin it).

---

### Task 1: Env contract, fail-closed compose, test hygiene

**Files:**
- Modify: `backend/requirements.txt`, `backend/app/__init__.py`, `docker/docker-compose.yml`, `Docs/07_API_Contract_SignBridge_AI.md` (env section, 5 lines max)
- Create: `tests/conftest.py`
- Test: `tests/test_env_config.py`

**Interfaces:**
- Consumes: existing `os.getenv` defaults in `backend/app/deps.py`; Task 10 prod guard (`create_app` raises on production + default secret)
- Produces: `.env` auto-loaded at `import app` time with resolved-source log line; `JWT_SECRET` pinned to `test-secret` for the whole suite via `conftest.py`; compose fails fast without `JWT_SECRET`/`POSTGRES_PASSWORD` and sets `APP_ENV=production` + 4-origin `CORS_ORIGINS`

- [ ] **Step 1: Write failing tests** in `tests/test_env_config.py`

```python
def test_prod_with_strong_secret_boots():  # APP_ENV=production + JWT_SECRET=<strong> -> create_app() OK
def test_conftest_pins_test_secret():  # os.environ JWT_SECRET == "test-secret" without per-test setup
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_env_config.py -v` (from `backend/`)
Expected: FAIL (no conftest pin; module missing).

- [ ] **Step 3: Implement**: add `python-dotenv` to requirements; load `<repo>/backend/.env` then `<repo>/.env` in `backend/app/__init__.py` before any `app.*` import (log resolved path at import); create `tests/conftest.py` setting `JWT_SECRET=test-secret` (and nothing else); compose: `APP_ENV=production`, `${JWT_SECRET:?set JWT_SECRET}`, `${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD}`, 4-origin CORS; 5-line env section in `Docs/07`
- [ ] **Step 4: Run full backend suite**

Run: `py -m pytest tests/ -v` (from `backend/`)
Expected: PASS (27+2 new; per-test env juggling still works, conftest is the default).

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt backend/app/__init__.py docker/docker-compose.yml Docs/07_API_Contract_SignBridge_AI.md tests/conftest.py tests/test_env_config.py
git commit -m "feat(env): load .env at startup; fail-closed compose; pin test secret"
```

### Task 2: Container serves predictions + warmup + frontend base ARG

**Files:**
- Modify: `docker/Dockerfile.backend`, `docker/Dockerfile.frontend`, `docker/docker-compose.yml` (backend `--proxy-headers`, keep single worker with comment)
- Create: `scripts/warmup.py`, `scripts/smoke_container.py`
- Test: `scripts/` self-check only (`py scripts/warmup.py --help` exit 0; payload builder unit probe); container proof is a manual gate in Task 24

**Interfaces:**
- Consumes: Task 1 compose env; `GET /health`, `POST /predict` contracts
- Produces: image containing `models/*.keras|scaler|registry` + annotations; entrypoint that boots uvicorn, polls `/health`, fires one warmup `POST /predict`, then idles; `VITE_API_BASE` build ARG (default `http://localhost:8000`); `smoke_container.py --base-url` asserting health/model/classes/predict/text-to-sign over real HTTP

- [ ] **Step 1: Implement Dockerfile + scripts** per Interfaces (HEALTHCHECK via python-urllib CMD-SHELL; entrypoint = shell calling `scripts/warmup.py --wait` semantics: poll health 60 s, one warmup predict, exit code reflects result)
- [ ] **Step 2: Attempt compose proof; record honestly if docker is absent**

Run: `docker compose build backend` then `docker compose up -d backend db`, then `py scripts/smoke_container.py --base-url http://localhost:8000`
Expected: all checks pass; if docker is unavailable, report `DOCKER_ABSENT` with the exact failing command and stop (Task 24 retries).

- [ ] **Step 3: Commit**

```bash
git add docker/ scripts/warmup.py scripts/smoke_container.py
git commit -m "fix(deploy): ship models in image; warmup entrypoint; http container smoke"
```

### Task 3: Real metrics + honest alerts

**Files:**
- Modify: `backend/requirements.txt`, `backend/app/main.py`, `deploy/prometheus.yml`, `deploy/alert_rules.yml`, `Docs/10_Technology_Stack_SignBridge_AI.md`
- Create: `backend/app/metrics.py`, `tests/test_metrics.py`
- Test: `tests/test_metrics.py`

**Interfaces:**
- Consumes: `error_envelope` shape; `get_model()` load point in `backend/app/deps.py`
- Produces: `http_requests_total{path,code}`, `http_5xx_total`, `infer_seconds` histogram (observed in predict + stream paths), `model_loaded` gauge (1 after first successful load); `GET /metrics` (Prometheus exposition, no auth); rewritten alerts against these series + `up==0`

- [ ] **Step 1: Write failing tests**

```python
def test_metrics_endpoint_exposes_series():  # /metrics 200, contains http_requests_total
def test_predict_observes_inference():  # POST /predict -> infer_seconds_count increments, model_loaded == 1
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_metrics.py -v` (from `backend/`)
Expected: FAIL.

- [ ] **Step 3: Implement** per Interfaces (middleware records path/code; histogram observed around both inference call sites; gauge set in `get_model()` post-load; alert rules: `up==0` 2m, `rate(http_5xx_total[5m])>0.01`, `histogram_quantile(0.95,infer_seconds)>0.2` 5m, `model_loaded==0` 5m)
- [ ] **Step 4: Run**

Run: `py -m pytest tests/ -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt backend/app/metrics.py backend/app/main.py backend/app/deps.py deploy/prometheus.yml deploy/alert_rules.yml Docs/10_Technology_Stack_SignBridge_AI.md tests/test_metrics.py
git commit -m "feat(ops): prometheus metrics and honest alerts"
```

### Task 4: Database lifecycle (engine once, sessions closed)

**Files:**
- Modify: `backend/app/deps.py`, `backend/app/routers/session.py`, `backend/app/routers/speech.py`, `backend/app/routers/admin.py`
- Test: `tests/test_db_m1.py` (append), full suite as regression

**Interfaces:**
- Consumes: `Base` in `backend/app/models.py`; `DATABASE_URL` env (honored at call time, cached per URL)
- Produces: `get_engine() -> Engine` (one per URL, `create_all` once per engine); `get_db_session()` contextmanager (`try/finally: close()`); all router call sites converted from bare `next(get_db())`

**Constraints for this task:** keep `get_db()` generator shim (existing tests/importers may use it) delegating to the new machinery; never commit `signbridge_m1.db`.

- [ ] **Step 1: Write failing tests** (append to `tests/test_db_m1.py`)

```python
def test_session_is_closed_after_use():  # session.close called (spy) after context exit
def test_engine_reused_across_calls():  # get_engine() is get_engine()
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_db_m1.py -v` (from `backend/`)
Expected: FAIL (names missing).

- [ ] **Step 3: Implement** per Interfaces; convert every `db = next(get_db())` to `with get_db_session() as db:` (routers + `log_prediction`); `create_all` moves into engine init
- [ ] **Step 4: Run**

Run: `py -m pytest tests/ -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/deps.py backend/app/routers/session.py backend/app/routers/speech.py backend/app/routers/admin.py tests/test_db_m1.py
git commit -m "fix(db): single engine per URL; sessions always closed"
```

### Task 5: Retention that works on Postgres + schedule

**Files:**
- Modify: `scripts/retention.py`, `Docs/DEPLOY_RUNBOOK.md` (cron block, 8 lines max)
- Create: `tests/test_retention.py`
- Test: `tests/test_retention.py`

**Interfaces:**
- Consumes: `Base`, `Feedback`, `Prediction`, `RecognitionSession`, `ApiLog` models; `POLICY` day counts (unchanged values)
- Produces: `sweep(db_url) -> {sessions, predictions, api_logs}` deleting children-first (feedback → predictions → sessions) with tz-aware cutoffs; cron example `0 3 * * * .../retention.py` in runbook

- [ ] **Step 1: Write failing tests**

```python
def test_sweep_deletes_children_first():  # old session+prediction+feedback rows vanish, counts reported
def test_sweep_keeps_fresh_rows():  # recent rows survive
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_retention.py -v` (from `backend/`, own tmp sqlite via `tmp_path`, never the dev DB)
Expected: FAIL.

- [ ] **Step 3: Implement** per Interfaces (tz-aware `datetime.now(timezone.utc)`; explicit child-first deletes; keep `redact()` untouched)
- [ ] **Step 4: Run**

Run: `py -m pytest tests/test_retention.py tests/test_db_m1.py -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/retention.py Docs/DEPLOY_RUNBOOK.md tests/test_retention.py
git commit -m "fix(ops): postgres-correct retention sweep with schedule"
```

### Task 6: Back up the real database

**Files:**
- Modify: `scripts/backup.py`, `Docs/DEPLOY_RUNBOOK.md` (RPO note, 5 lines max)
- Test: extend with tmp-based test in `tests/test_backup.py` (create)

**Interfaces:**
- Consumes: artifact list in `backup.py`; `DATABASE_URL` env
- Produces: `backup()` uses `pg_dump` (subprocess, clear error if binary missing) when URL is postgres, file copy otherwise; manifest records `db_kind`; restore note covers DB + `registry.json:active_model`

- [ ] **Step 1: Write failing tests**

```python
def test_sqlite_backup_still_works(tmp_path):  # manifest HASH-OK on scratch tree
def test_postgres_backup_invokes_pg_dump():  # subprocess mocked; command contains pg_dump + host/db
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_backup.py -v` (from `backend/`)
Expected: FAIL.

- [ ] **Step 3: Implement** per Interfaces (no live PG required; mocked subprocess)
- [ ] **Step 4: Run**

Run: `py -m pytest tests/test_backup.py -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/backup.py Docs/DEPLOY_RUNBOOK.md tests/test_backup.py
git commit -m "fix(ops): back up postgres, not just the sqlite file"
```

### Task 7: CI that actually gates (incl. Postgres job)

**Files:**
- Modify: `.github/workflows/ci.yml`
- Test: none (workflow file; validation = local green + reviewer diff-check + first push run)

**Interfaces:**
- Consumes: `tests/conftest.py` (Task 1), PG service syntax for Actions
- Produces: backend job (`PYTHONPATH=backend`, real `pytest`, no `|| true` on tests), frontend job (real `npm test` → `vitest run`, plus `tsc --noEmit` and `build`), `pg` job (`postgres:16` service + `DATABASE_URL` pointing at it, runs `pytest tests/test_db_m1.py tests/test_retention.py tests/test_backup.py`); `mypy || true` stays with a `# debt` comment

- [ ] **Step 1: Rewrite the workflow** per Interfaces (fix the `--watchAll=false` vitest misuse by calling the repo's own `test` script)
- [ ] **Step 2: Validate locally**: `py -m pytest tests/ -v` (backend), `npx vitest run`, `npx tsc --noEmit`, `npm run build` (frontend); attempt a local PG run only if `pg_isready` exists, else report `NO_LOCAL_PG` (CI run on push is the proof)
- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "fix(ci): working gates incl. postgres job"
```

### Task 8: Inference off the event loop

**Files:**
- Modify: `backend/app/routers/predict.py`, `backend/app/routers/stream.py`
- Test: append to `tests/test_api_p4.py`

**Interfaces:**
- Consumes: existing `infer()` logic and stream inference block (behavior identical, only execution context changes)
- Produces: both inference call sites run via `asyncio.to_thread` (same shapes, same threshold, same timing field semantics)

- [ ] **Step 1: Write failing test**

```python
def test_parallel_predicts_overlap():  # 4 concurrent predicts wall-time < 3x single-predict wall-time
```

- [ ] **Step 2: Run to confirm red/fragile**

Run: `py -m pytest tests/test_api_p4.py::test_parallel_predicts_overlap -v` (from `backend/`, allow 300 s for cold model)
Expected: FAIL (serial ~4x) or flaky-slow.

- [ ] **Step 3: Implement** per Interfaces (extract pure sync inference functions; `await asyncio.to_thread(...)` at the two call sites; no math changes)
- [ ] **Step 4: Run**

Run: `py -m pytest tests/test_api_p4.py -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/predict.py backend/app/routers/stream.py tests/test_api_p4.py
git commit -m "perf: run inference in worker threads"
```

### Task 9: WebSocket validation parity + backpressure

**Files:**
- Modify: `backend/app/routers/stream.py`
- Test: append to `tests/test_ws.py`

**Interfaces:**
- Consumes: REST validation rules (`isinstance list`, `len == 189`, all-finite floats) from `predict.py`; `SEQ_LEN`, `FEAT_DIM`
- Produces: per-frame validation (non-list/wrong-len/non-float/non-finite → `{"type":"error","code":"INVALID_INPUT"}` + `continue`, socket stays open); rolling buffer capped at `SEQ_LEN` (never unbounded); at most one inference per 500 ms per socket (first window always infers immediately so existing flow tests keep passing)

- [ ] **Step 1: Write failing tests**

```python
def test_ws_malformed_frame_stays_open():  # ['oops']*189 -> error frame, socket usable afterwards
def test_ws_nan_frame_rejected():  # NaN frame -> error frame, no prediction emitted for it
def test_ws_flood_is_bounded():  # 200 rapid frames -> prediction received, round-trip < 30 s
```

- [ ] **Step 2: Run to confirm red** (allow 300 s cold model)

Run: `py -m pytest tests/test_ws.py -v` (from `backend/`)
Expected: FAIL (socket wedges on malformed frame — the proven behavior).

- [ ] **Step 3: Implement** per Interfaces (validate before append; `buf = buf[-SEQ_LEN:]`; timestamp gate for inference; no math changes)
- [ ] **Step 4: Run**

Run: `py -m pytest tests/test_ws.py tests/test_api_p4.py -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/stream.py tests/test_ws.py
git commit -m "fix(ws): validate frames, cap buffer, throttle inference"
```

### Task 10: Stop swallowing prediction errors

**Files:**
- Modify: `backend/app/routers/session.py` (`log_prediction`)
- Test: append to `tests/test_history.py`

**Interfaces:**
- Consumes: Task 3 `*_total`/error counters (increment on failure); stdlib `logging`
- Produces: `log_prediction` logs exceptions (`logger.exception`, counter++) and FK-prechecks (session/class rows) before insert; API behavior unchanged on success

- [ ] **Step 1: Write failing test**

```python
def test_log_failure_is_logged_not_silent():  # monkeypatched db.add raising -> predict 200 AND caplog record present
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_history.py -v` (from `backend/`)
Expected: FAIL (nothing logged today).

- [ ] **Step 3: Implement** per Interfaces (keep best-effort return contract: still returns a `pred_*` id shape)
- [ ] **Step 4: Run**

Run: `py -m pytest tests/test_history.py tests/test_api_p4.py -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/session.py tests/test_history.py
git commit -m "fix(db): log prediction persistence failures with FK precheck"
```

### Task 11: Real `No-Sign` state (energy gate + UI mapping)

**Files:**
- Modify: `backend/app/routers/predict.py`, `backend/app/routers/stream.py`, `frontend/src/views/Live.tsx`, `frontend/src/views/Live.test.tsx`
- Test: `tests/test_api_p4.py` (append), `tests/test_ws.py` (append), `Live.test.tsx` (append)

**Interfaces:**
- Consumes: `RecState` (already includes `"No-Sign"`), `STATES` list in `Live.tsx`
- Produces: all-blank/low-energy windows (`max abs < 1e-6` post-normalization — rule now, matches blank-frame semantics) return `status "no-sign"` (REST) / `state "No-Sign"` (WS) with the argmax prediction attached but never `"recognized"`; `toState` exported pure and maps `"no-sign"` → `"No-Sign"`

- [ ] **Step 1: Write failing tests**

```python
def test_blank_frames_yield_no_sign():  # zeros -> status "no-sign", not recognized
```

```ts
test("toState maps no-sign to No-Sign", ...)
```

- [ ] **Step 2: Run both to confirm red**

Run: `py -m pytest tests/test_api_p4.py::test_blank_frames_yield_no_sign -v` (backend) and `npx vitest run src/views/Live.test.tsx` (frontend)
Expected: FAIL on both.

- [ ] **Step 3: Implement**: energy check before inference in both paths (threshold constant `NOSIGN_ENERGY = 1e-6` next to threshold default); export `toState` from `Live.tsx` with the `no-sign` branch; no other UI changes
- [ ] **Step 4: Run**

Run: `py -m pytest tests/test_api_p4.py tests/test_ws.py -v` (backend) and `npx vitest run; npx tsc --noEmit` (frontend)
Expected: PASS. (Note: existing zero-input tests asserting old labels must be updated to `no-sign` in the same commit — list each touched assertion in the report.)

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/predict.py backend/app/routers/stream.py frontend/src/views/Live.tsx frontend/src/views/Live.test.tsx tests/test_api_p4.py tests/test_ws.py
git commit -m "feat: no-sign energy gate end to end"
```

### Task 12: Session lifecycle integrity (reject ghosts, real close, purge)

**Files:**
- Modify: `backend/app/routers/predict.py`, `backend/app/routers/session.py`, `Docs/07_API_Contract_SignBridge_AI.md` (endpoint lines only)
- Test: append to `tests/test_api_p4.py`, `tests/test_history.py`

**Interfaces:**
- Consumes: `log_prediction`, `SESSIONS`, `RecognitionSession.status`
- Produces: `POST /predict` with unknown non-empty `session_id` → 404 `UNKNOWN_SESSION` (empty stays session-less as today); `DELETE /session/{sid}` marks DB row `closed` (in-memory entry removed as today); new `DELETE /sessions/{sid}/purge` removing feedback → predictions → session row, 404 unknown

- [ ] **Step 1: Write failing tests**

```python
def test_predict_unknown_session_404(): ...
def test_close_marks_closed_and_purge_removes(): ...
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_api_p4.py tests/test_history.py -v` (from `backend/`)
Expected: FAIL (new names missing).

- [ ] **Step 3: Implement** per Interfaces (purge order children-first per Task 5 learning; contract docs updated)
- [ ] **Step 4: Run**

Run: `py -m pytest tests/ -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/predict.py backend/app/routers/session.py Docs/07_API_Contract_SignBridge_AI.md tests/test_api_p4.py tests/test_history.py
git commit -m "fix(api): ghost sessions rejected; close and purge are real"
```

### Task 13: Streamed recognitions reach History

**Files:**
- Modify: `backend/app/routers/stream.py`
- Test: append to `tests/test_ws.py`

**Interfaces:**
- Consumes: `log_prediction` (Task 10 version), per-socket last-logged class
- Produces: WS `prediction` with `state == "Recognized"` is persisted via `log_prediction(session_id, ...)` only when its `class_id` differs from the last logged one on that socket (bounded volume, deterministic)

- [ ] **Step 1: Write failing test**

```python
def test_ws_recognized_persists_to_history():  # stream with real sid -> GET predictions contains the class
```

- [ ] **Step 2: Run to confirm red** (allow 300 s cold model)

Run: `py -m pytest tests/test_ws.py -v` (from `backend/`)
Expected: FAIL (nothing persisted today).

- [ ] **Step 3: Implement** per Interfaces
- [ ] **Step 4: Run**

Run: `py -m pytest tests/test_ws.py tests/test_history.py -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/stream.py tests/test_ws.py
git commit -m "feat(stream): persist recognized predictions to history"
```

### Task 14: Input validation hardening batch

**Files:**
- Modify: `backend/app/routers/speech.py`, `backend/app/routers/admin.py`
- Test: append to `tests/test_api_p4.py`

**Interfaces:**
- Consumes: `match_phrases`, `SignAsset` lookup, registry/artifact paths
- Produces: LIKE specials (`%`, `_`, `[`) escaped before the `ilike` fallback (exact match untouched); `POST /promote` rejects unknown `model_id` with 422 `UNKNOWN_MODEL` unless it names an on-disk `models/*.keras` stem or a registry-history id

- [ ] **Step 1: Write failing tests**

```python
def test_t2s_wildcards_unsupported():  # "%" and "___" -> items [], unsupported lists them
def test_promote_unknown_model_422(): ...
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_api_p4.py -v` (from `backend/`)
Expected: FAIL (new names).

- [ ] **Step 3: Implement** per Interfaces
- [ ] **Step 4: Run**

Run: `py -m pytest tests/test_api_p4.py -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/speech.py backend/app/routers/admin.py tests/test_api_p4.py
git commit -m "fix(api): escape like-wildcards; validate promote model ids"
```

### Task 15: Registry merge + portable script paths

**Files:**
- Modify: `scripts/register.py`, `scripts/e2e_10sign.py`, `scripts/smoke_prod.py`
- Test: create `tests/test_register.py`

**Interfaces:**
- Consumes: `models/registry.json` schema incl. `active_model`/`previous_model`/`history`
- Produces: `build_registry(existing: dict) -> dict` pure function preserving deployment keys while refreshing training keys; `ROOT = Path(__file__).resolve().parents[1]` in all three scripts (behavior otherwise identical)

- [ ] **Step 1: Write failing test**

```python
def test_build_registry_preserves_deployment_keys():  # existing active/previous/history survive rebuild
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_register.py -v` (from `backend/`, `PYTHONPATH` covering repo root for the import)
Expected: FAIL.

- [ ] **Step 3: Implement** per Interfaces (script `main` calls the pure function; no retraining, no file writes in tests — pass dicts)
- [ ] **Step 4: Run**

Run: `py -m pytest tests/test_register.py -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/register.py scripts/e2e_10sign.py scripts/smoke_prod.py tests/test_register.py
git commit -m "fix(scripts): registry merge preserves deploys; portable paths"
```

### Task 16: Rollback coherence

**Files:**
- Modify: `backend/app/routers/admin.py`, `Docs/07_API_Contract_SignBridge_AI.md` (rollback lines), `Docs/DEPLOY_RUNBOOK.md` (rollback block)
- Test: append to `tests/test_api_p4.py`

**Interfaces:**
- Consumes: Task 10 `read_registry`/`write_registry`, `active_model`/`previous_model`
- Produces: `POST /rollback` swaps `active_model` ↔ `previous_model` (audit-logged as today), 404 `NO_ROLLBACK_STATE` when no previous exists; runbook rollback = endpoint (or endpoint + file restore), exactly one story

- [ ] **Step 1: Write failing tests**

```python
def test_rollback_restores_previous_model():  # promote X -> rollback -> active back
def test_rollback_empty_404(): ...
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_api_p4.py -v` (from `backend/`, registry try/finally pattern per Task 10 precedent)
Expected: FAIL.

- [ ] **Step 3: Implement** per Interfaces (replaces the audit-only note added in Task 10 of the prior plan)
- [ ] **Step 4: Run**

Run: `py -m pytest tests/test_api_p4.py -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/admin.py Docs/07_API_Contract_SignBridge_AI.md Docs/DEPLOY_RUNBOOK.md tests/test_api_p4.py
git commit -m "feat(admin): rollback reverts the active model"
```

### Task 17: API limits batch (pagination + open-endpoint throttle)

**Files:**
- Modify: `backend/app/routers/session.py`, `backend/app/main.py`
- Test: append to `tests/test_api_p4.py`, `tests/test_history.py`

**Interfaces:**
- Consumes: existing `rate_limit` dependency
- Produces: `GET /sessions` and `GET /sessions/{sid}/predictions` accept `limit` (default 50, max 200, clamped); open `GET /health|/model|/classes` throttled at 120/min/IP via the same limiter

- [ ] **Step 1: Write failing tests**

```python
def test_sessions_limit_clamped():  # limit=1000 -> at most 200 items
def test_open_endpoints_throttled():  # >120 rapid /health -> 429 envelope (mirror existing rate test pacing)
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_api_p4.py tests/test_history.py -v` (from `backend/`)
Expected: FAIL.

- [ ] **Step 3: Implement** per Interfaces
- [ ] **Step 4: Run**

Run: `py -m pytest tests/ -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/session.py backend/app/main.py tests/test_api_p4.py tests/test_history.py
git commit -m "fix(api): paginate lists; throttle open endpoints"
```

### Task 18: Dead schema — log requests, accept feedback, keep User

**Files:**
- Modify: `backend/app/main.py` (sampled ApiLog middleware), `backend/app/routers/session.py` or new `backend/app/routers/feedback.py` (minimal `POST /api/v1/feedback`), `Docs/07_API_Contract_SignBridge_AI.md`
- Test: append to `tests/test_api_p4.py`, `tests/test_history.py`

**Interfaces:**
- Consumes: `ApiLog`, `Feedback`, `Prediction` models; `SAMPLE_RATE` env (default `"1.0"`, parsed float, dev logs everything)
- Produces: middleware inserting `{request_id, path, status_code}` per sampled request (never breaks responses — wrap in try/except); `POST /api/v1/feedback {prediction_id, actual_class_id?, rating?}` → 200 + row, 404 unknown prediction; `User` table kept with a one-line `Docs/08` note (future auth)

- [ ] **Step 1: Write failing tests**

```python
def test_request_is_logged():  # GET /health -> ApiLog row with its request_id
def test_feedback_roundtrip():  # predict w/ session -> POST feedback -> 200; bogus id -> 404
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_api_p4.py tests/test_history.py -v` (from `backend/`)
Expected: FAIL.

- [ ] **Step 3: Implement** per Interfaces (middleware after `request_id_mw` so the id exists; feedback router registered under `/api/v1`)
- [ ] **Step 4: Run**

Run: `py -m pytest tests/ -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/main.py backend/app/routers/feedback.py backend/app/routers/session.py Docs/07_API_Contract_SignBridge_AI.md Docs/08_Database_Schema_SignBridge_AI.md tests/test_api_p4.py tests/test_history.py
git commit -m "feat(api): request logging and feedback endpoint"
```

### Task 19: Client timeouts (fetch + capture deadlines)

**Files:**
- Modify: `frontend/src/api/client.ts`, `frontend/src/views/Live.tsx`, `frontend/src/landmarks.ts`
- Create: `frontend/src/api/client.timeout.test.ts` (name exact; suite runs it automatically)
- Test: new file + `npx vitest run`, `npx tsc --noEmit`

**Interfaces:**
- Consumes: existing `req()` shape and error contract (`Error` with `.code`); `Live` busy/note rendering; `capture(video, frames)` signature (extended with optional deadline, default behavior unchanged)
- Produces: exported `fetchWithTimeout(url, init, ms)` used by `req()` with per-endpoint budgets (predict 120 s, everything else 15 s); timeout errors carry `code "TIMEOUT"` and reach the existing note UI; `capture(video, frames, deadlineMs = 60000)` aborts with the existing no-hands-style Error when the deadline passes

- [ ] **Step 1: Write failing tests** (fake timers + never-resolving fetch mock; no jsdom, pure-function level per repo precedent)

```ts
test("req times out with code TIMEOUT", ...)
test("capture aborts past its deadline", ...)
```

- [ ] **Step 2: Run to confirm red**

Run: `npx vitest run src/api/client.timeout.test.ts` (from `frontend/`)
Expected: FAIL.

- [ ] **Step 3: Implement** per Interfaces (budgets as named constants; no dependency changes)
- [ ] **Step 4: Run**

Run: `npx vitest run; npx tsc --noEmit` (from `frontend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/client.ts frontend/src/views/Live.tsx frontend/src/landmarks.ts frontend/src/api/client.timeout.test.ts
git commit -m "fix(ui): timeouts on requests and capture"
```

### Task 20: MediaPipe fallback, truthful errors, disposal

**Files:**
- Modify: `frontend/src/landmarks.ts`, `frontend/src/views/Live.tsx`
- Test: append to `frontend/src/views/Live.test.tsx` (or `landmarks.test.ts` — follow the seam-level precedent, `vi.mock` allowed, no new deps)

**Interfaces:**
- Consumes: `landmarker()` singleton in `landmarks.ts`; `LandmarkProvider` interface + `status/error` fields
- Produces: creation attempts `["GPU", "CPU"]` in order (first success wins); errors distinguish download failure (network) from delegate failure (unsupported); `dispose()` clears the shared promise; `Live` unmount cleanup calls provider dispose (safe no-op if never created)

- [ ] **Step 1: Write failing tests**

```ts
test("falls back to CPU when GPU delegate fails", ...)
test("dispose clears the shared landmarker", ...)
```

- [ ] **Step 2: Run to confirm red**

Run: `npx vitest run` (from `frontend/`)
Expected: FAIL (new names).

- [ ] **Step 3: Implement** per Interfaces (internal `createLandmarker(delegates, factory)` seam for testability; public behavior identical on the happy path)
- [ ] **Step 4: Run**

Run: `npx vitest run; npx tsc --noEmit` (from `frontend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/landmarks.ts frontend/src/views/Live.tsx frontend/src/views/Live.test.tsx
git commit -m "fix(ui): mediapipe cpu fallback and disposal"
```

### Task 21: CI repair

**Files:**
- Modify: `.github/workflows/ci.yml`
- Test: none (workflow file; validation = local green + reviewer diff-check + first push run)

**Interfaces:**
- Consumes: Task 1 conftest, Task 7 PG patterns (reuse its service block)
- Produces: backend job with `PYTHONPATH=backend` + real `pytest` (fail on red); frontend job with repo's own `test` script + `tsc --noEmit` + `build`; PG job running the DB-touching suites; `mypy || true` kept with `# type-debt` comment

- [ ] **Step 1: Rewrite the workflow** per Interfaces (drop the vitest `--watchAll=false` misuse; no `|| true` on tests/build)
- [ ] **Step 2: Validate locally**: `py -m pytest tests/ -v`, `npx vitest run`, `npx tsc --noEmit`, `npm run build`; PG run only if a server is reachable, else report `NO_LOCAL_PG`
- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "fix(ci): gates that actually gate"
```

### Task 22: Backend hardening batch

**Files:**
- Modify: `backend/app/deps.py`, `backend/app/routers/session.py`, `ai/preprocessing/landmarks.py`, `frontend/src/hands.ts` (comment only), `Docs/07_API_Contract_SignBridge_AI.md` (CSV-restart note, 3 lines)
- Test: append to `tests/test_api_p4.py`, `tests/test_db_m1.py`

**Interfaces:**
- Consumes: `require_auth`, `model_version`, `get_policy`, `SESSIONS`
- Produces: `hmac.compare_digest` token compare; `lru_cache` on registry/policy file readers (restart picks up CSV/registry edits — documented); `SESSIONS` capped at 1000 (oldest evicted); canonicalize docstrings corrected both sides ("least-active-hand-first seating; deterministic, train/serve identical")

- [ ] **Step 1: Write failing tests**

```python
def test_sessions_cache_evicts_oldest():  # 1001 entries -> len<=1000, newest kept
def test_version_reader_cached():  # two calls, one underlying file read (spy) — or mtime-based equivalent
```

- [ ] **Step 2: Run to confirm red**

Run: `py -m pytest tests/test_api_p4.py tests/test_db_m1.py -v` (from `backend/`)
Expected: FAIL.

- [ ] **Step 3: Implement** per Interfaces (no behavior change except the cap; wrong-token 403 path unchanged)
- [ ] **Step 4: Run**

Run: `py -m pytest tests/ -v` (from `backend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/deps.py backend/app/routers/session.py ai/preprocessing/landmarks.py frontend/src/hands.ts Docs/07_API_Contract_SignBridge_AI.md tests/test_api_p4.py tests/test_db_m1.py
git commit -m "fix: constant-time auth, cached registry, bounded sessions, docstring truth"
```

### Task 23: Frontend + deploy hardening batch

**Files:**
- Modify: `frontend/src/api/client.ts`, `frontend/src/views/Live.tsx` (stream base line), `frontend/src/views/History.tsx` (drop dead eslint suppression), `backend/app/main.py` (prod docs gate + security headers), `Docs/07_API_Contract_SignBridge_AI.md`
- Test: `frontend/src/api/client.timeout.test.ts` (append), `tests/test_api_p4.py` (append: prod docs 404)

**Interfaces:**
- Consumes: `VITE_API_BASE` handling; `create_app()` env guard pattern (Task 10)
- Produces: `||` (not `??`) for `VITE_API_BASE` in both frontend spots so `""` falls back to localhost default; `/docs|/redoc|/openapi.json` return 404 when `APP_ENV=production`; minimal security headers middleware (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`); dead suppression removed

- [ ] **Step 1: Write failing tests**

```ts
test("empty VITE_API_BASE falls back to localhost", ...)
```

```python
def test_docs_disabled_in_production():  # APP_ENV=production -> /docs 404, /health 200
```

- [ ] **Step 2: Run both to confirm red**

Run: `npx vitest run src/api/client.timeout.test.ts` (frontend) and `py -m pytest tests/test_api_p4.py::test_docs_disabled_in_production -v` (backend)
Expected: FAIL on both.

- [ ] **Step 3: Implement** per Interfaces
- [ ] **Step 4: Run**

Run: `npx vitest run; npx tsc --noEmit` (frontend) and `py -m pytest tests/ -v` (backend)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/client.ts frontend/src/views/Live.tsx frontend/src/views/History.tsx backend/app/main.py Docs/07_API_Contract_SignBridge_AI.md frontend/src/api/client.timeout.test.ts tests/test_api_p4.py
git commit -m "fix: env-base fallback, prod docs gate, security headers"
```

### Task 24: Full verification + gate record

**Files:**
- Modify: none, except the gate record (`Docs/M6_GATE.md` append, same format as 2026-10-06 entry)
- Test: everything below is the test

**Interfaces:**
- Consumes: all tasks above; Task 2 `smoke_container.py`
- Produces: go/no-go per gate + follow-up issues filed (not fixed here)

- [ ] **Step 1: Suites**

Run: `py -m pytest tests/ -v` (backend, allow 300 s cold model); same with `DATABASE_URL` pointed at a scratch Postgres if reachable, else report `NO_LOCAL_PG`
Expected: all PASS; PG run green or explicitly outstanding.

- [ ] **Step 2: Container smoke**

Run: compose rebuild + `py scripts/smoke_container.py --base-url http://localhost:8000`
Expected: all checks pass; if docker is absent, report `DOCKER_ABSENT` with the exact command (carried, not fixed here).

- [ ] **Step 3: Browser pass** (fresh profile): Live `Ready`; Vocab 50 + Convert `thank you` → Thank You without Settings; History labels + delete; Admin registry-active; camera denial → Error + guidance; Convert with GPU-blocked MediaPipe → CPU-fallback note (Task 20 proof); console zero errors
Expected: matches all of the above.

- [ ] **Step 4: Record the result** in `Docs/M6_GATE.md`: date, commit SHA, pass/fail per step, carried items, follow-ups
