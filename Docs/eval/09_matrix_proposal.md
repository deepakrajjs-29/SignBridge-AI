# M13 §9 — Accuracy Regression Matrix (16 items) — PROPOSAL for native lead

Status: **proposal** — for the native lead to paste/apply as `Docs/M13_ACCURACY_CALIBRATION.md` §9
(subagent Task 6 may not edit M13 directly).

Provenance note: `Docs/M13_ACCURACY_CALIBRATION.md` currently has no §9 regression-matrix list
(§9 is "Versions"); the plan's Spec Coverage line pins "Phase 8 regression matrix (16 items) → Task 6".
The 16 items below are therefore reconstructed **1:1 from the plan's pinned accuracy/calibration
requirements** (`Docs/plans/2026-10-19-realtime-accuracy-calibration.md` — Global Constraints,
Review Focus, Task Interfaces/Steps; §9.15 numbering matches the plan's Task 6 Step 4 reference to
"provisional-display assertions from §9.15"). Every claimed test was verified by name in `tests/`
(or `frontend/src/`) AND run green (`py -3 -m pytest <file> -q`, or `npm test` for frontend files).

## Matrix

| # | Item | Coverage | Verification note |
|---|---|---|---|
| 9.1 | Class-mapping pin: `class_id = ISL_{y+1:03d}` order ↔ `label_of` ↔ `class_map.csv` (truth mapping used by `predict.py`) | `tests/test_class_mapping.py::test_class_map_sorted_and_aligned_with_label_of`, `tests/test_class_mapping.py::test_class_list_order_matches_sorted_map` | `py -3 -m pytest tests/test_class_mapping.py -q` → 2 passed |
| 9.2 | Split integrity: SPLIT-109 signer-disjoint, nominal 70/15/15, shapes (8800/2397/3629) — no leakage | `tests/test_split_v2.py::test_split_v2_signer_disjoint_and_shape`, `tests/test_split_v2.py::test_split_v2_ratios_nominal_70_15_15` | `py -3 -m pytest tests/test_split_v2.py -q` → 2 passed |
| 9.3 | VAL baseline harness: pinned metric keys (argmax/overall/accepted/coverage/FAR/low-conf-correct/macro-F1/ECE/Brier/latency/counts) + self-check vs naive per-row `infer_ensemble` (atol 1e-5) | eval harness — `py -3 scripts/eval_report.py --split val --self-check` → `Docs/eval/01_baseline_val.json` | Harness artifact exists: n=2397, argmax 0.833125, self-check passed (M13 §3). VAL-only; TEST arm is Task 8's single touch |
| 9.4 | Ensemble output is a probability distribution: shape `(N,109)`, rows sum to 1, all ≥ 0 | `tests/test_ensemble400.py::test_ensemble_proba_shape_and_mass` (N=1) **+ filled by this task:** `tests/test_model_300.py::test_infer_ensemble_is_probability_distribution` (N=2) | `pytest tests/test_ensemble400.py -q` → 3 passed; `pytest tests/test_model_300.py -q` → 4 passed (new test included) |
| 9.5 | Calibration primitives: missing `calibration.json` → identity `{"temperature": 1.0}`; T=1 identity; T>1 flattening + row-sum 1; `recognize_probs_batch` ≡ per-row (atol 1e-4) and non-negative | `tests/test_calibration.py::test_get_calibration_defaults_to_identity`, `::test_calibrate_probs_identity_and_flattening`, `::test_recognize_probs_batch_matches_single_rows`, **+ new:** `::test_recognize_probs_batch_rows_are_non_negative` | `py -3 -m pytest tests/test_calibration.py -q` → 6 passed (all tests in file, incl. new) |
| 9.6 | Live policy shape: `threshold == accept_threshold` (= 0.57), `0 ≤ provisional (0.00) ≤ accept ≤ 1`, `tta_windows` in supported set | `tests/test_decision_policy.py::test_live_policy_shape` **+ filled by this task:** `tests/test_calibration.py::test_live_policy_tta_windows_supported` | `pytest tests/test_decision_policy.py -q` → 3 passed; `pytest tests/test_calibration.py -q` → 6 passed |
| 9.7 | Three-state decision boundaries inclusive; missing policy keys collapse to legacy two-state | `tests/test_decision_policy.py::test_boundaries_inclusive`, `tests/test_decision_policy.py::test_missing_keys_stay_two_state` | `py -3 -m pytest tests/test_decision_policy.py -q` → 3 passed |
| 9.8 | TTA window plumbing: `make_windows` returns `(1,45,189)` for k∉{3}, `(3,45,189)` for k=3, finite output | eval harness/manual + **filled by this task:** `tests/test_calibration.py::test_make_windows_contract` | No pre-existing unit test covered `make_windows`; new test green in the 6-passed run of `tests/test_calibration.py`. TTA gate numbers themselves are harness-measured (`Docs/eval/05_val_w1.json` / `05_val_w3.json`) |
| 9.9 | REST three-state status set `{recognized, provisional, uncertain}`; blank input short-circuits to `no-sign` before model work; 422/413/404 envelopes preserved | `tests/test_api_p4.py::test_predict_200_and_alias` (status tuple at :30), `tests/test_api_p4.py::test_blank_frames_yield_no_sign`, `tests/test_api_p4.py::test_predict_422_dim_and_413` | `py -3 -m pytest tests/test_api_p4.py -q` → 31 passed |
| 9.10 | Persistence asymmetry: WS provisional is NOT persisted; REST persists unconditionally (pinned, documented) | `tests/test_ws.py::test_ws_provisional_not_persisted` (WS side); `tests/test_history.py::test_predict_with_session_logs_and_history_reads` (REST side) | `pytest tests/test_ws.py -q` → 14 passed; `pytest tests/test_history.py -q` → 6 passed |
| 9.11 | REST↔WS parity: same input → equal `class_id`, equal status, equal rounded confidence — 45-row frame path and 105-row full-T `window` path | `tests/test_ws.py::test_rest_ws_parity_45_rows`, `tests/test_ws.py::test_rest_ws_full_t_parity_105_rows` | Both in the 14-passed run of `tests/test_ws.py` |
| 9.12 | WS `window` message: full-T prediction arrives; `1..600` row validation else `INVALID_INPUT` | `tests/test_ws.py::test_ws_window_full_t_prediction`, `tests/test_ws.py::test_ws_window_invalid_input` | Both in the 14-passed run of `tests/test_ws.py` |
| 9.13 | Full-T capture path: `buildFeatureRows` = full-T features (no subsample), `recognizeFrames` calls `sendWindow` exactly once and never `sendFrame`; `sendWindow` queues while CONNECTING | frontend: `src/hands.test.ts` ("T=45: full-T buildFeatureRows IS the model window"), `src/api/stream.test.ts` ("sendWindow before open queues and flushes on open…"), `src/views/Live.test.tsx` ("stream prediction wins and REST predict is never called") | Names grep-verified in `frontend/src`; `npm test` → **48 passed (8 files)**; frontend files are native-lead-owned (not edited by this task) |
| 9.14 | Flicker-safe commit: A→soft→A commits exactly once; two consecutive soft windows re-arm; no-sign hard-release arms in one window | frontend: `src/views/Live.test.tsx` ("flicker sequence A -> soft -> A commits exactly once", "A -> soft -> soft -> A commits twice", "a single soft window does NOT re-arm", "two consecutive soft windows re-arm", "no-sign arms in one window") | Names grep-verified; covered by the 19-test `Live.test.tsx` inside `npm test` → 48 passed |
| 9.15 | Provisional display: `toState("provisional"/"Provisional") → "Provisional"`; `confidenceNote` provisional copy (`Provisional (x.x%) — plausible, needs more evidence…`); explicit-user-gate-only (`readThresholdGate` null / 75 / garbage) | frontend: `src/views/Live.test.tsx` ("toState maps provisional (REST lowercase and WS capitalized)", "confidenceNote distinguishes provisional, uncertain, recognized", "unset -> null; explicit value -> percent; garbage -> null") | Assertions exist exactly as the plan's Task 3 Step 9 pinned them; inside `npm test` → 48 passed |
| 9.16 | Accuracy gates & end-to-end metrics: VAL argmax 0.8331 / accept-0.57 overall 0.7409 / accepted 0.9034 / coverage 0.8202 baselines; TTA gate (Δoverall ≥ +0.010 AND w3 p95 ≤ 300 ms, both failed → stays 1); h5-webcam-replay VAL retrain gate (`idle_realistic` visible ≥ 0.80 at accept threshold); final TEST eval + manual webcam protocol | eval harness + manual: `Docs/eval/01_baseline_val.json`, `Docs/eval/05_val_w1.json`, `Docs/eval/05_val_w3.json`, **new:** `Docs/eval/06_webcamsim_val.txt` (`py -3 scripts/eval_webcam_sim.py --split val --thr 0.57`), Task 8 `08_*` finals, Task 9 manual protocol (20 signs × 4 attempts + held-sign/repeat/sentence) | VAL numbers above are recorded artifacts; webcam-replay VAL run completed by this task (see `06_webcamsim_val.txt`); TEST arms deliberately NOT run here (Task 8 single touch); manual protocol = Task 9 (needs camera, native/user) |

