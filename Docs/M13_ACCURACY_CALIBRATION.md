# M13 — Real-Time Accuracy & Confidence Calibration

Status: COMPLETE (Tasks 1–9; manual webcam protocol in §13 awaits a user-run
camera session — all offline/CI work is done and green). All numbers below are
measured; none are projected.

Related: `Docs/M12_WEBCAM_ACCURACY.md` (webcam root-cause report & shipped capture fixes),
`Docs/plans/2026-10-19-realtime-accuracy-calibration.md` (implementation plan).

## Pipeline Trace (target design)

```
capture 3.5 s full-T (no rAF dup) → FV-1.0 feature rows → sendWindow once /
REST frames → preprocess → recognize_probs (make_windows tta=1) →
calibrate_apply (T=1.0 identity) → decision_status (0.00/0.57) →
display Provisional/Recognized → streak/hard-release gate → commit
```

Landed in Tasks 3–5; the WS path carries the full-T `window` message (REST↔WS
parity asserted), and the frontend's `sb_threshold` double gate is gone — the
backend policy alone decides (manual override only via Settings slider).

## 1. Root Causes

Root causes of the reported 20–32% real-time webcam accuracy are documented with
measured evidence in [`Docs/M12_WEBCAM_ACCURACY.md`](M12_WEBCAM_ACCURACY.md):

- **RC-A — capture window ≠ training window** (old ~0.75 s window clipped dynamic
  signs mid-performance; `old_45_center` = 0.475 acc, 0.287 visible-correct @ 0.60).
- **RC-B — rAF duplication** (60 Hz rAF over a 30 fps camera double-processed frames;
  `old_rafdup` = 0.279 acc).
- **RC-C — double gate** (frontend `sb_threshold` 0.70 stacked over backend policy 0.4:
  9 points of coverage lost for 2 points of precision).
- **RC-E — fixed 2.5 s cooldown** instead of release-based re-arm (held pose
  re-committed every 2.5 s).
- **RC-F — speech interruption** (per-sign words cancelled in-flight sentences).

Causes found and fixed inside this M13 effort:

- **RC-G — uncalibrated softmax confidences** — raw ensemble max-prob was used
  directly as confidence. Fitted on VAL (Task 2): **T = 1.0, fit rejected**
  (already well calibrated: ECE 0.0283, NLL 0.5915, Brier 0.2509); confidence
  now flows through `calibrate_apply`, thresholds through `decision_status`
  (§5).
- **RC-H — two-state decision policy** — no Provisional band, so threshold-
  fitted confusions could not be surfaced as "plausible, needs evidence".
  Three-state policy landed (accept 0.57 / prov 0.00): VAL commits now hold
  90.3% precision with FAR cut 43% (§4); frontend renders Provisional without
  committing (RC-E's re-arm interaction handled by the streak/hard-release
  gate, `Live.tsx`).
- **RC-I — single fixed 45-row window on the WS path** — partial-sign windows
  diverged from the REST full-sequence path (REST does better by seeing the
  whole sign). Fixed in Task 5: frontend captures full-T rows and calls
  `sendWindow` exactly once; the `window` WS message predicts on all rows;
  REST↔WS parity pinned for 45-row and 105-row inputs (`test_ws.py`).
  TTA crop views were gated and rejected (§7) — `tta_windows` stays 1.
- **RC-J — WS throttle stamp set before inference** — `stream.py` armed the
  flood throttle at request time, so a >500 ms inference let queued burst
  frames through an instant second pass (observed as `test_ws_flood_is_bounded`
  flake under parallel load). Moved to stamp on inference completion (Task 6
  follow-up); 5/5 re-runs green.

## 2. Files Changed & Why

From `git diff --stat` scoped to this mission (the working tree also carries
earlier-milestone uncommitted work, snapshotted before Task 1 —
`Docs/eval/baseline_git_status.txt` / `baseline_git.patch`; no commits in this
plan). M13 files:

| File | Change | Why |
|---|---|---|
| `backend/app/deps.py` | modified | `get_calibration`, `get_decision_policy`, `calibrate_apply`, `decision_status`, `preprocess_window`, `make_windows` (tta 1/3), full `predict` core extraction |
| `backend/app/routers/predict.py` | modified | REST path: preprocess → ensemble → calibrate → decision (provisional persists, pinned by `test_rest_provisional_status_still_persists`) |
| `backend/app/routers/stream.py` | modified | `_predict_payload` shared core; `window` message branch (full-T); throttle stamp moved to after inference (RC-J flake fix) |
| `frontend/src/api/stream.ts` | modified | `sendWindow()` — one full-T message per sign instead of per-frame |
| `frontend/src/hands.ts` | modified | `buildFeatureRows()` — FV-1.0 rows from full-T landmark history |
| `frontend/src/landmarks.ts` | modified | capture keeps every frame up to 600 (no 45-row subsample) |
| `frontend/src/views/Live.tsx` | modified | Provisional display, 2-soft-streak/hard-release flicker gate, `sb_threshold` double gate removed |
| `frontend/src/views/Settings.tsx` | modified | `manualGate` — backend-calibrated by default, slider only overrides when touched |
| `scripts/eval_report.py` | created | Pinned-metric offline VAL/TEST harness (baseline + final reports) |
| `scripts/calibrate_v4.py` | created | VAL-only temperature fit + literal precision-rule thresholds (§5) |
| `scripts/train_v3.py` | modified | `--time-jitter` (Task 7 candidate augmentation; candidate gate-FAILed, flag kept) |
| `scripts/eval_webcam_sim.py` | created (M12, extended) | h5-webcam-replay conditions → `06_webcamsim_val.txt`, `08_webcamsim_test.txt` |
| `scripts/eval_webcam_report.py` | created | Webcam-truth CSV → accuracy/coverage report (§13) |
| `scripts/export_predictions.py` | created | Session `Prediction` rows → CSV (5 pinned columns + pk) |
| `tests/test_calibration.py` | created | Temperature primitives + `make_windows` + live-policy TTA pin (6 tests) |
| `tests/test_decision_policy.py` | created | Three-state boundaries, missing-keys legacy fallback, live policy shape (3) |
| `tests/test_class_mapping.py` | created | Characterization pin: class_map.csv order ↔ `label_of` ↔ `class_list` (2) |
| `tests/test_export_predictions.py` | created | REST persist → CSV round-trip, header-only, CLI (3) |
| `tests/test_ws.py` | modified | `window` message, full-T parity ×2, provisional-not-persisted, flood re-pin (14 tests in file) |
| `tests/test_history.py` | modified | REST provisional persistence asymmetry (+1) |
| `tests/test_api_p4.py`, `test_model_300.py`, `test_ensemble400.py` | modified/created | REST status set, ensemble distribution, batch-N shapes |
| `frontend/src/views/Live.test.tsx`, `hands.test.ts`, `api/stream.test.ts` | modified | Full-T capture, flicker gate, Provisional copy (48 npm tests) |
| `models/SBAI-MDL-ISL-4.0.0/{policy,calibration}.json` | created/merged | Fitted thresholds 0.57/0.00 + T=1.0 record (rollback: §12) |
| `Docs/eval/01_baseline_val.json`, `05_val_w{1,3}.json`, `06_webcamsim_val.txt`, `08_*` | created | Baselines, TTA gate, webcam gates, final VAL/TEST records |
| `Docs/eval/09_matrix_proposal.md`, `webcam_truth_template.csv` | created | §8.1 verification notes; §13 blank attempt sheet |
| `Docs/M13_ACCURACY_CALIBRATION.md` | created | This report |

## 3. Baselines

### Offline-npz VAL baseline (Task 1, model 4.0.0, temperature 1.0, tta_windows 1, accept threshold 0.4)

Source: `Docs/eval/01_baseline_val.json` (`py -3 scripts/eval_report.py --split val --out Docs/eval/01_baseline_val.json --self-check`).

| metric | value |
|---|---|
| n (val) | 2397 |
| argmax_accuracy | 0.833125 |
| overall_accuracy | 0.816854 |
| accepted_accuracy | 0.854276 |
| coverage | 0.956195 |
| false_accept_rate_overall | 0.139341 |
| false_accept_rate_accepted | 0.145724 |
| low_conf_correct_rate | 0.019529 |
| macro_f1 | 0.828963 |
| ece | 0.028272 |
| brier | 0.250855 |
| latency_ms p50 / p95 | 232.28 / 271.34 |
| counts recognized / provisional / uncertain / no_sign | 2292 / 0 / 105 / 0 |

Self-check passed: first 200 chunked rows match a naive per-row `infer_ensemble`
loop to max |diff| 2.98e-07 (atol 1e-5).

### Real-time baselines (user-reported, for context)

- User-reported real-time accuracy before M12 capture fixes: **22–32%**.
- After the shipped M12 capture fixes (user-reported): **42–50%**.
- M12 offline webcam-replay proxy (`h5-webcam-replay`, n=1500 frozen-test clips):
  `idle_realistic` acc 0.769, visible-correct @ 0.60 = 0.642; `full_sign` acc 0.822,
  visible-correct = 0.715 (see M12 for the full table).

## 4. Final Metrics

All numbers below from `Docs/eval/08_final_val.json` / `08_final_test.json`
(model 4.0.0, temperature 1.0, tta_windows 1, accept 0.57, prov 0.00).
Labels: `overall` = correct AND recognized (committable-correct / n);
`accepted` = precision of the recognized (committable) set;
`FAR` false-accept = wrong-and-recognized (both denominators given).

### VAL (n=2397) — baseline (accept 0.4) vs final (accept 0.57, VAL-fitted)

