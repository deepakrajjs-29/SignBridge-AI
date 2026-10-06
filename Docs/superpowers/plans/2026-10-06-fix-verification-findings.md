# Fix Verification Findings — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all 7 issues and 4 gaps from the 2026-10-06 Playwright/API verification report, in dependency order, leaving `pytest`, `vitest`, `tsc`, and a browser pass green.

**Architecture:** Backend-first contract fixes (single route table, envelope-shaped errors, label-bearing history, phrase-aware text-to-sign), then one root-cause frontend fix (delete compiled `.js` twins shadowing `.ts` sources), then robustness/seed-data work, then gap closure (WS wiring, promote effect, prod auth guard). Each task is independently testable.

**Tech Stack:** FastAPI + TensorFlow/Keras (Python), React + Vite + TypeScript + Vitest, SQLite (dev) / Postgres (prod), Playwright (manual browser pass).

**Spec:** 2026-10-06 verification report in chat history (the spec for this plan). Pinned values copied verbatim below: guarded endpoints return `401 {"detail":{"code":"UNAUTHORIZED"}}` without token; `POST /predict` with 45×189 floats returns `200 {"success":true,"prediction":{...}}`; `POST /text-to-sign {"text":"thank you"}` returns `200` with `"unsupported_words":["thank","you"]`; `GET /sessions/{sid}/predictions` items contain `prediction_id, class_id, confidence, status, created` and **no** `label`; `GET /api/v1/classes` is registered twice (`backend/app/main.py:68`, `backend/app/routers/session.py:47`); served `frontend/src/api/client.js:3` returns `localStorage.getItem("sb_token") ?? ""` while `client.ts:4` returns `... || "change-me"`; `sign_assets` URIs are all `''`; `model_versions` holds one row `signbridge-lstm-v1/development` vs registry `SBAI-MDL-ISL-1.0.0` and `/api/v1/model` reporting `signbridge-gru-v1`.

## Global Constraints
- PythonServing: model input stays 45 frames × 189 features (`SEQ_LEN=45`, `FEAT_DIM=189`); do not change inference math, threshold default `0.4`, or the fixed 45-frame windowing in `predict.py:46-51`.
- Auth split stays: open `GET /health|/model|/classes`; Bearer on predict/session/tts/admin (decide WS in Task 9 and document it).
- 501 stubs (`/tts`, `/predict/image`, `/predict/video`) stay 501 until their owning phases (P5/P8); only their contracts/tests may change.
- No new production dependencies without updating `backend/requirements.txt` + `Docs/10_Technology_Stack_SignBridge_AI.md`.
- Frontend default API base stays `http://localhost:8000` (`VITE_API_BASE` override intact).
- `JWT_SECRET` default `"change-me"` is dev-only; prod must fail fast (Task 10).

## Review Focus
- Empty `sb_token` in a fresh browser must still reach guarded endpoints after Task 2 (default token), and a wrong token must still 401/403.
- `"thank you"`, `"good morning"`, `"good night"` must resolve to `ISL_002`, `ISL_008`, `ISL_009` after Task 5.
- `getUserMedia` that never settles must surface Error + note within 10 s after Task 8 (no silent hang).
- MediaPipe CDN blocked must still leave REST predict usable (Live degrades to session+predict, never a dead page).
- First `POST /predict` on a cold server takes ~60 s (TF import); no task may run it without a ≥300 s timeout, and no health/readiness gate may depend on model load.

---

### Task 1: Baseline, version control, and failing reproductions

**Files:**
- Modify: `tests/test_api_p4.py` (append), `tests/test_history.py` (append)
- Create: `frontend/src/api/client.test.ts`
- Test: same files

**Interfaces:**
- Consumes: existing suites (`pytest tests/`, `npx vitest run`, `npx tsc --noEmit` in `frontend/`)
- Produces: red tests consumed by Tasks 3 (`test_single_classes_route`), 4 (`test_session_predictions_include_label`), 5 (`test_text_to_sign_multiword`), and Task 2 (`token default test`)

- [ ] **Step 1: Init git and commit the untouched baseline**

Run: `git init; git add -A; git commit -m "chore: baseline before verification-fixes"`
Expected: clean `git status`.