Coverage tally: **11 items → concrete backend test files** (9.1, 9.2, 9.4, 9.5, 9.6, 9.7, 9.8*, 9.9,
9.10, 9.11, 9.12 — 9.8 test-covered only by the new test added here, its TTA numbers are harness-measured),
**3 items → frontend test files** (9.13, 9.14, 9.15; verified green, native-owned),
**1 item → eval harness with a recorded VAL artifact** (9.3),
**1 item → harness + manual protocol** (9.16, including the deliberately deferred Task 8 TEST touch and
Task 9 manual run). 11 + 3 + 1 + 1 = 16.

## Gaps found

**Filled by this task (all green):**
1. `tests/test_model_300.py::test_infer_ensemble_is_probability_distribution` — batch of 2 → shape `(2,109)`,
   rows sum to 1 ± 1e-5, all ≥ 0 (item 9.4; previously only N=1 was covered).
2. `tests/test_calibration.py::test_recognize_probs_batch_rows_are_non_negative` — calibrated batch probs ≥ 0
   and shape `(4,109)` (item 9.5; sum-to-1 was already asserted, non-negativity was not).
3. `tests/test_calibration.py::test_make_windows_contract` — `make_windows` k∈{1,3} shape contract and
   fallback (item 9.8; no unit test existed for the TTA plumbing).
