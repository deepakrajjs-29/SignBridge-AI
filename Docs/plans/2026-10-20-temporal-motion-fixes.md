# Temporal / Static-vs-Dynamic Fix Plan (P0–P3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Measure temporal information use, add global-wrist trajectory features with gated retraining, improve capture UX and policy honesty, and pin/document preprocessing behavior — without ever activating an unverified model.

**Architecture:** Evaluation-first: pure-Numpy motion probes + baseline runs before any feature change. Feature ablation = parallel Python (`ai/features/build.py::frame_features_v2`) and TypeScript (`hands.ts`) twins producing 193-dim rows (189 existing + 4 trajectory channels), trained offline under new artifact names (`EXP-2026-004`, `scaler_109_traj.npz`, model id `SBAI-MDL-ISL-4.1.0`), activated only if explicit numeric gates pass. UI tasks (countdown, policy note) are independent and ship regardless.

**Tech Stack:** Python 3.14 + TF 2.22 (CPU), NumPy, pytest; React+TS, vitest; existing FastAPI backend.

**Spec:** `Docs/eval/static_dynamic_audit.md` source = the approved static-vs-dynamic audit (saved in Task 0). Approved fix priorities P0–P3 from that audit.

## Global Constraints

- Do NOT touch active artifacts of `SBAI-MDL-ISL-4.0.0`, `scaler_109_real.npz`, or `EXP-2026-003` — new names only (`scaler_109_traj.npz`, `EXP-2026-004`).
- v1 pipeline stays byte-identical: `SEQ_LEN=45`, `FEAT_DIM=189` defaults in `ai/`, `frontend/src/hands.ts` FEAT_DIM, `.env`/`backend/.env` FEAT_DIM=189 unless activation gates pass.
- No `git commit` unless the user explicitly asks.
- No fabricated numbers: every reported metric comes from an executed command; failed gates are recorded as failures.
- Test commands: backend `py -3 -m pytest tests -q` (use `Select-Object -Last N` for tailing on PowerShell); frontend `npm test -- --run`; typecheck `npx tsc --noEmit` (workdir `frontend/`).
- Baselines (frozen): VAL argmax 0.8331, TEST argmax 0.8129 / macro-F1 ~0.8079 (`Docs/eval/08_final_test.json`), webcam-sim `full_sign` 0.822 (`Docs/eval/08_webcamsim_test.txt`).
- **Activation gates for 4.1.0 (all must pass):** VAL argmax ≥ 0.8231; TEST argmax ≥ 0.8029; webcam-sim `full_sign` ≥ 0.8122. On any fail → keep 4.0.0 active, write falsification report, skip Tasks 7A/7B.
- Policy unchanged: `accept_threshold=0.57`, `provisional_threshold=0.0`, `tta_windows=1` (no re-tuning in this plan).

## Review Focus

1. **Train/serve feature drift** (Python vs TS twins produce different 193-dim rows → silent garbage): owned by Task 3 tests (Python synthetic-frame assertions) + Task 7A parity-fixture regeneration and `hands.test.ts`.
2. **Unsafe activation** (switching `active_model`/`FEAT_DIM` with failing gates → 422s on every predict): owned by Task 6 gate checklist (explicit numbers, written report) + Task 7A post-switch `/model` + full pytest.
3. **Artifact collision** (193-dim scaler written over `scaler_109_real.npz`, or models saved into `EXP-2026-003`): owned by Task 5 `--scaler-file`/`--exp` overrides and Task 4 npz-name assertions.
4. **Sample-order integrity** (`split_idx_109.npz` reused on rebuilt tensors with different ordering → garbage split): owned by Task 4 `y`-equality assert before save.
5. **Countdown regressions** (existing Live tests / continuous mode broken by pre-capture delay): owned by Task 8 single-mode-only countdown + timer tests.

---

### Task 0: Save audit document

**Files:**
- Create: `Docs/eval/static_dynamic_audit.md`

**Interfaces:**
- Consumes: the full audit text presented in chat (pipeline diagram, stage evidence, verified-vs-hypothesis split, fix plan, limitations).
- Produces: spec document referenced by this plan; later tasks append an "Implementation Status" section (Task 12).

