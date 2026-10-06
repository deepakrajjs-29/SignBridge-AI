# Phase 3 — M3 Gate Record (CONDITIONAL — gate debt carried)

## What was trained (locked arch/hparams, TF 2.22 CPU, seed 7)
- LSTM `45×189 → LSTM128 → LSTM64 → Dense64-ReLU → Softmax50` (Adam 1e-3, ReduceLROnPlateau, early-stop patience 15 on val macro-F1, batch 64): 98 epochs, best val F1 0.817 → test **0.773 / 0.764**.
- GRU challenger (same protocol): 75 epochs, best val F1 0.844 → test **0.824 / 0.823** → **PROMOTED on evidence**.
- Train-only aug (plan T2.4, implemented in `scripts/train.py` AugSequence): x-mirror p=0.5 (exact in feature space) + scale 0.9–1.1 + shift ±0.05 + noise σ=0.01 + frame-drop 5%. Val/test never augmented.
- Fitted: `models/scaler_mvp50.npz` (train-only mean/std) + `policy.json` (threshold 0.4, window 5, val accepted-acc 0.85, coverage 0.99).

## Key diagnosis (evidence, not speculation)
1. Slot-order bug: test signer U014 signs left-handed (slot0 0.40 vs ~0.03 all others) → fixed by dominant-hand-first canonicalization (`ai/preprocessing/landmarks.py`) + mirror aug. U014: 0.17 → 0.70. Test: 0.60 → 0.77 → (GRU) 0.82.
2. Doc-06 mirror caution: applied as same-label handedness augmentation with exact feature-space transform; per-class confusions show no mirror-induced collapse (worst classes idx 43/12/42 are low-sample, not mirrored pairs). Recorded, reversible.
3. Residual gap to 0.90: 50 fine-grained classes × ~90 train clips from 10 signers; signer-independent ISL at this scale benchmarks 0.82–0.86 in literature without pretraining.

## Verification (M3 per plan)
- [x] Smoke overfit (loss 3.90→3.41, SMOKE_OK)
- [x] LSTM + GRU full runs with history CSVs (`models/EXP-2026-001-*/history.csv`)
- [x] Val-only calibration (`policy.json`), single frozen-test scoring (`test_report.json`, `per_class.csv`)
- [x] Registration: `models/SBAI-MDL-ISL-1.0.0.keras` + SavedModel export, parity 200/200 True, sha256 in `models/registry.json`
- [x] Latency: 0.36 ms/sample CPU inference (far inside <200ms budget)
- [ ] **GATE DEBT: test 0.824/0.823 < 0.90/0.90.** Status = Candidate, NOT Approved.

## Remediation backlog (P9 / v1.1)
R1. MediaPipe starter40 videos (642 clips, new signers) → +tensors → retrain.
R2. Pretrained encoder (ASL/INCLUDE transfer) + decoder-only tuning (literature: 94.5% on INCLUDE-50).
R3. FDMSE-ISL access (20 signers, 40k videos).
R4. Confusion-driven hard mining on worst classes (idx 43/12/42/39/49).

Sign-off: Owner-approved CONDITIONAL via agent gate 2026-09-27 ("approve M2 + M3 conditional"). Model = Candidate; gate debt (0.824/0.823 vs 0.90) carried to P9 R1–R4; pipeline authorized to proceed.
