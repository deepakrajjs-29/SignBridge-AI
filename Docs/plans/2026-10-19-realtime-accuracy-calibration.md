# Real-Time Accuracy & Confidence Calibration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (hybrid variant in use: native lead + subagents for isolated tasks) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Raise genuine real-time webcam recognition toward 80% on an independent evaluation set by fixing confidence calibration, introducing a three-state decision policy (Accepted / Provisional / Uncertain), hardening temporal commit behavior, and pushing window accuracy — everything tuned on VAL, TEST measured once, final report produced.

**Architecture:** Pure decision/calibration functions in `backend/app/deps.py` (`calibrate_probs`, `decision_status`, `recognize_probs`) consumed by REST + WS + eval scripts; a single VAL-only fitting script (`calibrate_v4.py`) writes `calibration.json` + `policy.json`; frontend gains a Provisional display state, streak-based release re-arm, explicit-user-gate-only thresholding, and full-T capture rows sent via one new WS `window` message (parity with REST by shared preprocessing); evidence-gated retrain and TTA.

**Tech Stack:** Python 3.14 / FastAPI / TF / NumPy (backend), React + TS + Vitest (frontend), existing MediaPipe capture + WS stream. No model-architecture rebuild.

**Spec:** User's 9-phase accuracy+calibration master prompt (session 2026-10-19; all decisive values pinned inline below). Supporting: `Docs/M12_WEBCAM_ACCURACY.md` (root causes + shipped capture fixes).

**Execution mode (user-approved):** HYBRID — native agent is project lead, owner of all shared-file changes, integrator, and final verifier. Fresh subagents execute isolated tasks (Tasks 1, 6, 7, 9); native reviews each subagent's diff before integration. Parallel only where files and dependencies are disjoint; otherwise sequential.

## Global Constraints

