# Phase 2 — M2 Gate Record

## Delivered
- T2.0 `data/dataset/raw/`: starter40 (0.18 GB, 642 clips + metadata) + isl500 filtered (23 + 27 words: videos + MediaPipe `.h5`) + islrtc Numbers (43 files, retained for v1.1).
- T2.1 `data/dataset/annotations/CURATION-v1.0_manifest.csv` (8,734 rows) + `CURATION-v1.0_summary.md`; CR-001 swap applied → class_map.csv v2 (50 dynamic words), 50/50 OK.
- T2.2 `ai/preprocessing/landmarks.py`: ISL500 `.h5` = single `intermediate` dataset `(T,2,21,3)` float32; wrist-relative + hand-size normalization; zero-safe missing hands. Reuse path confirmed — no MediaPipe rerun needed for ISL500.
- T2.3 `ai/features/build.py` (189 = 126 norm xyz + 42 speed magnitudes + 21 hand-shape stats) + `scripts/build_tensors.py` → `data/dataset/processed/tensors_mvp50.npz` **(7438, 45, 189)**, 50 classes, 15 signers, 0 skipped.
- T2.4 `scripts/make_split.py` → `SPLIT-1.0.json` + `split_idx.npz`: train U001–U010 (4,697; 88–103/class), val U011–U012 (1,091; 19–23/class), test U013–U015 frozen (1,650; 31–35/class).

## Verification (M2 per plan)
- [x] Per-class counts ≥15 clips across ≥10 signers (min: 31 test clips, 30+ total signers with starter40 overlap)
- [x] Unit-equivalent: tensor shape/dtype/mask asserted in build (`(45,189)` float32, NaN/Inf → 0)
- [x] Leakage script: pairwise signer sets disjoint → PASS, split coverage == N (7,438)
- [x] Frozen test checksums: `split_idx.npz` + `SPLIT-1.0.json` committed to processed/annotations
- [x] Starter40 (642 clips, signer/split metadata) reserved as cross-dataset eval set for P3 robustness

## Carries to P3
- Feature definition FV-1.0 = 126+42+21 (documented above; scaler fitted in P3 on train only).
- ISLRTC Numbers + digits/letters queue = v1.1 (no fingerspell video source in current corpora).

Sign-off: Owner-approved conditional via agent gate 2026-09-27 ("approve M2 + M3 conditional"). FV-1.0 + SPLIT-1.0 frozen.
