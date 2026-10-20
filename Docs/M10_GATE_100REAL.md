# M10 — 100-class REAL-data gate record (SBAI-MDL-ISL-3.0.0)

## What was trained (locked arch/hparams, TF CPU, seed 7)
- Vocab: 100 dynamic ISL words (ISL_001-050 unchanged; ISL_051-100 re-scoped
  2026-10-11 to ISL500-covered words — the previous +50 of Sorry/Welcome/...
  had zero real clips anywhere and were cut).
- Data: CURATION-v3.0 — 13,597 real ISL500 MediaPipe clips, 100/100 classes
  pass the cut rule (129-160 clips x 15 signers each).
- Split: SPLIT-3.0 signer-separated (train U001-U010 n=8078, val U011-U012
  n=2193, test U013-U015 n=3326, 31-35/class), leakage PASS.
- LSTM 150 epochs (best val F1 0.8048) + GRU challenger 96 epochs (best val
  F1 0.8162), Adam 1e-3, ReduceLROnPlateau, early-stop patience 15 on val
  macro-F1, train-only mirror/scale/shift/noise/drop aug. Scaler fit on
  train only (scaler_100_real.npz). Threshold swept on VAL only (0.4).

## Single frozen-test scoring (U013-U015, never trained on)
- LSTM: acc **0.7721** / macro-F1 **0.7664**, n=3326.
- GRU challenger: acc 0.7676 / macro-F1 0.7627.
- DEPLOYED ensemble mean(LSTM, GRU, mirror-TTA), val-tuned (w=0.5, thr 0.4):
  acc **0.8109** / macro-F1 **0.8062** — 80% target MET on held-out test.
- Worst single-model classes: Eat 0.33, Good Evening 0.50, Father 0.53,
  Bank 0.53, Bread 0.56, Hot 0.56, Pizza 0.57, Month 0.58. Best: Stay 0.99,
  Family/Which 0.96. Full table: models/EXP-2026-003-lstm-full/per_class.csv.
- Export parity 200/200 true. Registry sha256 recorded.

## Verification
- [x] Smoke overfit + full runs with history CSVs
- [x] Val-only calibration (policy.json), single frozen-test scoring
- [x] Registration SBAI-MDL-ISL-3.0.0 + SavedModel export + parity
- [x] Latency probe (dev CPU, single-window LSTM: p50 268 / p95 381ms;
  GRU: p95 191ms; deployed 2-call ensemble ≈ 300ms p95 on dev CPU)
- [ ] **GATE DEBT: single-model 0.7721/0.7664 < 0.90/0.90; ensemble clears
  the 0.80 user target (0.8109/0.8062) but 0.90 release gates stay open;
  latency p95 > 200ms on this dev CPU.** Status = Candidate, NOT Approved.

## Remediation backlog
R1. Confusion-driven hard mining on worst classes (Eat/Good Evening/Father/
Bank/Bread/Hot/Pizza/Month) + more signer diversity (left-handed coverage).
R2. Pretrained encoder transfer (literature: 94.5% on INCLUDE-50).
R3. Latency: GRU variant is inside budget (p95 191ms) at -0.004 F1; TFLite/
  quantization or batching for LSTM; re-measure on serving hardware.
R4. Live-camera accuracy study (offline test != live performance).

Pipeline authorized to serve 3.0.0 (strictly better than 2.0.0 synthetic on
every measured axis); 0.90 gates remain open debt, reported honestly.