- [ ] **Step 1:** Write `Docs/eval/static_dynamic_audit.md` containing: pipeline diagram; stage table (capture → features → resample → model → policy) with file/function citations; VERIFIED conclusion "temporal order reaches the model"; verified contributing facts (wrist-relative normalization erases global path, 3.5 s idle dilution, single window prediction, provisional=0.0, blanket sign_type); hypotheses H1–H5 table; fix plan P0–P3; limitations (no live camera, no model.summary run).
- [ ] **Step 2:** Verify: file exists and contains sections "Pipeline", "Verified", "Hypotheses", "Limitations".

---

### Task 1: Motion-probe transforms (P0a)

**Files:**
- Create: `backend/app/eval_probe.py`
- Test: `tests/test_eval_probe.py`

**Interfaces:**
- Produces:
  - `staticify(X: np.ndarray) -> np.ndarray` — input (n,45,F), output same shape, every timestep replaced by `X[:, 0:1, :]` broadcast.
  - `time_shuffle(X: np.ndarray, seed: int = 7) -> np.ndarray` — per-sample independent permutation of the 45 timesteps via `np.random.default_rng(seed)` sequential draws; deterministic for fixed (n,45,F); preserves each sample's row multiset.
- Consumed by: Task 2 script.

- [ ] **Step 1: failing tests** — `tests/test_eval_probe.py`:
  - `test_staticify_replaces_all_steps_with_frame0`: construct (3,45,189) with distinct rows; assert `staticify(X)[:, t] == X[:, 0]` for all t, shape preserved.
  - `test_time_shuffle_deterministic`: same seed → identical output; different seed (use seed 8) → different output for a non-degenerate X.
  - `test_time_shuffle_preserves_row_multiset`: for each sample, `np.sort` along time equal before/after.
  - `test_time_shuffle_permutation_is_valid`: each sample's output rows are a permutation of input rows (compare sorted lexicographically).
- [ ] **Step 2:** Run `py -3 -m pytest tests/test_eval_probe.py -q` → FAIL (module missing).
- [ ] **Step 3:** Implement the two functions in `backend/app/eval_probe.py` (numpy only, no TF imports).
- [ ] **Step 4:** Run test file → PASS.
- [ ] **Step 5:** Run full backend suite `py -3 -m pytest tests -q` → all pass (131+).

---

### Task 2: Motion-sensitivity baseline eval (P0a)

**Files:**
- Create: `scripts/eval_motion_sensitivity.py`
- Output: `Docs/eval/motion_sensitivity.json`

**Interfaces:**
- Consumes: `backend/app/eval_probe.py` (Task 1); `data/dataset/processed/tensors_109_real.npz`, `split_idx_109.npz`, `models/scaler_109_real.npz`; active ensemble via `from app import deps` (pattern copied from `scripts/eval_webcam_sim.py` which already sys.path-inserts `backend/` and `ai/`).
- Produces: JSON `{model_version, n_test, generated, conditions: {full: {argmax_acc, macro_f1}, staticify: {...}, time_shuffle: {...}}}`.

- [ ] **Step 1:** Write script: load test split (all 3629), scale with `scaler_109_real.npz`, build three condition tensors (`identity`, `staticify`, `time_shuffle(seed=7)`), predict each with `deps.recognize_probs` (tta from policy), compute argmax accuracy + macro-F1 per condition, write JSON.
- [ ] **Step 2:** Run `py -3 scripts/eval_motion_sensitivity.py` (workdir repo root).
- [ ] **Step 3:** Verify recorded numbers: `full` argmax_acc within ±0.005 of 0.8129 (sanity — pipeline identical); log `staticify` and `time_shuffle` values **as measured, even if they surprise**. Print all three to console and confirm JSON written. If `full` sanity check fails → stop, debug before proceeding.

---

### Task 3: Feature v2 Python twin (P0b)

**Files:**
- Modify: `ai/features/build.py` (add only; do not alter `frame_features`/`to_sequence`)
- Test: `tests/test_frame_features_v2.py`