- [ ] **Step 2: Write failing backend reproduction tests** (append, do not edit existing tests)

```python
def test_single_classes_route():  # exactly one route object serves GET /api/v1/classes
def test_session_predictions_include_label():  # every item has non-empty "label"
def test_text_to_sign_multiword():  # "thank you" -> items [ISL_002], unsupported []
```

- [ ] **Step 3: Write failing frontend test** in `frontend/src/api/client.test.ts`

```ts
test("token defaults to change-me when nothing is stored", ...)
```

- [ ] **Step 4: Run and confirm red**

Run: `pytest tests/test_api_p4.py tests/test_history.py -v` and `npx vitest run src/api/client.test.ts` (in `frontend/`)
Expected: the 4 new tests FAIL; all pre-existing tests PASS (record any pre-existing failure as-is, do not fix here).

- [ ] **Step 5: Commit**

```bash
git add tests/ frontend/src/api/client.test.ts
git commit -m "test: reproduce verification findings (red)"
```

### Task 2: Remove compiled `.js` twins shadowing `.ts` sources (fixes: app sends no token)

**Files:**
- Delete: `frontend/src/App.js`, `main.js`, `hands.js`, `landmarks.js`, `api/client.js`, `api/stream.js`
- Modify: `frontend/.gitignore` (add `src/**/*.js` guard with `!` exceptions only where a real `.js` source exists — today: none)
- Test: `frontend/src/api/client.test.ts` (from Task 1) + full `vitest run` + `tsc --noEmit`

**Interfaces:**
- Consumes: Task 1 red token test
- Produces: single-source `.ts`/`.tsx` modules; `token(): string` default `"change-me"` is the served code

- [ ] **Step 1: Prove no explicit `.js` imports exist**

Run: `grep -rn "from [\"'].*\.js[\"']" frontend/src --include="*.ts" --include="*.tsx" ; grep -o 'src="[^"]*"' frontend/index.html`
Expected: no `.js` import hits; index entry is `/src/main.tsx`. (If a hit exists, repoint it to the extensionless/`.ts` module in this task.)

- [ ] **Step 2: Delete the six compiled twins and add the gitignore guard**
- [ ] **Step 3: Run tests and typecheck**

Run: `npx vitest run; npx tsc --noEmit` (in `frontend/`)
Expected: PASS, including the Task 1 token test (now executing against `client.ts`).

- [ ] **Step 4: Boot dev server and prove the served client sends the default token**

Run: `npm run dev -- --port 3000`, open `http://127.0.0.1:3000`, Vocab → Convert `hello`
Expected: `hello → Hello` renders, no 401; `localStorage` untouched.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "fix(frontend): remove compiled .js twins; serve .ts sources so default token applies"
```

### Task 3: De-duplicate `GET /api/v1/classes` (fixes: Duplicate Operation ID warning, dead route)

**Files:**
- Modify: `backend/app/routers/session.py:47-51` (delete the `/classes` handler; `class_list` import stays — still used by `label_of`? no: remove only if unused)
- Test: `tests/test_api_p4.py::test_single_classes_route` (Task 1)

**Interfaces:**
- Consumes: Task 1 red test
- Produces: one `GET /api/v1/classes` served from `backend/app/main.py:68-72`

- [ ] **Step 1: Delete the shadowed handler** in `session.py` (keep the file's other routes untouched)
- [ ] **Step 2: Run**

Run: `pytest tests/test_api_p4.py -v`
Expected: PASS; startup log contains no `Duplicate Operation ID` warning (assert by running `pytest -W error::UserWarning tests/test_api_p4.py -v`).

- [ ] **Step 3: Commit**

```bash
git add backend/app/routers/session.py tests/test_api_p4.py
git commit -m "fix(api): single /api/v1/classes route"
```

### Task 4: Include `label` in session predictions (fixes: blank labels in History)

**Files:**
- Modify: `backend/app/routers/session.py:72-88` (`session_predictions` response items)
- Test: `tests/test_history.py::test_session_predictions_include_label` (Task 1)

**Interfaces:**
- Consumes: existing `label_of(class_id: str) -> str` in `backend/app/deps.py:39-43`
- Produces: prediction items shaped `{prediction_id, class_id, label, confidence, status, created}` — `History.tsx:59-66` works unchanged. Explicit non-goal: `prediction_id` stays `""` for session-less predicts (no DB row exists to delete); do not invent IDs.

- [ ] **Step 1: Add `"label": label_of(r.class_id)` to each item** in `session_predictions` (import `label_of` from `app.deps`)
- [ ] **Step 2: Run**

Run: `pytest tests/test_history.py -v`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add backend/app/routers/session.py tests/test_history.py
git commit -m "fix(api): include label in session predictions"
```

