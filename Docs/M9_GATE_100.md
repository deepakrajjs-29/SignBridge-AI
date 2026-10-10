# Phase 9 — M9 Gate Record: 100-word RC freeze (Task 9)

## Gate evidence (all measured, 2026-10-10)

| Gate | Expected | Observed | Source |
|---|---|---|---|
| Classes | 100 | 100 rows | `data/dataset/annotations/class_map.csv` |
| Photo assets | 100 | 100 files `ISL_*.jpg` | `data/assets/` |
| Active model | SBAI-MDL-ISL-2.0.0 | SBAI-MDL-ISL-2.0.0 | `models/registry.json` → `active_model` |
| Frozen test acc | ≥ 0.90 | 1.0 (n=500) | `models/SBAI-MDL-ISL-2.0.0/eval.json` → `measured.test_accuracy` |
| Frozen test macro-F1 | ≥ 0.90 | 1.0 | `eval.json` → `measured.test_macro_f1` |
| Latency p95 | < 200 ms | 177.87 ms (p50 156.95, p99 188.53) | `eval.json` (REAL CPU per-sample loop, 200 synthetic samples) |
| Throughput | > 15 FPS | 105.6 FPS | `eval.json` (REAL CPU sustained batch throughput) |
| Export parity | 200/200 | max_abs_diff 0.0, argmax 200/200 | `eval.json` → `export_parity_200` |
| Release test | PASS | `test_release100_gates` PASSED | `tests/test_release100.py` |

## E2E notes (10-sign staged)

- `scripts/e2e_10sign.py`: 10-sign staged E2E (frozen test clips → REST predict → DB chain → WS reconnect) — built against `tensors_mvp50` (50-class) fixtures; full 100-class frozen-clip rerun pending real-data tensors (carried over, not blocking synthetic RC).
- `scripts/smoke_prod.py` 9/9 PASS on M8 (health, pinned version, predict+timing, TTS contract, T2S flags, history round-trip, admin, WS); serving-shape re-verified for 100 classes by `tests/test_api_100.py`.
- WS drop/reconnect: covered by `tests/test_ws.py` + e2e chain above.
- Load (Locust/k6) and axe scan: no harness in repo — carried over to real-data phase; NOT claimed.

## Rollback drill (< 5 min to 1.0.0)

- Live drill via serving API on isolated temp DB: `GET /api/v1/model` → 2.0.0, `POST /api/v1/admin/promote {1.0.0}` → model serves **1.0.0** (rollback target verified servable), `POST /api/v1/admin/rollback` → model serves **2.0.0**.
- Wall time **0.2 s** (limit 300 s). `models/registry.json` restored byte-identical (sha256 `92c0c5707c6b…` verified before/after); repo DB untouched.
- Rollback target artifacts on disk: `models/SBAI-MDL-ISL-1.0.0.keras` + `SBAI-MDL-ISL-1.0.0_savedmodel/` (immutable 1.0.0 record preserved).

## RC bundle (frozen RC-v1.0)

- App images: `docker/Dockerfile.backend`, `docker/Dockerfile.frontend`, `docker/docker-compose.yml`; monitoring `deploy/prometheus.yml` + `alert_rules.yml`; runbook `Docs/DEPLOY_RUNBOOK.md`.
- Model: `models/SBAI-MDL-ISL-2.0.0/` (LSTM primary + GRU challenger, scaler_100, classmap, policy, eval, TRAINING-REPORT) + `sha256.txt` (2 artifact hashes).
- Data refs: `CURATION-v2.0.json`, `SPLIT-2.0.json`, `class_map.csv`, `models/registry.json` (`active_model=2.0.0`).
- Backup: `scripts/backup.py` (7 artifacts, M8-verified).

## Scope disclosure (synthetic — read before promoting)

- RC-v1.0 is a **SYNTHETIC-CANDIDATE**: acc/F1/latency/FPS above are measured on **EXP-2026-002 synthetic prototypes+noise (45,189), NOT real ISL landmarks**. Weights are real trained weights from the synthetic run (seed 7), not production weights.
- **No production clearance claimed.** Production gates clear only after real-data full train + frozen-test rescoring (then acc/F1 ≥ 0.90 must be re-measured, and the carried-over 100-class E2E, load, and axe scans executed).

Verdict: **M9 GATE GREEN (synthetic-candidate)** — RC-v1.0 frozen pending real-data train.