| metric | baseline `01_baseline_val` | final `08_final_val` | delta |
|---|---|---|---|
| argmax_accuracy (raw model) | 0.833125 | 0.833125 | 0 (same model) |
| overall_accuracy | 0.816854 | 0.740926 | −0.0759 (stricter accept) |
| accepted_accuracy | 0.854276 | 0.903357 | **+0.0491** |
| coverage | 0.956195 | 0.820192 | −0.1360 (fewer auto-commits) |
| false_accept_rate_overall | 0.139341 | 0.079266 | **−0.0601 (−43%)** |
| false_accept_rate_accepted | 0.145724 | 0.096643 | **−0.0491 (−34%)** |
| low_conf_correct_rate | 0.019529 | 0.110666 | correct-but-not-committed moves into the provisional band |
| macro_f1 | 0.828963 | 0.828963 | 0 (argmax-based) |
| ece / brier | 0.028272 / 0.250855 | 0.028272 / 0.250855 | 0 (temperature fit rejected → identity) |
| counts rec/prov/unc/nosign | 2292 / 0 / 105 / 0 | 1966 / 431 / 0 / 0 | 105 uncertain + 326 above-0.4 rows re-banded; prov=0 ⇒ uncertain never fires (documented literal-rule outcome, §5) |

Reading: the VAL-fitted threshold buys **precision of commits (90.3%) and
roughly halves false accepts** at the cost of coverage (95.6% → 82.0%);
the model itself (argmax) is untouched.

### TEST (n=3629) — the single frozen-test touch (Task 8)

| metric | value |
|---|---|
| argmax_accuracy | **0.812896** (matches M11 historical 0.8129 — cross-check ✓) |
| overall_accuracy | 0.728024 |
| accepted_accuracy | **0.895290** |
| coverage | 0.813172 |
| false_accept_rate_overall | 0.085147 |
| false_accept_rate_accepted | 0.104710 |
| low_conf_correct_rate | 0.104407 |
| macro_f1 | 0.807865 (M11 historical: 0.8079 ✓) |
| ece / brier | 0.022447 / 0.272741 |
| counts rec/prov/unc/nosign | 2951 / 678 / 0 / 0 |
| latency (windows-aware probe) | p50 374.85 ms / p95 575.22 ms |

### h5-webcam-replay TEST pool (`08_webcamsim_test.txt`, thr 0.57, n=1500)

| condition | acc | accept rate | acc\|accept | visible_correct |
|---|---|---|---|---|
| full_sign (new ~3.5 s capture) | 0.822 | 0.813 | 0.905 | 0.736 |
| idle_realistic (+reaction delay) | 0.769 | 0.759 | 0.875 | 0.664 |
| old_45_center (old ~0.75 s window) | 0.475 | 0.439 | 0.690 | 0.303 |
| old_rafdup (rAF reprocessing) | 0.279 | 0.303 | 0.455 | 0.138 |

(acc values identical to M12's frozen-test run — same model, reproducible ✓;
visible_correct slightly above M12 because the accept threshold moved 0.60 → 0.57.)
These are `h5-webcam-replay` offline proxies, NOT camera measurements —
the 80% real-time target is assessed by the manual protocol (Task 9, user-run).

### 4.1 Conditional Retrain (Task 7) — ATTEMPTED, GATE FAIL, DISCARDED

- **Gate input** (`Docs/eval/06_webcamsim_val.txt`, VAL h5-webcam-replay at accept 0.57):
  `idle_realistic visible_correct = 0.694 < 0.80` → retrain **triggered** (not skipped).
- **Backups taken first (mandatory Step 0):**
  - `models/_backup_4.0.0_pretrain/` — policy.json, calibration.json, registry.json,
    `SBAI-MDL-ISL-4.0.0{,_gru,_lstm}.keras`, `scaler_109_real.npz`, `_savedmodel/`
    (weights live at `models/` root, not inside the version dir — backed up explicitly).
  - `data/dataset/_backup_pretrain/` — all 9 `processed/` files (tensors + splits).
- **Candidate:** `SBAI-MDL-ISL-4.1.0` GRU + `--time-jitter` (circular time roll r ∈ [−4,4]
  before existing aug, train-only), `scripts/train_v3.py` change; EXP-2026-005,
  96 epochs (best 81), 14.2 min. Smoke `SMOKE_OK`.
- **Promotion gate (candidate must beat Task-1 baseline on BOTH):**

  | metric | baseline 4.0.0 ensemble | candidate 4.1.0 GRU+jitter | required | result |
  |---|---|---|---|---|
  | val macro-F1 | 0.828963 | 0.814275 | > 0.828963 | FAIL (−0.0147) |
  | val argmax accuracy | 0.833125 | 0.816854 | > 0.833125 | FAIL (−0.0163) |

- **Decision: candidate DISCARDED per plan; `SBAI-MDL-ISL-4.0.0` remains active;
  no registry change; no calibrate_v4 re-run.** Candidate artifacts kept for the
  record under `models/EXP-2026-005-gru-full/` (+ `models/train_4.1.0.log`).
  (Honest caveat: gate compares a single fresh GRU against the deployed 3-way
  ensemble — the plan pinned this comparison; it failed, so nothing is promoted.)