### Task 5: Phrase-aware text-to-sign (fixes: multi-word signs unreachable)

**Files:**
- Modify: `backend/app/routers/speech.py:32-51` (`text_to_sign`)
- Test: `tests/test_api_p4.py::test_text_to_sign_multiword` (Task 1) + extend with `"good morning"` → `ISL_008`, `"hello xyz"` → `xyz` unsupported

**Interfaces:**
- Consumes: `SignClass(label, class_id)`, `SignAsset(class_id, uri)` rows; `class_list()` labels as the phrase dictionary
- Produces: `match_phrases(text: str) -> tuple[list[str], list[str]]` (matched phrases in order, leftover single words) used by `text_to_sign`; matching is case-insensitive, longest-phrase-first, max 3 words per phrase

- [ ] **Step 1: Implement `match_phrases`** in `speech.py`: build a `{lower label: class_id}` map from `class_list()` once per call; greedily consume up to 3-word phrases; unmatched single words go to `unsupported_words`
- [ ] **Step 2: Rewire `text_to_sign`** to look up each matched phrase (exact label match first, `ilike` fallback) instead of whitespace tokens; asset lookup per `class_id` unchanged
- [ ] **Step 3: Run**

Run: `pytest tests/test_api_p4.py -v`
Expected: PASS, including `"thank you" → items [ISL_002], unsupported []`.

- [ ] **Step 4: Commit**

```bash
git add backend/app/routers/speech.py tests/test_api_p4.py
git commit -m "fix(api): phrase-aware text-to-sign for multi-word signs"
```

### Task 6: Reseed assets and model registry (fixes: "no visual yet" everywhere, Admin shows wrong model)

**Files:**
- Create: `scripts/seed_sign_assets.py`
- Modify: `database/migrations/` (new migration updating `sign_assets.uri` from manifest + replacing the `model_versions` row with registry values) — or extend the existing seed path if one owns these tables; check first and follow it
- Create: `data/assets/manifest.csv` (`class_id,uri,media_type`; URIs empty where no visual exists yet — honest `supported:false`)
- Test: append to `tests/test_db_m1.py`

**Interfaces:**
- Consumes: `models/registry.json` (`model_id`, `version`); Task 5's per-`class_id` asset lookup
- Produces: `seed_sign_assets(manifest_path) -> dict` (`{updated, missing}` counts); DB invariant: `admin/models` returns the registry's `model_id` with `status: active`

- [ ] **Step 1: Write failing tests**

```python
def test_admin_models_match_registry():  # model_id+version equal registry.json, status active
def test_supported_flags_match_manifest():  # supported == bool(uri) for every class
```

- [ ] **Step 2: Run to confirm red**

Run: `pytest tests/test_db_m1.py -v`
Expected: both FAIL (`signbridge-lstm-v1/development`, empty URIs).

- [ ] **Step 3: Implement script + migration**: upsert the `model_versions` row from `registry.json`; upsert `sign_assets.uri` from `manifest.csv` (leave honestly empty where no visual exists)
- [ ] **Step 4: Run seed, then tests**

Run: `py scripts/seed_sign_assets.py && pytest tests/test_db_m1.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/seed_sign_assets.py data/assets/manifest.csv database/migrations/ tests/test_db_m1.py
git commit -m "fix(data): seed sign asset URIs and registry-accurate model row"
```

### Task 7: Consistent error envelope for auth failures (fixes: 401 shape vs project contract)

**Files:**
- Modify: `backend/app/main.py` (add `HTTPException` handler emitting the `success:false` envelope with `request_id`)
- Test: append to `tests/test_api_p4.py`