**Interfaces:**
- Produces:
  - `FEAT_DIM_V2 = 193` (module constant next to `FEAT_DIM = 189`).
  - `frame_features_v2(canonical_raw: np.ndarray, norm: np.ndarray) -> np.ndarray` — args are the **canonicalized raw** frames (T,2,21,3) and the normalized frames (T,2,21,3) from the same source; returns (T,193) = `np.concatenate([frame_features(norm), traj], axis=1)` where `traj[t] = [w0_u, w0_v, du, dv]`, `w0 = canonical_raw[t, 0, 0, :2]` (hand-0 wrist, image coords), `du/dv = 0` at t=0 else difference vs previous step, all `float32`, `nan_to_num` like v1.
- Consumed by: Task 4 (tensor build), Task 7A (parity regeneration reference).

- [ ] **Step 1: failing tests** — `tests/test_frame_features_v2.py`:
  - `test_v2_shape_and_v1_prefix`: synthetic (T=10,2,21,3) frames; `X2 = frame_features_v2(canonicalize(f), normalize(canonicalize(f)))`; assert shape (10,193) and `X2[:, :189] == frame_features(normalize(canonicalize(f)))` exactly.
  - `test_v2_trajectory_matches_wrist`: linear wrist motion `u = 0.1 + 0.05*t` on hand 0; assert `traj[:,0] == u`, `traj[0,2:4] == 0`, `traj[t,2:4] == [0.05, 0]` (tolerance 1e-6).
  - `test_v2_missing_hand_zeros`: frame with hand 0 all-zero → its wrist + deltas zero in that frame's traj channels.
- [ ] **Step 2:** Run `py -3 -m pytest tests/test_frame_features_v2.py -q` → FAIL.
- [ ] **Step 3:** Implement `frame_features_v2` + `FEAT_DIM_V2` in `ai/features/build.py`.
- [ ] **Step 4:** Tests PASS; full suite PASS (v1 tests untouched).

---

### Task 4: Rebuild tensors with v2 features (P0b)

**Files:**
- Modify: `scripts/build_tensors_v3.py` (add `--feat {v1,v2}`, default `v1`; v2 uses `frame_features_v2(canonical, norm)` and asserts `feat_dim==193` in meta)
- Output: `data/dataset/processed/tensors_109_traj.npz`

**Interfaces:**
- Consumes: Task 3 `frame_features_v2`.
- Produces: npz with same keys as v1 (`X` (14826,45,193), `y`, `files`, meta) — `y` and `files` must be **element-wise identical** to `tensors_109_real.npz` so `split_idx_109.npz` stays valid.

- [ ] **Step 1:** Add `--feat` argument (default `v1`, preserving current behavior exactly); route feature computation; include `feat` in meta JSON.
- [ ] **Step 2:** Add integrity guard at save time for v2: if `tensors_109_real.npz` exists, `assert np.array_equal(y_new, y_v1) and files equal` → else raise with clear message.
- [ ] **Step 3:** Run `py -3 scripts/build_tensors_v3.py --feat v2 --tag 109_traj` (long-running; use generous timeout, report progress).
- [ ] **Step 4:** Verify: `np.load(...).files` keys present, `X.shape == (14826,45,193)`, `y` identical to v1 (guard passed), JSON meta written. If h5 source data missing or count mismatch → stop and report.

---

### Task 5: Training/eval plumbing for 193-dim (P0b)

**Files:**
- Modify: `ai/models/lstm.py` (`build_lstm`/`build_gru` gain `feat_dim: int = FEAT_DIM` parameter used in `keras.Input(shape=(SEQ_LEN, feat_dim))`; defaults keep 189)
- Modify: `scripts/train_v3.py` (add `--feat-dim` default 189 passed to builders; add `--scaler-file` default = current `scaler_{SPLIT_TAG}_real.npz` computation)
- Modify: `scripts/evaluate_v3.py` (add `--scaler-file` default = current hardcoded path)
- Test: `tests/test_lstm_feat_dim.py`

**Interfaces:**
- Produces: builders accepting 193; scripts accepting `--scaler-file scaler_109_traj.npz --feat-dim 193 --exp EXP-2026-004 --model-id SBAI-MDL-ISL-4.1.0 --tag 109_traj`.
- Consumes: Task 4 npz.