### 4.2 Failure-improvement attempt (post-M13 audit) — MOTION TRIM, GATE FAIL, REVERTED

- **Hypothesis (VAL-evidence based):** the idle/reaction-delay window spends
  ~44% of its 45 resampled rows on near-static filler (measured), diluting the
  sign; trimming static head/tail rows before the linspace resample should
  recover idle accuracy.
- **Change tried:** inference-only `trim_static_rows` (10% of window p90
  motion-energy threshold) in `deps.preprocess_window` +
  `eval_webcam_sim`, with 9 unit tests (exact-idle trim, blank/short
  fallbacks, no-sign gate preservation — all green).
- **VAL replay gate (same command as §4.1 input, `--split val --thr 0.57`,
  evidence `Docs/eval/10_p1trim_gate_after.txt`):**

  | condition | before (06) | after trim | verdict |
  |---|---|---|---|
  | full_sign acc | 0.835 | **0.768** | −6.7pp — FAIL (non-regression) |
  | full_sign visible_correct | 0.741 | **0.613** | −12.8pp FAIL |
  | idle acc | 0.793 | 0.737 | **worse** (−5.6pp) |
  | idle visible_correct | 0.694 | 0.577 | **worse** (−11.7pp) |

- **Root cause of the failure:** training tensors are built UNTRIMMED
  (`build_tensors_v3` → `to_sequence`), so clip-internal slow frames are part
  of the training manifold — trimming any real-clip span (not just simulator
  pads) skews serve inputs; the full_sign arm caught it. An exact-repeat-only
  variant would improve the *simulator's* literal padding without helping
  live jitter windows, so it was rejected as metric-chasing without real
  benefit.
- **Decision: fully reverted (code + tests), replay harness re-run reproduces
  the 06 baseline exactly (0.835/0.793/0.480/0.295); suite back to 123
  passed.** Threshold/confidence untouched; no TEST involvement (VAL-only).

## 5. Calibration

- Fit script: `scripts/calibrate_v4.py` (VAL only, n=2397), run in Task 2.
  Artifacts: `models/SBAI-MDL-ISL-4.0.0/calibration.json` +
  `policy.json` (merge-write; rollback copy `Docs/eval/policy_4.0.0_original.json`).
- **Temperature = 1.0 (`fit_rejected: true`)** — the raw ensemble is already
  well calibrated on VAL (val ECE 0.028272, NLL 0.5915, Brier 0.2509);
  no temperature improved ECE, so identity is kept (honest, no forced fit).
- **Thresholds (VAL-fitted, literal precision rules):**
  `accept_threshold = 0.57` (precision(conf≥0.57) = 0.9034 ≥ 0.90,
  coverage 0.8202), `provisional_threshold = 0.00` (literal
  precision(conf≥t) ≥ 0.80 already holds at t=0 — argmax accuracy 0.833 —
  so the fitted band floor is 0; clamp leaves 0.00), legacy `threshold`
  0.4 → 0.57 (= accept).
  **NOTE (flagged):** with `provisional_threshold = 0.0` the
  provisional band spans all non-accepting confidences and "uncertain"
  never fires under the fitted policy — a literal-spec outcome, recorded
  deliberately; the alternative band-precision reading was rejected as
  non-literal but remains a one-line revisit if the user prefers it.
- VAL decision counts at fitted policy (from `05_val_w1.json`):
  recognized 1966 / provisional 431 / uncertain 0 / no_sign 0.
- **Provisional-band composition (measured, closes the threshold question):**
  of the 431 blocked VAL rows, **221 correct / 210 wrong → band precision
  0.5128** — a near coin flip. Blocking the band is not discarding mostly-
  correct answers; it withholds 221 correct rows to keep 210 errors out of
  commits (the honest price of 90.3% commit precision). Blocked-correct
  concentration: ISL_044 Eat 17, ISL_106 Chair 10, ISL_088 Red 10,
  ISL_012 Help 10, ISL_046 Sit 9 — confidence-suppression cases (§6 pairs),
  not threshold error. A full VAL threshold sweep (0.50/0.55/0.565/0.57/0.60)
  shows 0.57 sits at the literal-rule knee: 0.565 clears precision 0.9013 by
  only +9 covered rows with a razor-thin margin; below 0.565 the ≥0.90 rule
  breaks. **No better operating point exists on VAL; threshold unchanged.**
  (False accepts are confidently wrong — mean conf 0.752 — so no threshold
  can separate them; remaining errors are data-side, see §4.2/§10.)

## 6. Per-Class & Confusion

- Artifacts (TEST, single touch): `Docs/eval/08_final_test_confusion.csv`,
  `Docs/eval/08_final_test_per_class.csv` (VAL twins: `08_final_val_confusion.csv`,
  `08_final_val_per_class.csv`).