**Interfaces:**
- Consumes: existing `error_envelope(request, code, message, status)` in `main.py:22-30`
- Produces: every error response (including 401/403/429) shaped `{"success":false,"error":{"code","message","details"},"request_id"}`; `Docs/07_API_Contract_SignBridge_AI.md` updated in Task 10 to match

- [ ] **Step 1: Write failing test**

```python
def test_unauthorized_uses_envelope():  # POST /api/v1/predict, no token -> success False, error.code UNAUTHORIZED, request_id present
```

- [ ] **Step 2: Run to confirm red**

Run: `pytest tests/test_api_p4.py::test_unauthorized_uses_envelope -v`
Expected: FAIL (current body is `{"detail":...}`).

- [ ] **Step 3: Implement**: map `HTTPException.detail` dicts (`{"code","message"}` from `require_auth`/`rate_limit`) into `error_envelope`; preserve status codes; non-dict details fall back to `{"code":"HTTP_<status>"}` — frontend `client.ts:15-21` parses this shape unchanged
- [ ] **Step 4: Run full backend suite**

Run: `pytest tests/ -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/main.py tests/test_api_p4.py
git commit -m "fix(api): envelope-shaped auth errors"
```

### Task 8: Camera robustness + favicon (fixes: silent hang, 404 noise)

**Files:**
- Modify: `frontend/src/views/Live.tsx:45-60` (`enableCamera`), `frontend/index.html` + add `frontend/public/favicon.svg`
- Test: `frontend/src/views/Live.test.tsx` (create; Vitest + jsdom: mock `getUserMedia` with a never-settling promise, assert Error state + note within virtual time)

**Interfaces:**
- Consumes: existing `note`/`state` rendering in `Live.tsx:126-169`
- Produces: `enableCamera(timeoutMs = 10000)` rejects to the existing Error path; busy text `"Requesting camera…"` while waiting

- [ ] **Step 1: Write failing test**

```ts
test("camera request that never settles shows Error + guidance", ...)
```

- [ ] **Step 2: Run to confirm red**

Run: `npx vitest run src/views/Live.test.tsx` (in `frontend/`)
Expected: FAIL (state stays `Ready`).

- [ ] **Step 3: Implement**: `Promise.race([getUserMedia(...), timeout(10000)])` in `enableCamera`; set busy text on entry, clear in `finally`; add `favicon.svg` + `<link rel="icon">`
- [ ] **Step 4: Run**

Run: `npx vitest run; npx tsc --noEmit` (in `frontend/`)
Expected: PASS; browser console shows no favicon 404.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/Live.tsx frontend/src/views/Live.test.tsx frontend/index.html frontend/public/favicon.svg
git commit -m "fix(ui): camera timeout with guidance; add favicon"
```

### Task 9: Wire the WebSocket stream into Live with REST fallback (closes: dead `stream.ts` client)

**Files:**
- Modify: `frontend/src/views/Live.tsx` (stream-first `start()`, REST `api.predict` fallback on `onError`), `frontend/src/api/stream.ts` (only if the auth decision below needs a signature change)
- Test: existing `tests/test_ws.py` must stay green; manual browser check in Task 11

**Interfaces:**
- Consumes: `connectStream(base, sessionId, {onStatus, onPrediction, onError})` from `api/stream.ts:12-22`; `isFiniteFrame`, `provider().capture`
- Produces: Live attempts WS frames and falls back to one-shot REST predict on any stream error; states shown: `Tracking` (streaming), `Recognized/Uncertain` (either path), `Tracking-Lost` (stream error before any prediction)

- [ ] **Step 1: Decide WS auth and document it in the task commit message**: either (a) keep `/stream` open and note why in `stream.py:1` docstring + `Docs/07`, or (b) accept `?token=` and verify against `JWT_SECRET`, closing the socket with `4401` on failure. (Recommended: (b) — 5 lines, consistent with the split-auth rule.)
- [ ] **Step 2: Add fallback test** in `frontend/src/views/Live.test.tsx` (extend the file from Task 8): mock `connectStream` to invoke `onError`, assert the REST `api.predict` path runs and the result renders (pins: CDN/stream failure never dead-ends Live)
- [ ] **Step 3: Implement stream-first `start()`**: `openSession` → `connectStream` → send captured frames via `sendFrame` → `onPrediction` updates result exactly like the REST path → `stop()`; any `onError`/exception runs the current REST block unchanged
- [ ] **Step 4: Run**

Run: `pytest tests/test_ws.py tests/test_api_p4.py -v` and `npx vitest run; npx tsc --noEmit` (in `frontend/`)
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/Live.tsx frontend/src/api/stream.ts backend/app/routers/stream.py
git commit -m "feat(live): websocket streaming with REST fallback"
```

