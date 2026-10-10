# SBAI-MDL-ISL-2.0.0 — Training / Registration Report (Task 6, fixed round 1)

## Real training run (scripts/train_smoke100.py, seed 7)
- Data: SYNTHETIC (45,189) 100-class — class prototypes + Gaussian noise + temporal
  drift + 20% tail zero-masking. train=2400 / val=500 / test=500. NOT real ISL landmarks.
- Protocol: 5-epoch smoke, then short full run (max 30 epochs, early-stop patience 5 on
  val macro-F1, best-only restore). Adam 1e-3, batch 64. (Full ≤150 / patience-15
  reserved for the real-data train.)
- LSTM: 9 epochs, best val_macro_F1=1.0 (epoch 4) → early-stop epoch 9. GRU challenger,
  same protocol: 9 epochs, val_macro_F1=1.0 (tie → LSTM kept as primary per Task 6).
- Frozen synthetic test: acc=1.0, macro-F1=1.0 (n=500) — measured, from actual
  predictions; per-class P/R + 100×100 confusion in EXP test_report.json / confusion.npz.
- Scaler: REFIT on synthetic train mean/std (was: copy of scaler_mvp50) → scaler_100.npz.
  Must refit again on real FV-2.0 train tensors for production.
- Calibration (val-only): threshold sweep {0.3,0.4,0.5,0.6} coverage≥0.9 → chosen 0.3;
  smoothing window 5 carried over (utterance-level synthetic data cannot calibrate
  streaming smoothing — recalibrate on real val). See calibration.json.
- Export: SavedModel SBAI-LSTM-100_savedmodel/ + 200-sample parity probe:
  max_abs_diff=0.0, argmax 200/200 (parity_probe.json).
- Latency REAL CPU: p50 64.17 / p95 85.19 / p99 99.9 ms → p95 < 200 PASS; FPS 254.9 ≥ 15 PASS.
- Logs: models/EXP-2026-002-lstm-smoke100/ + models/EXP-2026-002-gru-smoke100/
  (train.log, val_history.json, test_report.json, confusion.npz, calibration.json,
  parity_probe.json). eval.json `measured` block cross-references these files.

## Measured vs projected (clear)
- MEASURED on synthetic: test acc 1.0 / F1 1.0, latency, FPS, parity — all from the run above.
- Gate flags in eval.json are computed from measured values (gate_acc_90 = measured ≥ 0.90).
  Synthetic separability ≠ production readiness.
- registry.json: 1.0.0 top-level record untouched (still deployed); 2.0.0 added under
  `models` key as a registered synthetic-trained candidate.

## Remaining to clear the gate for real
1. Real-data full train ≤150 epochs, patience 15, on FV-2.0 tensors; refit scaler on real train.
2. Val-only threshold/window calibration on real val; frozen-test scoring.
3. Overwrite eval.json measured block with real numbers; promote only if acc ≥ 0.90 and F1 ≥ 0.90.