- [ ] **Step 1: failing test** — `tests/test_lstm_feat_dim.py`: `build_lstm(nclass=109, feat_dim=193)` → `model.input_shape == (None,45,193)`; `build_lstm()` default → `(None,45,189)`; same for `build_gru`. (Mark/skip if TF unavailable — it is available: tf 2.22.)
- [ ] **Step 2:** Run test → FAIL, implement param in `lstm.py`, PASS.
- [ ] **Step 3:** Add script args (pure plumbing, preserve defaults so existing commands behave identically). Verify with `py -3 scripts/train_v3.py --help` and `py -3 scripts/evaluate_v3.py --help`.
- [ ] **Step 4 — timebox checkpoint:** Run smoke: `py -3 scripts/train_v3.py --mode smoke --arch lstm --tag 109_traj --feat-dim 193 --scaler-file scaler_109_traj.npz --model-id SBAI-MDL-ISL-4.1.0-scout --exp EXP-2026-004`. Record wall-clock per epoch. **If projected full training of both archs exceeds the time budget for today, STOP here and report the estimate to the user before Task 6.**

---

### Task 6: Full training, gates, registration (P0b) — conditional activation

**Files:**
- Create (outputs): `models/EXP-2026-004-lstm-full/…`, `models/EXP-2026-004-gru-full/…`, `models/scaler_109_traj.npz`, registry entry `SBAI-MDL-ISL-4.1.0`
- Create: `Docs/eval/trajectory_ablation_result.md`

**Interfaces:**
- Consumes: Task 5 script overrides, Task 4 npz, Task 2 script (re-run with candidate later), `scripts/register_v3.py`.
- Produces: gate verdict; if PASS: registered-but-maybe-not-active 4.1.0 entry (`register_v3.py` merges without touching `active_model`).

- [ ] **Step 1:** Train both archs: `--mode full` for `--arch lstm` and `--arch gru`, each with `--tag 109_traj --feat-dim 193 --scaler-file scaler_109_traj.npz --model-id SBAI-MDL-ISL-4.1.0 --exp EXP-2026-004`. (Scaler written once by first run — script must not overwrite if exists; if it exists from a prior partial run, delete only `scaler_109_traj.npz` before the first full run to guarantee it matches the tensors.)
- [ ] **Step 2:** Evaluate: `py -3 scripts/evaluate_v3.py --arch lstm --tag 109_traj --exp EXP-2026-004 --model-id SBAI-MDL-ISL-4.1.0 --scaler-file scaler_109_traj.npz` and same for `--arch gru`. Record VAL/TEST accuracy + macro-F1 from emitted reports into `trajectory_ablation_result.md`.
- [ ] **Step 3 — numeric gates:**
  - VAL argmax ≥ **0.8231** (best of the two archs)
  - TEST argmax ≥ **0.8029** (best arch)
  - Webcam-sim: run `scripts/eval_webcam_sim.py` against the candidate — extend it with optional `--model` / `--scaler` overrides (default = active backend behavior unchanged) → `full_sign` ≥ **0.8122**
  - Write every measured number into `Docs/eval/trajectory_ablation_result.md` including per-arch results and motion-probe rerun if features changed results (`eval_motion_sensitivity.py` has `--feat`? if needed, add optional `--tag/--scaler-file/--feat-dim` overrides, default v1 behavior).
- [ ] **Step 4 — verdict:**
  - **ALL PASS:** run `py -3 scripts/register_v3.py --tag 109_traj --exp EXP-2026-004 --model-id SBAI-MDL-ISL-4.1.0` (inspect its scaler/parity inputs first; add `--scaler-file` only if it reads a scaler). Confirm `registry.json` contains 4.1.0 and **`active_model` still 4.0.0** → proceed to Task 7.
  - **ANY FAIL:** record failure honestly, register nothing active, skip Tasks 7A/7B entirely, proceed to Task 8. Mark this plan's Task 7 checkboxes cancelled with the measured numbers.

---

### Task 7A: Activation switch (only if gates PASS)

**Files:**
- Modify: `.env` and `backend/.env` (`FEAT_DIM=193`)
- Modify: `models/registry.json` (`active_model` → `SBAI-MDL-ISL-4.1.0`)
- Modify: `frontend/src/hands.ts` + regenerate `frontend/src/hands.parity.json` + `frontend/src/hands.test.ts`
- Create: `scripts/gen_hands_parity.py`
- Test: `tests/test_feat_dim_consistency.py`