### Task 10: Gap closure — promote effect, prod auth guard, honest stubs, docs

**Files:**
- Modify: `backend/app/routers/admin.py:47-58` (`promote`), `backend/app/deps.py` (`require_auth` area + startup guard), `Docs/07_API_Contract_SignBridge_AI.md`, `Docs/30_Bug_Defect_Log_SignBridge_AI.md`, `Docs/32_Known_Issues_Limitations_SignBridge_AI.md`
- Test: append to `tests/test_api_p4.py`

**Interfaces:**
- Consumes: `models/registry.json` read/write helpers (add `read_registry()/write_registry()` in `deps.py` next to `model_version()`); `model_version()` must reflect the promoted model after Task 10
- Produces: `promote` persists `{active_model}` to `registry.json` + audit row; non-dev boot with default `JWT_SECRET` refuses to start with a clear message

- [ ] **Step 1: Write failing tests**

```python
def test_promote_switches_active_model():  # promote X -> GET /model reports X (restore registry after)
def test_prod_refuses_default_secret():  # APP_ENV=production + JWT_SECRET=change-me -> create_app raises RuntimeError
```

- [ ] **Step 2: Run to confirm red**

Run: `pytest tests/test_api_p4.py -v`
Expected: both FAIL.

- [ ] **Step 3: Implement**: `promote` writes `registry.json` (`active_model`, history append if the file supports it — otherwise `active_model` + `previous_model`) and commits the `ModelDeployment` + audit rows as today; startup guard in `create_app()` (not import time, so tests can construct the app): `if APP_ENV=production and secret is default: raise RuntimeError(...)`
- [ ] **Step 4: Document the honest stubs**: in `Docs/07` mark `/tts`, `/predict/image`, `/predict/video` as stubbed-with-owner-phase (P5/P8); log fixed items in `Docs/30`; leave TF cold-start (~60 s) and CDN MediaPipe downloads in `Docs/32`
- [ ] **Step 5: Run**

Run: `pytest tests/ -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/admin.py backend/app/deps.py backend/app/main.py tests/test_api_p4.py Docs/
git commit -m "feat(admin): promote switches active model; prod refuses default secret; docs updated"
```

### Task 11: Full verification pass and sign-off

**Files:**
- Modify: none (report only; file issues for anything red instead of fixing here)

**Interfaces:**
- Consumes: all tasks above
- Produces: go/no-go per gate below

- [ ] **Step 1: Backend suite + contract probe**

Run: `pytest tests/ -v` (allow ≥300 s for the first model load)
Expected: all PASS; then probe the live server: `GET /health|/model|/classes` 200; `POST /predict` 401 without token / 200 with token; `POST /text-to-sign {"text":"thank you"}` → `ISL_002`, `unsupported []`.

- [ ] **Step 2: Frontend suite + build**

Run: `npx vitest run; npx tsc --noEmit; npm run build` (in `frontend/`)
Expected: all PASS; `dist/` emitted.

- [ ] **Step 3: Browser pass** (fresh profile, no saved token): load `:3000` → Live renders `Ready`; Vocab lists 50 + Convert `hello` works **without** visiting Settings; Convert `thank you` → Thank You item; History shows labels and delete works; Admin lists the registry (gru) model; Live camera denial/timeout shows Error + note
Expected: matches all of the above; console has no errors except none.

- [ ] **Step 4: Record the result** in `Docs/M6_GATE.md` (or current gate file): date, commit SHA, pass/fail per step, follow-ups filed