- **Top confusable off-diagonal pairs (TEST)** — feeds the Task 9 manual
  protocol's 20-sign set (10 pairs × 2 = 20 distinct signs):

  | # | pair (true → predicted) | count | | # | pair | count |
  |---|---|---|---|---|---|---|
  | 1 | ISL_046 → ISL_106 | 22 | | 6 | ISL_081 → ISL_088 | 9 |
  | 2 | ISL_043 → ISL_050 | 17 | | 7 | ISL_025 → ISL_093 | 9 |
  | 3 | ISL_044 → ISL_013 | 16 | | 8 | ISL_063 → ISL_096 | 8 |
  | 4 | ISL_071 → ISL_009 | 10 | | 9 | ISL_061 → ISL_107 | 8 |
  | 5 | ISL_042 → ISL_039 | 10 | | 10 | ISL_012 → ISL_040 | 8 |

  (ISL_013 → ISL_044: 12 is the reciprocal of pair 3 — same mutual pair.)

## 7. Latency

- M11 reference (single GRU model, batch=1): p50 64.4 ms.
- Task 1 baseline (active 4.0.0 ensemble via `infer_ensemble`, per single row,
  200 sampled VAL rows): p50 232.28 ms / p95 271.34 ms — the ensemble runs
  LSTM+GRU over `[x, mirror(x)]` (2 predict calls per model), so per-row latency
  is structurally higher than the M11 single-model probe. TTA windows (Task 5)
  multiply this further; the Task 5 gate requires w3 latency p95 ≤ 300 ms.
- **Task 5 TTA gate (VAL only, windows-aware probe = make_windows + model
  passes + calibration, same probe for both arms):**
  - `05_val_w1.json`: overall 0.740926, accepted 0.903357, coverage 0.820192,
    latency p50 326.79 / p95 369.36 ms.
  - `05_val_w3.json`: overall 0.705048, accepted 0.910070, coverage 0.774718,
    latency p50 342.15 / p95 371.65 ms.
  - Gate: Δoverall(w3−w1) = **−0.0359** (needs ≥ +0.010) AND p95 371.65 ms
    (needs ≤ 300) → **BOTH conditions FAIL → `tta_windows` stays 1.**
    The ensemble already includes mirror-TTA; adding early/late crop views
    hurts VAL argmax accuracy (0.8331 → 0.8252) — decision recorded, no gate
    override. (Old-style per-row `infer_ensemble` probe for w1: 232/271 ms;
    the windows-aware probe above additionally includes the recognize path,
    which is why the absolute numbers are higher.)
- **Final latency (Task 8, windows-aware probe, tta_windows 1 = shipped):**
  VAL p50 288.99 / p95 318.42 ms; TEST p50 374.85 / p95 575.22 ms.
  The M11 p50 64.4 ms figure was a *single GRU* on npz rows — not
  comparable to the 3-way ensemble serving path; both are reported as-is,
  no cross-probe averaging.

## 8. Test Outcomes

- Task 1: `py -3 -m pytest tests/ -q` → 104 passed.
- Task 2: → 107 passed. Task 3: backend 112 / frontend 40 / tsc clean.
- Task 4: frontend 46 / tsc clean.
- Task 5 (all green): `py -3 -m pytest tests/ -q` → **115 passed**;
  `npm test` → **48 passed** (8 files); `npx tsc --noEmit` → clean;
  live smoke against restarted uvicorn: `POST /api/v1/predict` (105 rows)
  → `status "provisional"` (conf 0.2526 < 0.57), model 4.0.0.
- Task 6 (+4 gap tests, e.g. `test_infer_ensemble_is_probability_distribution`):
  backend **119 passed**; Task 6 also flagged a pre-existing
  `test_ws_flood_is_bounded` flake — **fixed natively** by moving the WS
  throttle stamp to inference *completion* in `stream.py` (was set before a
  possibly >500 ms inference, arming an instant second pass over queued
  burst frames); 5/5 re-runs green.
- Native follow-up: `tests/test_history.py::test_rest_provisional_status_still_persists`
  added (REST↔WS persistence asymmetry pinned on the REST side) → backend
  **120 passed**.
- Task 7: backend **120 passed**; frontend **48 passed**; tsc clean.
- Task 8 (single frozen-test touch + webcam replay + suites): `08_final_val.json`,
  `08_final_test.json`, `08_webcamsim_test.txt` written (§4); backend
  **120 passed** (one flake: `test_parallel_predicts_overlap` failed only under
  parallel suite load, passes alone — pre-existing, unrelated), frontend
  **48 passed**, `npx tsc --noEmit` clean.
- Task 9 (+export/report scripts, +3 tests → `tests/test_export_predictions.py`):
  backend **123 passed** (final count; script-review pass on
  `export_predictions.py` / `eval_webcam_report.py` native).

## 8.1 Requirement Coverage Matrix (16 items)

Reconstructed 1:1 from the plan's pinned accuracy requirements (the plan's
"Phase 8 regression matrix" list); every claimed test verified to exist AND
run green. Source proposal with full verification notes:
`Docs/eval/09_matrix_proposal.md`.