**Interfaces:**
- Consumes: Task 3 `frame_features_v2`, Task 6 pass verdict.

- [ ] **Step 1 (backend):** Update both `.env` files to `FEAT_DIM=193`; set `active_model` to 4.1.0. Add `tests/test_feat_dim_consistency.py`: `deps.FEAT_DIM == 193`, `app.main` model info feat_dim, and predict-router validation rejects an 189-dim payload with 422 while accepting 193 (use existing test client pattern from `tests/`).
- [ ] **Step 2 (frontend parity):** Write `scripts/gen_hands_parity.py`: reads `frontend/src/hands.parity.json`, keeps existing input `frames` fixtures, rewrites expected outputs via the Python v2 pipeline (`frame_features_v2(canonicalize(f), normalize(canonicalize(f)))` for the full-T rows case; keep `to_sequence` handling consistent with what the fixture stores — inspect current fixture schema first and preserve it).
- [ ] **Step 3:** Run generator; update `hands.ts`: `FEAT_DIM = 193`, add `frameFeaturesV2(canonical, norm)`, `buildFeatureRows` = v2 pipeline (single active path); update `hands.test.ts` expectations (dim 193).
- [ ] **Step 4:** Verify: backend full pytest PASS; frontend `npm test -- --run` PASS; `npx tsc --noEmit` clean; restart backend → `GET /health` shows 4.0.0→**4.1.0**, `/api/v1/model` feat_dim **193**; REST predict smoke with 193-dim payload returns `success`; with 189-dim returns 422.

### Task 7B: (conditional) — cancelled if Task 6 fails
- [ ] (No-op placeholder: on gate failure record "4.1.0 not activated; 4.0.0 remains active" in `trajectory_ablation_result.md`.)

---

### Task 8: Single-sign countdown (P1)

**Files:**
- Modify: `frontend/src/views/Live.tsx`
- Test: `frontend/src/views/Live.test.tsx`

**Interfaces:**
- Produces: exported `COUNTDOWN_TICKS = 3`, `COUNTDOWN_MS = 400` (total 1200 ms) — used only by single-sign mode; continuous mode unchanged.
- Behavior: clicking single-sign predict shows an overlay counting 3→2→1 (1 tick per 400 ms) **before** `provider().capture()` starts; abort if unmounted.

- [ ] **Step 1: failing tests** in `Live.test.tsx` (fake timers):
  - `test_single_sign_capture_waits_for_countdown`: click predict with `vi.useFakeTimers()`; assert provider capture NOT called at t=0, called after advancing 1200 ms; overlay text visible during countdown.
  - `test_continuous_mode_has_no_countdown`: continuous start → capture begins without 1200 ms delay (advance 0–100 ms, capture already called).
  - Existing Live tests updated (advance timers where the flow now includes countdown) — all must pass.
- [ ] **Step 2:** Run `npm test -- --run` → new tests FAIL.
- [ ] **Step 3:** Implement countdown state + overlay in `Live.tsx` (single mode path only, inside/before `captureAndRecognizeOnce` when `mode === 'single'`).
- [ ] **Step 4:** `npm test -- --run` all PASS; `npx tsc --noEmit` clean.

---

### Task 9: Settings policy-honesty note (P1)

**Files:**
- Modify: `frontend/src/views/Settings.tsx` (near the manual threshold slider)
- Test: `Settings` test (create `frontend/src/views/Settings.test.tsx` if none exists)

**Interfaces:**
- Produces: visible copy exactly: `Server accept threshold: 0.57 (model policy). Predictions below this appear as Provisional and are never auto-added; your slider can only add a stricter personal gate on top.`

- [ ] **Step 1: failing test:** render Settings (with localStorage cleared of `sb_threshold`), assert the copy above is present.
- [ ] **Step 2:** Run → FAIL; add the note paragraph in `Settings.tsx`; PASS; `npx tsc --noEmit` clean.

---

### Task 10: Preprocessing pin tests + doc note (P2)

**Files:**
- Create: `tests/test_preprocess_window_pins.py`
- Modify: `Docs/eval/static_dynamic_audit.md` (append short "Deferred: padding/mask" note)

