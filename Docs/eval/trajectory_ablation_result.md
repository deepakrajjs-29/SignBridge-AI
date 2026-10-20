# Trajectory Feature Ablation (FV-1.0 + 4 global-wrist channels → FV-2.0 pilot)

**Date:** 2026-10-20 · **Experiment:** `EXP-2026-006` · **Candidate id:** `SBAI-MDL-ISL-4.2.0` · **Plan:** `Docs/plans/2026-10-20-temporal-motion-fixes.md` Task 6

> **VERDICT: FAILED activation gates → NOT registered, NOT activated. `SBAI-MDL-ISL-4.0.0` remains the active model.** Tasks 7A/7B (activation switch) skipped.

## What was trained

- **Features:** FV-1.0 189 dims + `[w0_u, w0_v, du, dv]` global hand-0 wrist trajectory (pre-normalization image coords) = **193 dims** (`frame_features_v2`), so global hand path — previously erased by wrist-relative normalization — is visible to the model.
- **Data:** `tensors_109_traj.npz` (14,826 ordered clips, y/files integrity-verified identical to `tensors_109_real.npz`), signer-disjoint `split_idx_109.npz` (8800/2397/3629), own scaler `scaler_109_traj.npz` (1,1,193).
- **Training:** locked arch/hparams (Adam 1e-3, batch 64, ≤150 epochs, early-stop patience 15 on val macro-F1, default mirror+scale/shift/noise/drop aug; mirror extended to negate trajectory channels), TF-CPU (GPU unavailable in this TF build), seed 7.

## Results

| Model | Arch | Epochs / wall | Best val macro-F1 | **VAL argmax acc** | TEST argmax acc | TEST macro-F1 |
|---|---|---|---|---|---|---|
| 4.2.0 candidate | LSTM128→64 | 114 / 22.2 min | 0.7608 | **0.7693** | 0.7641 | 0.7556 |
| 4.2.0 candidate | GRU128→64 | 112 / 17.6 min | 0.8172 | **0.8214** | 0.8052 | 0.8015 |
| 4.2.0 (informational) | LSTM+GRU mean, **no** mirror-TTA | — | — | 0.8231 (exact boundary) | not scored | not scored |
| **4.0.0 baseline (active)** | ensemble + mirror-TTA | — | 0.8290 | **0.8331** | **0.8129** | **0.8079** |

Sources: `models/EXP-2026-006-{lstm,gru}-full/test_report.json` + `policy.json` (`val_argmax_acc`); baseline `Docs/eval/08_final_test.json`, M13.

## Gate table (plan Global Constraints)

| Gate | Required | Measured (best arch = GRU) | Result |
|---|---|---|---|
| VAL argmax acc | ≥ 0.8231 | **0.8214** | **FAIL** (−0.0017) |
| TEST argmax acc | ≥ 0.8029 | 0.8052 | PASS |
| webcam-sim `full_sign` | ≥ 0.8122 | **not run** | verdict already determined (all gates must pass); running it requires adding the v2 feature path to `eval_webcam_sim.py` for a candidate that cannot be activated — skipped to avoid pointless surface area |
| **Overall** | all pass | 1 FAIL | **FAIL** |

Cross-check against the stricter M13 promotion gates (val acc ≥ 0.833125, val macro-F1 ≥ 0.828963): also **FAIL** under every reading (single-arch and ensemble-no-TTA).

## Analysis (measured vs hypothesis)

- **Measured:** adding global trajectory channels did **not** improve validation accuracy. GRU+traj (0.8214) fell 1.2pp short of baseline ensemble val (0.8331); LSTM+traj collapsed to 0.7693 — the trajectory channels appear to add overfit-prone input (camera framing position is signer/framing-dependent) far more to LSTM than GRU.
- **Measured:** the temporal-dynamics conclusion from `motion_sensitivity.json` (staticify → 0.0091, time_shuffle → 0.4274) already showed the shipped 189-dim model relies heavily on temporal order; the ablation confirms that *adding explicit global path* does not convert that reliance into better generalization.
- **Hypothesis (unverified):** H1 (global path erasure hurts location/trajectory signs) remains plausible for per-class effects but is **not supported as an overall-accuracy fix** by this run. Per-class comparison (does SIT/WALK/GO improve while others hold?) was not part of the gate and is left as optional follow-up on `EXP-2026-006-*/per_class.csv`.
- **Train/serve mirror caveat (found during implementation):** serve-side `deps.mirror_features` (189-dim logic) does not negate trajectory channels, while the training-time mirror now does — another reason this candidate must not ship without further work.

## Versioning notes

- `SBAI-MDL-ISL-4.1.0` was intentionally **NOT** reused: it is the documented, discarded GRU+time-jitter candidate from 2026-10-19 (`Docs/24_…` line 476, `Docs/M13_…` §Task 7, `Docs/32_…` LIM-022; artifacts in `models/EXP-2026-005-gru-full/`, untouched).
- This experiment therefore used `SBAI-MDL-ISL-4.2.0` in `models/EXP-2026-006-*`. Artifacts retained for traceability; registry unchanged (`active_model` = `SBAI-MDL-ISL-4.0.0`, `models` has no 4.1.0/4.2.0 entry).
- FV-2.0 code (`frame_features_v2`, FEAT_DIM_V2=193) remains in the codebase as tested, inactive capability; serving path, `.env` `FEAT_DIM=189`, and frontend `hands.ts` unchanged (Task 7B executed).

## Status

- [x] Both archs trained, evaluated, gates computed, report written
- [ ] 4.1.0/4.2.0 activation — **cancelled: gates failed**
- [ ] webcam-sim full_sign for candidate — cancelled (verdict determined)