4. `tests/test_calibration.py::test_live_policy_tta_windows_supported` — live policy `tta_windows ∈ {1,3}`
   (item 9.6; `test_live_policy_shape` did not assert the TTA key).

**Needs native lead (not offline-testable in this task's file scope):**
- REST-side provisional-persist row specifically asserted for a *provisional* REST prediction (only the
  general REST persistence pin `tests/test_history.py::test_predict_with_session_logs_and_history_reads`
  plus the WS not-persisted test exist; an explicit REST-provisional row test would live in
  `tests/test_history.py` / `tests/test_api_p4.py` — outside this task's editable set).
- Frontend assertions for items 9.13–9.15 already exist and pass; any *new* frontend coverage would touch
  `frontend/**` — off-limits here (listed for native if more is wanted).
- Item 9.16 TEST arms (`08_final_test.json`, `08_webcamsim_test.txt`) and the Task 9 manual webcam
  protocol require the native lead (TEST is touched exactly once in Task 8; the protocol needs a camera).

## Val replay evidence (reference for item 9.16)

`Docs/eval/06_webcamsim_val.txt` — `py -3 scripts/eval_webcam_sim.py --split val --thr 0.57`, VAL pool
(n=1500 sampled of 2397, seed 11):

```
full_sign        n=1500 acc=0.835 accept@0.57=0.821 acc|accept=0.903 visible_correct=0.741
idle_realistic   n=1500 acc=0.793 accept@0.57=0.783 acc|accept=0.886 visible_correct=0.694
old_45_center    n=1500 acc=0.480 accept@0.57=0.435 acc|accept=0.698 visible_correct=0.303
old_rafdup       n=1500 acc=0.295 accept@0.57=0.297 acc|accept=0.416 visible_correct=0.123
```

`idle_realistic` visible-correct = **0.694 < 0.80** → per plan Task 7 Step 1 this VAL gate does **not**
skip retraining (recorded for the native lead's Task 7 decision).