- **No git commit/push/merge until the user explicitly says so** — this plan contains no commit steps (overrides the skill's default commit steps). Existing uncommitted changes are preserved and backed up before any new modification.
- Fit temperature, thresholds, and the TTA flag **only on SPLIT-109 val** (n=2397). Test (n=3629) and the h5 webcam-replay test pool are evaluated **exactly once** in Task 8; val-split runs of the same harnesses are allowed for gates.
- Every reported number carries its source: `offline-npz`, `h5-webcam-replay`, or `user-reported`. Offline numbers are never labeled real-time. Accepted-accuracy is never quoted without coverage and overall accuracy alongside. No fabricated numbers, no confidence manipulation, no unmeasured claims.
- Train/val/test kept strictly separate (SPLIT-109 signer-disjoint); no leakage. Backup model + dataset before any retraining or replacement (Task 7); never overwrite existing work without a recoverable backup.
- Architecture preserved: active model stays `SBAI-MDL-ISL-4.0.0` unless a Task 7 candidate strictly wins (rollback = re-activate 4.0.0).
- Suites after every task: backend → `py -3 -m pytest tests/ -q`; frontend → `npm test` and `npx tsc --noEmit`. All green before the next task. Complete suites again at the end.
- Python: `py -3`, NumPy only (no SciPy or new dependencies). Backend port 8000, JWT `change-me`.
- `models/SBAI-MDL-ISL-4.0.0/policy.json` is the single source of truth for thresholds; keep the legacy `threshold` key equal to `accept_threshold`; never touch registry top-level `model_id` or the registry `policy` field.
- Frontend contract: only `status === "recognized"` commits to sequence/speech. Provisional and Uncertain are display-only.
- WS persistence contract unchanged: only `Recognized` rows persist. REST keeps its existing unconditional logging (asymmetry is documented, not "fixed").

## Review Focus

1. **Mid-hold flicker** (one provisional/uncertain window inside a held sign) re-arms the commit gate and speaks the same gloss twice → Task 4 tests: `A→prov→A` yields exactly one commit; `A→soft→soft→A` yields two; `no-sign` arms in one window.
2. **Full-T rows over the legacy per-frame protocol** would fire a prediction from the *first* 45 rows (partial sign) and diverge from REST → Task 5: `recognizeFrames` must call `sendWindow` exactly once and never `sendFrame`; REST↔WS full-T parity test asserts identical class/status/confidence.
3. **Calibration invalidates thresholds fitted on raw confidences** (and the implicit 60% frontend floor interacts with them) → thresholds are fit in the same script run on calibrated VAL confs (Task 2); the user gate applies only when `sb_threshold` is explicitly set (Task 4); Task 6/8 verifies final val accepted-accuracy ≥ baseline.
4. **Provisional changes pinned status sets and persistence semantics** → Task 3 explicitly adapts `test_api_p4:30` tuple to `("recognized","provisional","uncertain")`, adds a WS test that provisional is *not* persisted, and pins REST provisional *is* persisted (pre-existing behavior).
5. **Blank/invalid input must short-circuit before any calibration/TTA model work** → Task 2 re-runs the energy-gate/no-sign tests after wiring; Task 5 keeps 422/413 envelope tests untouched and adds a `window` `INVALID_INPUT` test.

## File Structure

| Area | Files |
|---|---|
| Backend core | `backend/app/deps.py` (+`_calibration_path`, `get_calibration`, `calibrate_probs`, `decision_status`, `recognize_probs`, `recognize_probs_batch`, `make_windows`, `preprocess_window`), `backend/app/routers/predict.py`, `backend/app/routers/stream.py` |
| Model artifacts | `models/SBAI-MDL-ISL-4.0.0/policy.json`, `models/SBAI-MDL-ISL-4.0.0/calibration.json` (new) |
| Scripts | `scripts/eval_report.py` (new), `scripts/calibrate_v4.py` (new), `scripts/eval_webcam_sim.py` (+`--split`, switch to `recognize_probs`), `scripts/export_predictions.py` (new), `scripts/eval_webcam_report.py` (new), `scripts/train_v3.py` (+`--time-jitter`, conditional) |
| Frontend | `frontend/src/hands.ts` (+`buildFeatureRows`), `frontend/src/landmarks.ts`, `frontend/src/api/stream.ts` (+`sendWindow`), `frontend/src/api/client.ts` (+`"Provisional"`), `frontend/src/views/Live.tsx` (`resolveCommit`, `readThresholdGate`, `confidenceNote`, `toState`), `frontend/src/views/Settings.tsx` |
| Tests | `tests/test_class_mapping.py`, `tests/test_calibration.py`, `tests/test_decision_policy.py`, adaptations in `tests/test_api_p4.py`, `tests/test_ws.py`, `frontend/src/views/Live.test.tsx`, `frontend/src/api/stream.test.ts`, `frontend/src/hands.test.ts` |
| Docs/outputs | `Docs/M13_ACCURACY_CALIBRATION.md` (new report), `Docs/eval/*.json|txt|csv`, `Docs/eval/policy_4.0.0_original.json` (rollback record) |

## Spec Coverage

Phase 1 audit/trace → Task 1 (M13 skeleton) + M12; Phase 2 confidence investigation → Task 2 (reliability dump); Phase 3 calibration → Task 2; Phase 4 confidence gates/three states → Tasks 2–3; Phase 5 temporal consistency → Task 4; Phase 6 accuracy push → Tasks 5 + 7; Phase 7 evaluation → Tasks 1, 6, 8, 9; Phase 8 regression matrix (16 items) → Task 6; Phase 9 final report → Task 9.

---

### Task 1: Baseline harness, class-mapping pin, M13 skeleton

**Owner:** subagent (isolated: all new files). **Reviewer:** native.

**Files:**
- Create: `scripts/eval_report.py`
- Create: `tests/test_class_mapping.py`
- Create: `Docs/M13_ACCURACY_CALIBRATION.md`, `Docs/eval/` (output dir), `Docs/eval/policy_4.0.0_original.json`

**Interfaces:**
- Consumes: `deps.get_scaler() -> (mu, sd)`, `deps.infer_ensemble(batch) -> (k, C)`, `deps.get_policy() -> dict`, `deps.label_of`, `deps.class_list()`, `data/dataset/processed/tensors_109_real.npz` (`X (14826,45,189)`, `y 0..108`), `split_idx_109.npz` (`train/val/test`).
- Produces: CLI `py -3 scripts/eval_report.py --split {val,test} [--windows N] [--confusion] [--per-class] [--out PATH]`; JSON keys exactly: `split, n, temperature, tta_windows, thresholds:{accept,provisional}, argmax_accuracy, overall_accuracy, accepted_accuracy, coverage, false_accept_rate_overall, false_accept_rate_accepted, low_conf_correct_rate, macro_f1, ece, brier, latency_ms:{p50,p95}, counts:{recognized,provisional,uncertain,no_sign}`. Status in Task 1 computed inline as `conf >= policy.get("accept_threshold", policy.get("threshold", 0.4))` → recognized else uncertain (switches to `decision_status` in Task 3). Truth mapping pin: `class_id = f"ISL_{int(y)+1:03d}"` (same formula as `predict.py:114,117`).

- [ ] **Step 1: Write `tests/test_class_mapping.py` (characterization — expected PASS)**

```python
import csv
from app import deps

def test_class_map_sorted_and_aligned_with_label_of():
    with open("data/dataset/annotations/class_map.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    ids = [r["class_id"] for r in rows]
    assert ids == [f"ISL_{i+1:03d}" for i in range(len(ids))]
    for r in rows[::11]:
        assert deps.label_of(r["class_id"]) == r["label"]

def test_class_list_order_matches_sorted_map():
    ids = [c["class_id"] for c in deps.class_list()]
    assert ids == [f"ISL_{i+1:03d}" for i in range(len(ids))]
```

- [ ] **Step 2: Run** `py -3 -m pytest tests/test_class_mapping.py -q` — **Expected: PASS.** If it fails, the class mapping is broken: stop and report; do not continue.

- [ ] **Step 3: Write `Docs/eval/policy_4.0.0_original.json`** — copy `models/SBAI-MDL-ISL-4.0.0/policy.json` verbatim (rollback record; M13 references it).

- [ ] **Step 4: Implement `scripts/eval_report.py`** — load split indices, scale `X[idx]` with `deps.get_scaler()`, batch-probabilities in chunks of 512 via `deps.infer_ensemble(...)` (per-sample raw probs, no calibration yet — file absent), compute the pinned metric keys (ECE 15 equal-width bins over conf-vs-argmax-correct; multiclass Brier = mean of per-sample `sum_c (p_c - onehot_c)^2`; latency = per-row wall time over 200 sampled rows, p50/p95; `macro_f1` computed with a local `_macro_f1(y_true, y_pred)` — no sklearn). Add `--self-check`: first 200 rows must match a naive per-row `infer_ensemble` loop to `atol 1e-5`.

- [ ] **Step 5: Run baseline** `py -3 scripts/eval_report.py --split val --out Docs/eval/01_baseline_val.json --self-check` — Expected: self-check passes, `n == 2397`, `0.75 <= overall_accuracy <= 0.90`, counts sum to n, `macro_f1` recorded (Task 7 gate reference).

- [ ] **Step 6: Create `Docs/M13_ACCURACY_CALIBRATION.md` skeleton** — §11 headings (root causes, files-changed, baselines, final metrics, calibration, per-class, latency, tests, versions, limitations, run instructions, rollback), root-cause summary linked to M12, baseline val table pasted from Step 5, pipeline-trace section marked "(final design lands in Tasks 3–5)".

- [ ] **Step 7: Run** `py -3 -m pytest tests/ -q` — Expected: all green (unchanged code paths).

---

### Task 2: Temperature calibration + VAL-fitted thresholds + backend wiring

**Owner:** native (shared files: `deps.py`, `predict.py`, `stream.py`, `policy.json`).

**Files:**
- Modify: `backend/app/deps.py` (add after `get_policy`)
- Modify: `backend/app/routers/predict.py` (lines ~96–105)
- Modify: `backend/app/routers/stream.py` (lines ~105–121)
- Create: `scripts/calibrate_v4.py`
- Create: `models/SBAI-MDL-ISL-4.0.0/calibration.json` (script output)
- Modify: `models/SBAI-MDL-ISL-4.0.0/policy.json` (script output, merge-write preserving existing keys)
- Modify: `scripts/eval_report.py` and `scripts/eval_webcam_sim.py` (switch probability computation to `recognize_probs` / `recognize_probs_batch` so calibrated confs and thresholds stay consistent)
- Test: `tests/test_calibration.py`

**Interfaces:**
- Produces (exact signatures, all in `backend/app/deps.py`):
  - `def _calibration_path() -> Path` — `MODELS / model_version() / "calibration.json"`
  - `def get_calibration() -> dict` — mtime-cached like `get_policy`; missing file → `{"temperature": 1.0}`
  - `def calibrate_probs(probs: np.ndarray) -> np.ndarray` — softmax temperature along the last axis; `T == 1.0` → identity return
  - `def recognize_probs(seq_scaled: np.ndarray) -> np.ndarray` — `(45,189) → (C,)`: ensemble branch `calibrate_probs(infer_ensemble(seq[None])[0])`, else `calibrate_probs(get_model().predict(seq[None], verbose=0)[0])`
  - `def recognize_probs_batch(X_scaled: np.ndarray, chunk: int = 512) -> np.ndarray` — `(N,45,189) → (N,C)`, same semantics, row-equal to per-row calls
- `calibration.json` schema: `{model_id, temperature, fitted_on: "val", val_nll, val_ece_before, val_ece_after, val_brier_before, val_brier_after, fit_rejected: bool, created}`
- `policy.json` new keys: `accept_threshold`, `provisional_threshold`, `tta_windows: 1`, `val_accepted_accuracy`, `val_coverage`, `updated_by: "calibrate_v4"`; `threshold` set equal to `accept_threshold`.

- [ ] **Step 1: Write failing tests in `tests/test_calibration.py`**

```python
def test_get_calibration_defaults_to_identity(monkeypatch, tmp_path):
    monkeypatch.setattr("app.deps._calibration_path", lambda: tmp_path / "missing.json")
    from app import deps
    assert deps.get_calibration() == {"temperature": 1.0}

def test_calibrate_probs_identity_and_flattening(monkeypatch, tmp_path):
    # identity at T=1, flattening + row-sum 1 at T>1
    p = np.array([0.8, 0.1, 0.1], dtype=np.float32)
    assert np.allclose(deps.calibrate_probs(p), p)
    monkeypatch.setattr(deps, "get_calibration", lambda: {"temperature": 2.0})
    q = deps.calibrate_probs(p)
    assert q.max() < 0.8 and np.isclose(q.sum(), 1.0)

def test_recognize_probs_batch_matches_single_rows():
    X = np.random.default_rng(0).normal(0, 0.5, (6, 45, 189)).astype("float32")
    batch = deps.recognize_probs_batch(X)
    rows = np.stack([deps.recognize_probs(x) for x in X])
    assert np.allclose(batch, rows, atol=1e-6)
```

- [ ] **Step 2: Run** `py -3 -m pytest tests/test_calibration.py -q` — Expected: FAIL (`AttributeError: _calibration_path`).

- [ ] **Step 3: Implement the four deps functions** exactly per Interfaces (mtime cache mirrors `_read_policy_cached`/`get_policy` at `deps.py:210–229`; temperature math: `logp = log(clip(p,1e-12,1))/T; e = exp(logp - max); return e/e.sum(-1, keepdims)`).

- [ ] **Step 4: Run tests → PASS**, then wire callers: `predict.py` inference block → `probs = await asyncio.to_thread(recognize_probs, normed)` (keep `run_inference` + `calibrate_probs(...)` in the non-ensemble else-branch); `stream.py` ensemble branch → `recognize_probs`, else-branch keeps `run_stream_inference` wrapped in `calibrate_probs` (the symbol must remain — `test_ws.py:141` patches it). Status lines unchanged (still `threshold`-based; Task 3 replaces them).

- [ ] **Step 5: Switch `scripts/eval_report.py` and `scripts/eval_webcam_sim.py`** to `deps.recognize_probs_batch` / `deps.recognize_probs` so all harness numbers flow through calibration once it exists.

- [ ] **Step 6: Run** `py -3 -m pytest tests/test_api_p4.py -q` (covers `status == "no-sign"` at line 202 and 422/413 envelopes) — Expected: PASS proves the energy gate still fires before any calibrated/TTA model work.

- [ ] **Step 7: Implement `scripts/calibrate_v4.py`** (asserts `deps.uses_ensemble()`):
  1. probs_raw on val via `infer_ensemble` on scaled `X[val]` (chunked); `ci = argmax`, `conf = max`.
  2. Temperature: grid `T ∈ exp(linspace(log 0.25, log 4.0, 151))`, minimize NLL of `y_val` under temperature-scaled probs; if `val_ece_after >= val_ece_before` → write `temperature = 1.0`, `fit_rejected = True`.
  3. Thresholds from **calibrated** val confs: `t_accept = min t ∈ {0.00…0.99 step 0.01} with precision(conf≥t) ≥ 0.90`, else `0.99`; `t_prov = min t with precision ≥ 0.80`, else `max(t_accept − 0.10, 0)`; clamp `t_prov = max(min(t_prov, t_accept − 0.01), 0)`.
  4. Merge-write `policy.json` (preserve `smoothing_window` etc.; set `threshold = accept_threshold`, `tta_windows = 1`); write `calibration.json`; print before/after ECE/Brier + chosen thresholds.
  Runtime expectation: ~2–4 min for 2397 ensemble rows.

- [ ] **Step 8: Run** `py -3 scripts/calibrate_v4.py` — Expected: prints val ECE improvement or `fit_rejected`, thresholds in band `0 ≤ t_prov < t_accept ≤ 0.99`.

- [ ] **Step 9: Verify artifacts** — `py -3 -c "import json; print(json.load(open('models/SBAI-MDL-ISL-4.0.0/calibration.json'))['temperature'], json.load(open('models/SBAI-MDL-ISL-4.0.0/policy.json')))"` — Expected: temperature present; policy contains `accept_threshold`, `provisional_threshold`, `tta_windows == 1`, `threshold == accept_threshold`.

- [ ] **Step 10: Run** `py -3 -m pytest tests/ -q` — Expected: all green (statuses still in the two-state set; conf shifts must not break any assertion).

---

### Task 3: Three-state decision policy (backend + frontend display)

**Owner:** native (shared files: `deps.py`, `predict.py`, `stream.py`, `Live.tsx`, `client.ts`).

**Files:**
- Modify: `backend/app/deps.py` (+`decision_status`), `backend/app/routers/predict.py:109`, `backend/app/routers/stream.py:124`
- Modify: `frontend/src/api/client.ts:71` (`RecState`), `frontend/src/views/Live.tsx` (`toState` at 85, `confidenceNote` new export, `applyPrediction` notes at 396–408)
- Modify: `scripts/eval_report.py` (decision line → `deps.decision_status`; provisional now counted)
- Test: `tests/test_decision_policy.py` (new), `tests/test_api_p4.py:30`, `tests/test_ws.py` (+2 tests), `frontend/src/views/Live.test.tsx`

**Interfaces:**
- Produces: `def decision_status(conf: float, policy: dict) -> str` — `acc = float(policy.get("accept_threshold", policy.get("threshold", 0.4)))`; `prov = min(float(policy.get("provisional_threshold", acc)), acc)`; `conf >= acc → "recognized"`, `conf >= prov → "provisional"`, else `"uncertain"`. REST returns lowercase; WS sends `decision_status(...).capitalize()` (`"Provisional"`).
- Frontend: `RecState` gains `| "Provisional"`; `toState("provisional") → "Provisional"`; `export function confidenceNote(status: string, confidence: number): string | null` — provisional: `` `Provisional (${(confidence*100).toFixed(1)}%) — plausible, needs more evidence. Not added to your sequence.` ``; any other non-recognized status: existing `Low confidence (...) — shown as Uncertain, not definitive.`; recognized → `null`.

- [ ] **Step 1: Write failing `tests/test_decision_policy.py`**

```python
def test_boundaries_inclusive():
    pol = {"accept_threshold": 0.6, "provisional_threshold": 0.3}
    assert deps.decision_status(0.6, pol) == "recognized"
    assert deps.decision_status(0.3, pol) == "provisional"
    assert deps.decision_status(0.2999, pol) == "uncertain"

def test_missing_keys_stay_two_state():
    assert deps.decision_status(0.5, {"threshold": 0.4}) == "recognized"
    assert deps.decision_status(0.39, {"threshold": 0.4}) == "uncertain"
    # provisional collapses onto accept when absent -> no provisional band
    pol = {"accept_threshold": 0.6}
    assert deps.decision_status(0.5, pol) == "uncertain"

def test_live_policy_shape():
    pol = deps.get_policy()
    assert pol["threshold"] == pol["accept_threshold"]
    assert 0 <= pol["provisional_threshold"] <= pol["accept_threshold"] <= 1
```

- [ ] **Step 2: Run → FAIL** (`decision_status` undefined).

- [ ] **Step 3: Implement `decision_status` in `deps.py`; switch `predict.py:109` → `status = decision_status(conf, policy)`; `stream.py:124` → `state = decision_status(conf, policy).capitalize()`; switch `eval_report.py` decision line to `deps.decision_status`.

- [ ] **Step 4: Adapt pinned tests:** `tests/test_api_p4.py:30` → `assert b["status"] in ("recognized", "provisional", "uncertain")`.

- [ ] **Step 5: Run** `py -3 -m pytest tests/test_decision_policy.py tests/test_api_p4.py -q` — Expected: PASS.

- [ ] **Step 6: Add WS tests to `tests/test_ws.py`** (reuse the `monkeypatch` fake-probs pattern from `test_ws_recognized_persists`):
  - *Provisional not persisted:* fake one-hot with value `v` chosen from `linspace(0.5, 0.99, 60)` such that `deps.calibrate_probs(fake)[0]` lands in `[prov, acc)` (skip with `pytest.skip("no provisional band")` if `prov >= acc`); assert WS `state == "Provisional"`, history row count unchanged; compute expected via `deps.decision_status(deps.calibrate_probs(fake)[0], deps.get_policy())` and assert the socket matched it.
  - *REST↔WS parity (45 rows):* same rng frames → `POST /api/v1/predict` vs WS frame stream → `rest["status"] == ws["state"].lower()` and `rest["prediction"]["class_id"] == ws["prediction"]["class_id"]` and equal confidences (both round 4).

- [ ] **Step 7: Run** `py -3 -m pytest tests/ -q` — Expected: all green.

- [ ] **Step 8: Frontend:** add `"Provisional"` to `RecState`; `toState` explicit provisional branch; add `confidenceNote`; `applyPrediction` uses it for non-recognized statuses (below-user-gate branch at 396–400 unchanged).

- [ ] **Step 9: Frontend tests in `Live.test.tsx`:** `expect(toState("provisional", true)).toBe("Provisional")`, `expect(toState("Provisional", true)).toBe("Provisional")`, confidenceNote provisional/uncertain/recognized cases.

- [ ] **Step 10: Run** `npm test` and `npx tsc --noEmit` — Expected: all green.

---

### Task 4: Flicker-safe re-arm + explicit-user-gate-only thresholding

**Owner:** native (shared files: `Live.tsx`, `Settings.tsx`).

**Files:**
- Modify: `frontend/src/views/Live.tsx` (`CommitInput` 99, `resolveCommit` 119, `applyPrediction` 374–425, `startSingle` ~526, continuous attempt start ~574, export `readThresholdGate`)
- Modify: `frontend/src/views/Settings.tsx` (line 126 removal, gate-state + copy 385–387)
- Test: `frontend/src/views/Live.test.tsx`

**Interfaces:**
- `CommitInput` gains `streak?: number` (default `0`) and `hardRelease?: boolean` (default `false`); `CommitDecision` unchanged.
- `export const RELEASE_WINDOWS = 2`.
- `resolveCommit` non-accepted branch becomes: `{commit: false, armed: input.armed || hardRelease || streak >= RELEASE_WINDOWS, lastLabel: input.lastLabel}` (accepted branches unchanged).
- `export function readThresholdGate(): number | null` — parse `sb_threshold` from localStorage; missing/NaN → `null`.
- `applyPrediction`: `const gate = readThresholdGate(); const meetsThreshold = gate === null || p.confidence >= gate / 100;` — below-gate note only when `gate !== null`. Maintains `releaseStreakRef = useRef(0)`; each prediction: `releaseStreakRef.current = accepted ? 0 : releaseStreakRef.current + 1`; passes `streak` and `hardRelease: status.toLowerCase() === "no-sign"` to `resolveCommit`; resets `releaseStreakRef.current = 0` wherever `freshAttemptRef` is set to `true` (line ~526) and at continuous attempt start (~574).

- [ ] **Step 1: Update the existing release test + add failing flicker tests in `Live.test.tsx`**

```tsx
// updated: release test now pins hardRelease semantics
const released = resolveCommit({ accepted: false, label: "NO SIGN DETECTED",
  lastLabel: "HELLO", armed: false, freshAttempt: false, hardRelease: true });
expect(released.armed).toBe(true);

// new: single soft window does NOT re-arm
expect(resolveCommit({ ...base, accepted: false, armed: false, streak: 1 }).armed).toBe(false);
// new: two consecutive soft windows re-arm
expect(resolveCommit({ ...base, accepted: false, armed: false, streak: 2 }).armed).toBe(true);

// new: flicker sequence commits exactly once
const r1 = resolveCommit({ ...base, accepted: true });            // commit, armed false
const r2 = resolveCommit({ ...base, accepted: false, armed: r1.armed, streak: 1 });
const r3 = resolveCommit({ ...base, accepted: true, armed: r2.armed }); // held same label -> no commit
expect(r1.commit).toBe(true); expect(r2.armed).toBe(false); expect(r3.commit).toBe(false);
```

Plus `readThresholdGate` tests: unset → `null`; `"75"` → `75`.

- [ ] **Step 2: Run → FAIL** (streak/hardRelease unknown fields).

- [ ] **Step 3: Implement** per Interfaces (`RELEASE_WINDOWS`, `resolveCommit` branch, `readThresholdGate`, `releaseStreakRef` wiring, gate-only-when-set, streak resets).

- [ ] **Step 4: Settings.tsx** — remove `localStorage.setItem("sb_threshold", ...)` from `handleSaveToken` (line 126; slider `onChange` already persists on touch); add `manualGate` state initialized from `localStorage.getItem("sb_threshold") !== null`; helper copy when `!manualGate`: `Automatic mode: backend-calibrated thresholds decide acceptance. Move the slider to set a manual override.`; existing copy when manual.

- [ ] **Step 5: Run** `npm test` and `npx tsc --noEmit` — Expected: all green (38+ tests).

- [ ] **Step 6: Sanity:** grep confirms no other `sb_threshold` read uses the default-60 path (`Live.tsx:382–389` replaced; `DEFAULT_THRESHOLD_PERCENT` kept as Settings UI default + its test at `Live.test.tsx:192` untouched).

---

### Task 5: Full-T capture rows + WS `window` message + TTA (VAL-gated)

**Owner:** native (shared files: backend routers + frontend stream/Live/landmarks).

**Files:**
- Modify: `frontend/src/hands.ts` (+`buildFeatureRows`), `frontend/src/landmarks.ts:233`, `frontend/src/api/stream.ts` (+`sendWindow`), `frontend/src/views/Live.tsx:234` (+doc comment 152–154)
- Modify: `backend/app/deps.py` (+`preprocess_window`, `make_windows`; extend `recognize_probs`/`recognize_probs_batch` with `windows: int = 1`), `backend/app/routers/predict.py` (use `preprocess_window` + pass `tta_windows`), `backend/app/routers/stream.py` (+`_predict_payload`, `window` message branch)
- Test: `frontend/src/hands.test.ts`, `frontend/src/api/stream.test.ts`, `frontend/src/views/Live.test.tsx`, `tests/test_ws.py`, `tests/test_api_p4.py` (unchanged envelope asserts)

**Interfaces:**
- `export function buildFeatureRows(frames: Frames): number[][]` = `frameFeatures(normalize(canonicalize(frames)))` — `(T,189)`, no subsample. `capture()` returns it (was `buildSequence(raw)`).
- `sendWindow: (frames: number[][]) => void` on the `connectStream` handle → `{"type":"window","frames":...}` (queued while CONNECTING via existing `sendRaw`).
- `def preprocess_window(frames: np.ndarray) -> np.ndarray | None` — resample/pad exactly as `predict.py:71–75`, energy gate (pre-norm, `NOSIGN_ENERGY`) → `None`, else scaled `(45,189)` float32. Callers keep their own 422/413 checks.
- `def make_windows(seq_scaled: np.ndarray, k: int) -> np.ndarray` — `k ∉ {1,3} → 1`; `k=1 → seq[None]`; `k=3` → crops `arr[0:45]`, `arr[0:39]`, `arr[6:45]`, each resampled to 45 via `linspace` over its own length → `(3,45,189)`.
- `recognize_probs(seq_scaled, windows: int = 1)` / `recognize_probs_batch(X, windows: int = 1)` — mean raw probs over windows, then `calibrate_probs` once (k=1 numerically identical to Task 2 behavior).
- WS `"window"` handler: validate `1 ≤ len ≤ 600` rows × `FEAT_DIM` else the existing `INVALID_INPUT` error shape; `buf = rows`; bypass the 500 ms throttle (infer immediately); persistence rule identical to frame path.
- `async def _predict_payload(window_raw: np.ndarray, session_id: str) -> tuple[dict, str, str]` — returns `(message payload, state, class_id)`; no-sign short-circuit included; used by BOTH frame and window branches (behavior-identical refactor guarded by existing `test_ws.py`).
- `predict.py` reads `tta = int(get_policy().get("tta_windows", 1))` and passes it.

- [ ] **Step 1: Frontend tests (failing):** `hands.test.ts` — for a `T=45` fixture, `expect(buildSequence(f)).toEqual(toSequence(buildFeatureRows(f)).seq)`; `stream.test.ts` — `sendWindow` queues while CONNECTING and flushes on open (mirror the `sendFrame` test at line 61); `Live.test.tsx` — replace `expect(sendFrame).toHaveBeenCalledTimes(FRAMES.length)` (line 97) with `expect(sendWindow).toHaveBeenCalledTimes(1); expect(sendWindow).toHaveBeenCalledWith(FRAMES); expect(sendFrame).not.toHaveBeenCalled()` and add `sendWindow: vi.fn()` to both mock handles (lines 66–75, 108–117).

- [ ] **Step 2: Run → FAIL**, then implement `buildFeatureRows`, `sendWindow`, `recognizeFrames` single-`sendWindow` call (+ doc comment). Audit `frontend/src/landmarks.test.ts` for `45`-row assertions on capture output and update them to `>= MIN_CAPTURE_FRAMES` rows of length 189.

- [ ] **Step 3: Run** `npm test` and `npx tsc --noEmit` — Expected: green.

- [ ] **Step 4: Backend: write failing tests** — `test_ws.py`: `window` message with `(105,189)` rng rows → prediction arrives, state in allowed set; `window` with 601 rows / wrong row width → `INVALID_INPUT`; REST↔WS **full-T parity**: same 105-row input via `POST /api/v1/predict` vs `{"type":"window"}` → equal `class_id`, `status == state.lower()`, equal rounded conf.

- [ ] **Step 5: Run → FAIL**, then implement: `preprocess_window`, `make_windows`, windows-aware `recognize_probs(_batch)`; refactor `predict.py` post-envelope logic onto `preprocess_window` (422/413/404 responses byte-identical); extract `_predict_payload` in `stream.py`, add the `window` branch per Interfaces; pass `tta_windows` policy value in both routers.

- [ ] **Step 6: Run** `py -3 -m pytest tests/ -q` — Expected: all green (existing envelope + frame-path tests are the refactor guard).

- [ ] **Step 7: TTA gate measurement (VAL only):**
  `py -3 scripts/eval_report.py --split val --windows 1 --out Docs/eval/05_val_w1.json`
  `py -3 scripts/eval_report.py --split val --windows 3 --out Docs/eval/05_val_w3.json`
  Gate: adopt `windows=3` only if `overall_accuracy(w3) − overall_accuracy(w1) ≥ 0.010` **and** `w3 latency p95 ≤ 300 ms`.

- [ ] **Step 8: Apply gate** — set `tta_windows` in `models/SBAI-MDL-ISL-4.0.0/policy.json` to `3` or leave `1`; re-run one `POST /api/v1/predict` (or `test_api_p4` subset) to confirm the mtime-cached policy picked it up; record decision + numbers for M13.

---

### Task 6: Webcam-replay val split + §9 regression matrix audit

**Owner:** subagent (isolated: `scripts/eval_webcam_sim.py` + matrix content delivered as an M13 section patch proposal + gap-test suggestions). Shared doc edits (`M13`) and shared test files reviewed/applied by native if they overlap with active tasks — run after Tasks 2–5 are integrated (policy final). **Reviewer:** native.

**Files:**
- Modify: `scripts/eval_webcam_sim.py` (+`--split`)
- Modify: `Docs/M13_ACCURACY_CALIBRATION.md` (+matrix) — native applies if conflicts
- Test: gaps found by the audit (expected home: `tests/test_model_300.py` or `tests/test_calibration.py`)

**Interfaces:**
- Consumes: policy `accept_threshold` from Task 2; baseline JSONs from Task 1.

- [ ] **Step 1:** `P.add_argument("--split", choices=["val", "test"], default="test")`; replace `te = S["test"]` with `idx_split = S[a.split]` (default preserves M12 repro commands); update docstring.

- [ ] **Step 2: Run val replay:** `py -3 scripts/eval_webcam_sim.py --split val --thr (accept_threshold) | Tee-Object Docs/eval/06_webcamsim_val.txt` — Expected: all four conditions printed (val pool; NOT the test pool).

- [ ] **Step 3: Build the §9 16-item matrix** — each item → concrete test file::name, or an explicit "covered by eval harness / manual protocol" row with reason. Verify each claimed test actually exists (`py -3 -m pytest <file> -q` or grep).

- [ ] **Step 4: Fill gaps** (anticipated): `test_infer_ensemble_is_probability_distribution` — batch of 2 → shape `(2,109)`, rows sum to 1 ± 1e-5, all ≥ 0; any missing provisional-display assertions from §9.15; anything else Step 3 flags that is offline-testable.

- [ ] **Step 5: Run** `py -3 -m pytest tests/ -q` + `npm test` + `npx tsc --noEmit` — Expected: all green.

---

### Task 7: Conditional accuracy push (retrain 4.1.0) — evidence-gated

**Owner:** subagent if triggered (isolated: `scripts/train_v3.py` + model output dirs); native performs backup verification, promotion decision, and registry/promotion changes (shared).

**Files:**
- Modify (only if triggered): `scripts/train_v3.py` (+`--time-jitter`)
- Registry/model dirs only on promotion; rollback record in M13.

- [ ] **Step 0: BACKUP (mandatory before any training output can collide with existing work):** copy `models/SBAI-MDL-ISL-4.0.0/` → `models/_backup_4.0.0_pretrain/` (weights + policy + scaler + calibration if present); copy `data/dataset/processed/` (tensors/split/scaler npz) → `data/dataset/_backup_pretrain/`; record backup paths in M13. Never overwrite existing artifacts.

- [ ] **Step 1: Read the gate** from `Docs/eval/06_webcamsim_val.txt`: if `idle_realistic` visible accuracy (correct-and-accepted / n) at `accept_threshold` **≥ 0.80** → **SKIP**: write "retrain skipped — offline proxy ≥ 0.80 (source: h5-webcam-replay val)" into M13 and stop.

- [ ] **Step 2 (if triggered):** add `--time-jitter` to `train_v3.py`'s `AugSequence`: per-sample circular roll along the time axis by `r ∈ [−4, 4]` (uniform), applied before the existing mirror/scale/shift/noise/drop aug; val/test never augmented (existing invariant).

- [ ] **Step 3:** `py -3 scripts/train_v3.py --mode smoke --arch gru --tag 109_real ...` first (validates pipeline, ~5 epochs), then `--mode full --arch gru --tag 109_real --model-id SBAI-MDL-ISL-4.1.0 --exp <next EXP id>`; capture printed `val_macro_f1` / `val_acc`.

- [ ] **Step 4: Promotion gate** — candidate `val_macro_f1` **and** val argmax accuracy must both exceed the Task 1 baseline for 4.0.0. If not → discard, record numbers, done.

- [ ] **Step 5 (if promoted):** activate 4.1.0 through the same mechanism that made 4.0.0 active (inspect `backend/app/routers/admin.py` / scripts for `active_model`; registry `policy` field and top-level `model_id` conventions preserved), then **re-run `py -3 scripts/calibrate_v4.py`** (temperature + thresholds refit into `models/SBAI-MDL-ISL-4.1.0/`), then `py -3 -m pytest tests/ -q`.

- [ ] **Step 6: Rollback proof** — document in M13: re-activate `SBAI-MDL-ISL-4.0.0` via the same mechanism + rerun `calibrate_v4`; suites must be green either way.

---

### Task 8: Final evaluation — TEST touched exactly once

**Owner:** native (integration).

**Files:**
- Create: `Docs/eval/08_final_val.json`, `Docs/eval/08_final_test.json`, `Docs/eval/08_webcamsim_test.txt`, `Docs/eval/08_confusion_test.csv`, `Docs/eval/08_per_class_test.csv`
- Modify: `Docs/M13_ACCURACY_CALIBRATION.md`

- [ ] **Step 1:** `py -3 scripts/eval_report.py --split val --out Docs/eval/08_final_val.json --confusion --per-class`

- [ ] **Step 2 (THE single test touch):** `py -3 scripts/eval_report.py --split test --out Docs/eval/08_final_test.json --confusion --per-class`

- [ ] **Step 3:** `py -3 scripts/eval_webcam_sim.py --split test --thr (accept_threshold) | Tee-Object Docs/eval/08_webcamsim_test.txt`

- [ ] **Step 4: Fill M13 metrics sections** — overall / accepted / coverage / false-accept (both definitions) / low-conf-correct rate **baseline vs final** (from `01_*` vs `08_*`), ECE + Brier before/after, calibration temperature, thresholds, per-class + confusion CSV references, latency before (`p50 64.4 ms`, M11) vs after (p50/p95 incl. TTA), `tta_windows` decision, versions (`4.0.0` or `4.1.0`, `tensors_109_real`, `SPLIT-109 8800/2397/3629`, `class_map.csv` 109), and suite results (`py -3 -m pytest tests/ -q`, `npm test`, `npx tsc --noEmit` outputs pasted).

- [ ] **Step 5: Run all three suites** one final time — Expected: all green; paste counts into M13.

---

### Task 9: Webcam manual protocol + export/report scripts + M13 completion

**Owner:** subagent for new scripts + template (isolated new files); native owns M13 final assembly (shared doc). **Reviewer:** native.

**Files:**
- Create: `scripts/export_predictions.py`, `scripts/eval_webcam_report.py`, `Docs/eval/webcam_truth_template.csv`, `tests/test_export_predictions.py`
- Modify: `Docs/M13_ACCURACY_CALIBRATION.md` (complete), `Docs/M12_WEBCAM_ACCURACY.md` (one cross-ref line to M13)

**Interfaces:**
- `py -3 scripts/export_predictions.py --session <sid> --out preds.csv` — reads `app.models.Prediction` rows (`session_id`, `class_id`, `confidence`, `model_id`, `created_at` as defined there).
- Truth CSV columns (pinned): `attempt_id, expected_class_id, displayed_label, displayed_state, displayed_conf, flips_in_attempt, notes`.
- `py -3 scripts/eval_webcam_report.py --truth truth.csv --out report.json` → metrics: `overall_accuracy` (correct & displayed_state==recognized / n), `accepted_accuracy`, `coverage`, per-class table, `flip_rate`; excludes rows with `notes == invalid` (counted separately).

- [ ] **Step 1: Implement export + test** — `tests/test_export_predictions.py`: create session (REST), `POST /api/v1/predict` with that session (REST persists unconditionally), run export → CSV contains the row.

- [ ] **Step 2: Implement `eval_webcam_report.py` + truth template CSV** (headers per Interfaces).

- [ ] **Step 3: Write the manual protocol into M13** — choose 20 signs = top-10 confusable pairs from `08_confusion_test.csv` + 10 random; 4 attempts each (80 total) in Single mode; plus held-sign ≥ 8 s repeat test, deliberate same-sign repeat ×3, one 5-sign sentence in Continuous mode; record every attempt row (displayed values transcribed from screen, including rejections); run the report script; paste results labeled `webcam-protocol (user-run, manual)`.

- [ ] **Step 4: Complete M13 §11** — root causes (+ new: uncalibrated softmax, dual gate, single-45 partial window), files-changed-and-why (from `git diff --stat` + prose — no commits), baseline real-time (**user-reported** 22–32% → 42–50% after the shipped capture fixes) vs offline proxies vs final numbers, limitations (offline ≠ webcam, no camera in this environment, REST/WS history asymmetry, provisional never committed, protocol is manual), run instructions (exact commands for every script/suite), rollback (`Docs/eval/policy_4.0.0_original.json` restore + delete `calibration.json` → T=1 identity + registry re-activate 4.0.0).

- [ ] **Step 5: Final verification** — `py -3 -m pytest tests/ -q`, `npm test`, `npx tsc --noEmit` all green; M13 states only measured numbers.