**Interfaces:**
- Consumes: `backend/app/deps.py::preprocess_window` (read its current behavior first — pad = repeat last **non-zero** row; linspace monotone; energy gate at 1e-6 → No-Sign indication).

- [ ] **Step 1:** Write pin tests: (a) T=30 input → output (45,F) with rows 30..44 equal to last input row; (b) T=100 → row indices strictly monotone non-decreasing (capture linspace order property by comparing against `np.linspace(0,99,45).astype(int)` result on a ramp input); (c) all-zero input → energy gate triggers (assert the exact current behavior: exception/No-Sign return — match implementation). Run → if any fails, implementation drifted: STOP, do not "fix" the test — report.
- [ ] **Step 2:** PASS with current code (these are characterization tests).
- [ ] **Step 3:** Append to audit doc: "Padding/mask hygiene (P2): model-side mask fix deferred — requires retrain because recurrent layers destroy the Keras mask and pad is a non-zero last-frame copy; current behavior is pinned by `tests/test_preprocess_window_pins.py`."

---

### Task 11: Motion-energy group metrics (P2)

**Files:**
- Create: `backend/app/eval_groups.py`, `scripts/eval_group_metrics.py`
- Test: `tests/test_eval_groups.py`
- Output: `Docs/eval/motion_group_metrics.json`

**Interfaces:**
- Produces:
  - `class_motion_energy(X: np.ndarray, y: np.ndarray) -> np.ndarray` — per-class **median** over samples of mean absolute speed-channel values `|X[:, :, 126:168]|` (v1 layout: speeds at 126:168), shape (C,), ordered by class index.
  - `assign_groups(energy: np.ndarray, n_groups: int = 3) -> np.ndarray` — labels 0=low,1=mid,2=high motion via `np.quantile(energy, [1/3, 2/3])` boundaries (ties → lower group).
- Consumes: `Docs/eval/08_final_test_per_class.csv` (per-class TEST F1) for the report join.

- [ ] **Step 1: failing tests** — toy energy arrays: quantile boundaries correct on `[0,1,2,3,4,5,6,7,8]` → groups `[0,0,0,1,1,1,2,2,2]`; `class_motion_energy` on synthetic (n,45,189) with known speed slice → expected medians; shape (C,) assertion.
- [ ] **Step 2:** FAIL → implement → PASS; full backend suite PASS.
- [ ] **Step 3:** Script: load `tensors_109_real.npz` + per-class CSV, compute groups + group-wise mean/median F1, write JSON + print table. Run it; record actual numbers.

---

### Task 12: Final verification + status docs

**Files:**
- Modify: `Docs/eval/static_dynamic_audit.md` ("Implementation Status" section)
- Modify: `Docs/37_Results_Analysis_SignBridge_AI.md` §17.1 (one-line pointer to audit doc + status)

- [ ] **Step 1:** Run full verification battery: backend pytest; frontend vitest; `npx tsc --noEmit`; confirm `git status` lists expected changes only (no model/scalar overwrites: `git status` should show no modification to `models/SBAI-MDL-ISL-4.0.0*`, `models/scaler_109_real.npz`, `models/EXP-2026-003*`).
- [ ] **Step 2:** Write "Implementation Status" into audit doc: which tasks completed, gate numbers (or failure), motion-sensitivity results, group metrics, countdown/settings status, what remains (live webcam truth CSV — human).
- [ ] **Step 3:** Add cross-reference line in `Docs/37_Results_Analysis_SignBridge_AI.md` §17.1 pointing to the audit doc; update `Docs/eval/webcam_15_sign_checklist.md` status line only if inaccurate.

---

## Self-review notes (decisions locked)

- **Why new exp/scaler names:** `train_v3`/`evaluate_v3` derive `scaler_{SPLIT_TAG}_real.npz` from tag prefix (`109`), so tag `109_traj` would collide → `--scaler-file` overrides are mandatory (Task 5).
- **Why frontend untouched unless activation:** avoids shipping 193-dim requests that the active 189 model would reject with 422 (Review Focus #2).
- **Countdown single-mode only:** continuous mode already has its 600 ms inter-sign buffer; adding 1.2 s there would degrade throughput.
- **No commits:** user has not requested git commits (Global Constraint).
- **P3 (do not re-enable rejected TTA/trim):** intentionally zero tasks — constraint, not omission.
