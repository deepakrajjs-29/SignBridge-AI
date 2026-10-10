# SBAI-MDL-ISL-2.0.0 — Training / Registration Report (Task 6)

## What is REAL
- `ai/models/lstm.py`: `NCLASS 50 -> 100`; model names `SBAI-LSTM-100` / `SBAI-GRU-100`;
  `build_lstm()` / `build_gru()` default to `nclass=100`, output shape `(None, 100)` verified via keras.
- `SBAI-LSTM-100.keras` + `SBAI-GRU-100.keras`: real keras-saved architectures (seed-7 init, NOT trained).
- `scaler_100.npz`: feature-wise mean/std copied from `scaler_mvp50.npz` (same 189-dim FV-2.0 features).
- `classmap.csv`: 100-class vocab copy (ISL_001 Hello … ISL_100 Yesterday).
- Latency (REAL, CPU, per-sample predict loop, 200 samples): p50 132.99 ms / p95 159.89 ms / p99 181.45 ms → p95 < 200 ms PASS.
- Throughput (REAL, batch predict): mean 13.24 ms/sample → 75.5 FPS → FPS >= 15 PASS.
- Export parity probe: 200-sample predict shape (200, 100), no diff (same in-memory graph).
- `tests/test_model100.py`: RED (2 failed: default 50, names -50) → GREEN (3 passed) after fix.

## What is STUB (clear disclosure)
- `eval.json` accuracy 0.92 / macro-F1 0.91 are PROJECTED acceptance targets, NOT measured.
  No GPU training (smoke or full) was executed in this environment per the Task 6 allowance
  ("lightweight architecture + metadata stub allowed"). These gates must be re-scored on a
  frozen test set after a real ≤150-epoch train before any production promotion.
- `models/registry.json` (1.0.0 record) deliberately untouched; this directory + `metadata.json`
  + `sha256.txt` constitute the 2.0.0 registration record.

## Remaining to clear the gate for real
1. Run smoke 5-epoch + full ≤150-epoch Adam 1e-3 train with early-stop (patience 15, val macro-F1).
2. Val-only threshold/window calibration; frozen-test scoring (acc, macro-F1, per-class P/R, confusion).
3. Replace stub acc/F1 in `eval.json` with measured values; promote only if acc ≥ 0.90 and F1 ≥ 0.90.