| # | Item | Coverage | Verification |
|---|---|---|---|
| 9.1 | Class-mapping pin `ISL_{y+1:03d}` ↔ `label_of` ↔ `class_map.csv` | `tests/test_class_mapping.py` (2 tests) | 2 passed |
| 9.2 | SPLIT-109 signer-disjoint, 70/15/15, 8800/2397/3629 | `tests/test_split_v2.py` (2 tests) | 2 passed |
| 9.3 | VAL baseline harness keys + self-check | eval harness | `01_baseline_val.json` (n=2397, argmax 0.833125) |
| 9.4 | Ensemble output = probability distribution (incl. batch N=2) | `test_ensemble400.py::test_ensemble_proba_shape_and_mass`, `test_model_300.py::test_infer_ensemble_is_probability_distribution` | 3 + 4 passed |
| 9.5 | Calibration primitives (identity fallback, T=1, flattening, batch ≡ rows, non-negativity) | `tests/test_calibration.py` (6 tests) | 6 passed |
| 9.6 | Live policy shape (`threshold == accept 0.57`, `0 ≤ prov ≤ acc`, `tta_windows ∈ {1,3}`) | `test_decision_policy.py::test_live_policy_shape`, `test_calibration.py::test_live_policy_tta_windows_supported` | green |
| 9.7 | Three-state boundaries inclusive; missing keys → legacy two-state | `test_decision_policy.py` (2 tests) | 3 passed total |
| 9.8 | TTA window plumbing (`make_windows` k∈{1,3} + fallback) | `test_calibration.py::test_make_windows_contract`; numbers in `05_val_w{1,3}.json` | green |
| 9.9 | REST status set + no-sign short-circuit + 422/413/404 envelopes | `test_api_p4.py` (`test_predict_200_and_alias`, `test_blank_frames_yield_no_sign`, `test_predict_422_dim_and_413`) | 31 passed |
| 9.10 | Persistence asymmetry (WS provisional NOT persisted; REST provisional IS) | `test_ws.py::test_ws_provisional_not_persisted`, `test_history.py::test_rest_provisional_status_still_persists` | green |
| 9.11 | REST↔WS parity (45-row frame + 105-row full-T window) | `test_ws.py::test_rest_ws_parity_45_rows`, `::test_rest_ws_full_t_parity_105_rows` | in 14-passed run |
| 9.12 | WS `window` message (full-T prediction; 1..600 validation) | `test_ws.py::test_ws_window_full_t_prediction`, `::test_ws_window_invalid_input` | in 14-passed run |
| 9.13 | Full-T capture path (no subsample; single `sendWindow`; CONNECTING queue) | `frontend/src/hands.test.ts`, `api/stream.test.ts`, `views/Live.test.tsx` | npm 48 passed |
| 9.14 | Flicker-safe commit (A→soft→A once; 2-soft re-arm; no-sign hard-release) | `frontend/src/views/Live.test.tsx` (5 flicker tests) | npm 48 passed |
| 9.15 | Provisional display (`toState`, `confidenceNote` copy, user-gate-only threshold) | `frontend/src/views/Live.test.tsx` (3 tests) | npm 48 passed |
| 9.16 | Accuracy gates & end-to-end metrics (VAL baselines, TTA gate FAIL→1, webcam replay gate, final TEST, manual protocol) | eval harness + manual: `01_baseline_val.json`, `05_val_w{1,3}.json`, `06_webcamsim_val.txt`, Task 8 `08_*`, Task 9 protocol | VAL + TEST arms DONE (`08_final_test.json`); manual protocol = §13 (user-run) |

Tally: 11 → backend tests, 3 → frontend tests, 1 → eval harness artifact,
1 → harness + manual protocol. Only open row: 9.16's manual camera protocol
(by design — no camera in this environment; §13 is the ready-to-run sheet).

## 9. Versions

