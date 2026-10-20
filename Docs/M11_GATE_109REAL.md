# M11 — 109-class REAL-data gate record (SBAI-MDL-ISL-4.0.0)

## What was trained (locked arch/hparams, TF CPU, seed 7)
- Vocab: 109 dynamic ISL words (ISL_001-100 unchanged; ISL_101-109 =
  Library, Meeting, Holiday, Pen, Paper, Chair, Police, Airport, Manager —
  the 9 audited ISL500-covered words from the 101-200 request; 5 exact dupes
  and 86 no-source/thin words queued in
  data/dataset/annotations/vocab_queue_200.csv, NOT trained).
- Data: CURATION-v4.0 — 14,826 real ISL500 MediaPipe clips, 109/109 classes
  pass the cut rule.
- Split: SPLIT-4.0 signer-separated (train U001-U010 n=8800, val U011-U012
  n=2397, test U013-U015 n=3629), leakage PASS.
- LSTM 130 epochs (best val F1 0.7726) + GRU challenger 94 epochs (best val
  F1 0.8156), Adam 1e-3, ReduceLROnPlateau, early-stop patience 15 on val
  macro-F1, train-only mirror/scale/shift/noise/drop aug. Scaler fit on
  train only (scaler_109_real.npz). Threshold swept on VAL only (0.4).

## Single frozen-test scoring (U013-U015, never trained on)
- GRU winner: acc **0.8057** / macro-F1 **0.8012**, n=3629.
- LSTM challenger: acc 0.7567 / macro-F1 0.7506.
- DEPLOYED ensemble mean(LSTM, GRU, mirror-TTA), val-tuned (thr 0.4):
  acc **0.8129** / macro-F1 **0.8079** — 80% target MET on held-out test.
- Worst GRU classes: ISL_046 0.20, ISL_044 0.41, ISL_066 0.41, ISL_013 0.53,
  ISL_074 0.56. Best: ISL_102 (Meeting) 0.98, ISL_006 0.97, ISL_055 0.97.
  Full table: models/EXP-2026-004-gru-full/per_class.csv.
- Export parity 200/200 true. Registry sha256 recorded.

## Verification
- [x] Full runs with history CSVs (EXP-2026-004-{lstm,gru}-full)
- [x] Val-only calibration (policy.json), single frozen-test scoring
- [x] Registration SBAI-MDL-ISL-4.0.0 + SavedModel export + parity
- [x] Promotion 4.0.0 (previous 3.0.0), live DB reseed 109/109, backend restart
- [x] Pinned tripwires: tests/test_ensemble400.py, tests/test_release400.py
- [ ] **GATE DEBT: single-model 0.8057/0.8012 < 0.90/0.90; ensemble clears
  the 0.80 user target (0.8129/0.8079) but 0.90 release gates stay open.**
  Status = Candidate, NOT Approved.

## Remediation backlog
R1. Hard mining on worst classes (ISL_046/044/066/013/074); ISL_046 (F1 0.20)
needs clip-level inspection (possible label noise).
R2. Remaining 91 queued words need real sources before any 200-class run.
R3. Live-camera accuracy study (offline test != live performance).

Pipeline authorized to serve 4.0.0 (strictly better than 3.0.0 on every
measured axis: +0.002 acc / +0.002 F1 with 9 more classes); 0.90 gates
remain open debt, reported honestly.