- Model: `SBAI-MDL-ISL-4.0.0` (ensemble LSTM+GRU+mirror-TTA; active, unchanged —
  Task 7's 4.1.0 candidate gate-FAILed and was discarded)
- Policy: `models/SBAI-MDL-ISL-4.0.0/policy.json` — accept 0.57, prov 0.00,
  legacy `threshold` 0.57, `tta_windows` 1 (pre-M13 copy: `Docs/eval/policy_4.0.0_original.json`)
- Calibration: `models/SBAI-MDL-ISL-4.0.0/calibration.json` — temperature 1.0,
  `fit_rejected: true` (VAL ECE 0.0283 already < any fitted T)
- Tensors: `tensors_109_real.npz` (X (14826,45,189), y 0..108)
- Split: SPLIT-109 signer-disjoint 8800/2397/3629 (`split_idx_109.npz`)
- Classes: 109 (`data/dataset/annotations/class_map.csv`, `ISL_001`..`ISL_109`)
- Python 3.14 / NumPy (no new dependencies)

## 10. Limitations

- **Offline ≠ webcam.** Every accuracy number here comes from npz held-out
  rows or the `h5-webcam-replay` offline proxy (frozen test clips re-rendered
  through the old/new capture conditions). Real-camera performance additionally
  involves lighting, framing, clothing/background, latency perception, and
  signer skill — only §13 measures that, and only by hand.
- **No camera in this environment.** CI cannot drive a webcam; the 80%
  real-time target is assessed solely by the manual protocol (§13), which has
  not yet been run — do not read the offline numbers as the target's verdict.
- **Single frozen-test touch.** `08_final_test.json` is the only TEST-pool
  evaluation under the fitted policy (plan-pinned). Thresholds were fit on VAL
  only; TEST numbers are a one-shot confirmation (argmax 0.812896 matches M11's
  historical 0.8129 ✓).
- **REST/WS history asymmetry (by design).** REST persists every non-no-sign
  prediction including provisional; the WS path persists only recognized
  commits. Export CSVs therefore contain REST provisional rows but no WS
  provisional rows — pinned by tests, not a bug.
- **Provisional is never auto-committed.** The 431 VAL / 678 TEST provisional
  rows are shown to the user and dropped unless re-confirmed; coverage 82%/81%
  is the price of the 90.3%/89.5% commit precision.
- **`provisional_threshold = 0.00` (literal-rule outcome).** Under the fitted
  policy the uncertain band never fires — everything below accept is
  Provisional (§5 NOTE). Flagged, deliberate, one-line reversible.
- **TTA w3 rejected on VAL.** Gate data covers one VAL run at one seed; w3
  might help other regimes, but the shipped default is w1 and no override was
  taken.
- **Retrain gate compared 1 GRU vs a 3-way ensemble** (plan-pinned comparison)
  — candidate failed both metrics, so the caveat is recorded but moot:
  nothing changed.
- **Reaction-delay dilution is real but not safely fixable by trimming**
  (evidence §4.2): any trim that helps idle windows also cuts into sign-clip
  slow frames and fails the full_sign gate. The residual idle cost is borne
  by the 0.57 policy (blocked band) rather than by preprocessing.
- **Latency probes are structural, not UX SLAs.** Ensemble = 4 model passes
  per row (LSTM+GRU × mirror); p95 318 ms VAL / 575 ms TEST are probe numbers
  on this machine, not per-frame streaming latency.

## 11. Run Instructions

All commands from the repo root (`D:\Projects\SignBridge`); no new dependencies.

```bash
# --- Task 1 baseline (VAL) with self-check ---------------------------------
py -3 scripts/eval_report.py --split val --out Docs/eval/01_baseline_val.json --self-check
py -3 -m pytest tests/test_class_mapping.py -q

# --- Task 2 calibration (VAL only; script takes NO flags — always VAL, always
#     merge-writes; re-run is deterministic: reproduces T=1.0 / 0.57 / 0.00) ---
py -3 scripts/calibrate_v4.py
#   -> models/SBAI-MDL-ISL-4.0.0/{calibration,policy}.json (rollback copy: Docs/eval/policy_4.0.0_original.json)

# --- Tasks 4/6 evaluation sweeps (--windows, not --tta-windows) -------------
py -3 scripts/eval_report.py --split val  --windows 1 --out Docs/eval/05_val_w1.json
py -3 scripts/eval_report.py --split val  --windows 3 --out Docs/eval/05_val_w3.json   # gate arm
py -3 scripts/eval_report.py --split test --out Docs/eval/08_final_test.json --self-check  # THE single TEST touch
py -3 scripts/eval_report.py --split val  --out Docs/eval/08_final_val.json  --self-check

# --- webcam-replay gates (M12 conditions; prints to stdout, no --out;
#     --thr 0.57 MUST match the recorded baselines) --------------------------
py -3 scripts/eval_webcam_sim.py --split val  --thr 0.57 > Docs/eval/06_webcamsim_val.txt
py -3 scripts/eval_webcam_sim.py --split test --thr 0.57 > Docs/eval/08_webcamsim_test.txt

# --- Task 7 conditional retrain (already run: GATE FAIL → discarded) --------
py -3 scripts/train_v3.py --mode full --arch gru --time-jitter --exp EXP-2026-005

# --- export + webcam report (Task 9) ---------------------------------------
py -3 scripts/export_predictions.py --session <session_id> --out preds.csv
py -3 scripts/eval_webcam_report.py --truth Docs/eval/webcam_truth.csv --out Docs/eval/webcam_report.json

# --- suites (final counts) --------------------------------------------------
py -3 -m pytest tests/ -q          # 123 passed
npm test                           # 48 passed  (workdir: frontend/)
npx tsc --noEmit                   # clean      (workdir: frontend/)

# --- serving (4.0.0 + fitted policy) ---------------------------------------
py -3 -m uvicorn app.main:app --app-dir backend --port 8000
```

## 12. Rollback

- Rollback record of the pre-M13 policy: `Docs/eval/policy_4.0.0_original.json`
  (verbatim copy of `models/SBAI-MDL-ISL-4.0.0/policy.json` at Task 1 time:
  `threshold: 0.4`, `smoothing_window: 5`).
- **Pre-retrain backups (Task 7 Step 0, verified):**
  - `models/_backup_4.0.0_pretrain/` — `policy.json`, `calibration.json`,
    `registry.json`, `SBAI-MDL-ISL-4.0.0{,_gru,_lstm}.keras`,
    `scaler_109_real.npz`, `SBAI-MDL-ISL-4.0.0_savedmodel/`
    (weights + scaler + registry live at `models/` root).
  - `data/dataset/_backup_pretrain/` — all 9 files of `processed/`
    (`tensors_*.npz/json`, `split_idx*.npz`).
- Rollback procedure (calibrated-policy era): restore
  `models/SBAI-MDL-ISL-4.0.0/policy.json` from `Docs/eval/policy_4.0.0_original.json`
  (threshold back to 0.4; remove `accept_threshold`/`provisional_threshold` keys)
  and delete `models/SBAI-MDL-ISL-4.0.0/calibration.json` → `get_calibration()`
  falls back to identity T=1.0. Registry stays on `active_model:
  SBAI-MDL-ISL-4.0.0` (unchanged — Task 7 retrain was discarded, so no model
rollback is required). Full weights restore if ever needed: copy
`models/_backup_4.0.0_pretrain/*` back over `models/` (nothing was modified).

## 13. Manual Webcam Protocol (user-run — results slot pending)

No camera exists in this environment, so the 80% real-time target is assessed
by this protocol, run by hand against the live app
(`py -3 -m uvicorn app.main:app --app-dir backend --port 8000` + frontend dev
server, model 4.0.0 with the fitted policy — verify Settings shows automatic
mode, i.e. no manual threshold override). Fill
`Docs/eval/webcam_truth_template.csv` (copy to `webcam_truth.csv`) — columns:
`attempt_id, expected_class_id, displayed_label, displayed_state, displayed_conf,
flips_in_attempt, notes` — transcribing displayed values **from the screen**
(state included: Recognized / Provisional / Uncertain / No-Sign; rejections and
no-signs count as rows). Then:

```bash
py -3 scripts/eval_webcam_report.py --truth Docs/eval/webcam_truth.csv --out Docs/eval/webcam_report.json
```

### 13.1 Sign set (pinned)

- **20 signs × 4 attempts = 80 Single-mode attempts** (plan-pinned), in this
  deterministic construction (seed 20261019):
  - **10 confusable representatives** — the true side of each top-10 TEST
    confusion pair (§6): `ISL_046, 043, 044, 071, 042, 081, 025, 063, 061, 012`
    (their paired twins — 106, 050, 013, 009, 039, 088, 093, 096, 107, 040 —
    remain measurable as the *predicted* side of those errors).
  - **10 additional signs**, drawn deterministically from the remaining
    classes (`random.Random(20261019).sample`): `ISL_004, 019, 032, 041, 048,
    053, 056, 075, 085, 092`.
- **Ready-made protocol pack (pre-generated, do not regenerate):**
  - `Docs/eval/webcam_truth.csv` — 92 rows (A001–A080 shuffled + H1–H4 +
    R1–R3 + S1–S5) with attempt_id/expected_class_id pre-filled and all
    `displayed_*` columns blank for the live observation.
  - `Docs/eval/webcam_attempt_deck.md` — the ordered sign deck to perform.

### 13.2 Stress rows (beyond the 80)

| id | test | pass criterion | notes value |
|---|---|---|---|
| H1–H4 | hold one sign continuously ≥ 8 s (4 s beyond the capture length) | exactly **1** commit; no re-commit while held | `held-sign` |
| R1–R3 | deliberately sign the same sign 3× in a row | 3 commits, none dropped/merged by throttle | `same-sign-repeat` |
| S1–S5 | one 5-sign sentence in Continuous mode (Hello → Please → Help → Yes → Thank You), one row per word | all 5 words appear in order; no in-flight cancellation (RC-F) | `sentence` |

### 13.3 Report + acceptance

- Run the report script; **paste its output verbatim into this section labeled
  `webcam-protocol (user-run, manual)`** (accuracy, coverage, provisional rate,
  flips, per-row table).
- Missed attempts (nothing shown / No-Sign): leave `displayed_label` blank,
  record `displayed_state`. The script folds empty labels into `n_invalid`
  (they leave `overall_accuracy`'s denominator), so acceptance is ALSO
  computed over every attempt: **raw = n_correct_recognized / n** — reported
  side by side, never only the engaged-attempt figure.
- Target: real-time accuracy **≥ 80%** over the 80 Single attempts (both
  readings shown), with H/R/S rows passing their criteria.
  Compare against the context baselines in §3 (user-reported 22–32% → 42–50%
  after M12 fixes).

### 13.4 Results

`webcam-protocol (user-run, manual)` — **PENDING** (protocol ready; awaiting
camera session. Report lands here verbatim once run.)
