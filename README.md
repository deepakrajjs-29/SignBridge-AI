# SignBridge AI

Real-time Indian Sign Language (ISL) recognition system: MediaPipe hand
landmarks → 189-D velocity-augmented features → deep sequence ensemble
(LSTM + GRU + mirror-TTA) over a 109-sign vocabulary, with a calibrated
decision policy and a live webcam frontend.

**Status (2026-10-19):** M11–M13 complete. Active model `SBAI-MDL-ISL-4.0.0`
(109-class real-data ensemble). Frozen-test accuracy **81.29%** (macro-F1
**80.79%**); policy-accepted commit precision **89.5% @ 81.3% coverage**
(TEST). The live-camera accuracy protocol (M13 §13) is **pending** — offline
replay is a proxy, not live accuracy. Open release-gate debt: ≥0.90
acceptance target not met (see `Docs/M11_GATE_109REAL.md`, `Docs/32_Known_Issues_Limitations_SignBridge_AI.md`).

## Quick start

```bat
:: Backend (models/registry.json decides the model; MODEL_VERSION is fallback only)
cd backend
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000
:: or from repo root: run-backend.bat

:: Frontend (separate shell)
cd frontend
npm install
npm run dev
:: http://localhost:3000

:: Docker (backend + frontend + Postgres)
docker compose -f docker/docker-compose.yml up --build
```

Copy `.env.example` to `.env` and set `JWT_SECRET` (and `DATABASE_URL` if
using Postgres). API auth is a Bearer token; the default dev secret lives in
`.env`.

## Tests

```bat
py -m pytest tests/ -q        :: 147 backend tests (passing)
cd frontend && npm test       :: 60 vitest tests (passing)
cd frontend && npx tsc --noEmit   :: clean
```

## Model & policy

- Active model: `models/SBAI-MDL-ISL-4.0.0.keras` + bundle in
  `models/SBAI-MDL-ISL-4.0.0/` (`policy.json`, `calibration.json`).
- Lineage: 1.0.0 (MVP) → 2.0.0 (synthetic stub, not production-cleared) →
  3.0.0 (100-class real, M10) → **4.0.0 (109-class real, active, M11)**.
  Candidate 4.1.0 failed promotion gates and was discarded (backups in
  `models/_backup_4.0.0_pretrain/`).
- Decision policy (M13): accept τ = 0.57, provisional floor 0.00, 5-frame
  smoothing, three display states (Recognized / Provisional / Uncertain) +
  No-Sign. Provisional is display-only and never auto-commits. Temperature
  calibration T = 1.0 (fit rejected; ECE already 0.028 VAL).

## Repository layout

| Path | Contents |
| --- | --- |
| `backend/` | FastAPI app (`app/main.py`, `app/deps.py`, routes, WS) |
| `frontend/` | React + Vite app (live capture, MediaPipe Hands, vitest suite) |
| `models/` | Registry, active 4.0.0 bundle, LSTM/GRU members, backups |
| `scripts/` | Eval harness (`eval_report.py`, `calibrate_v4.py`, `eval_webcam_sim.py`, …), training, export, ops |
| `data/` | 109-class tensors + SPLIT-109 signer-disjoint splits (+ pretrain backup) |
| `tests/` | Backend pytest suite |
| `Docs/` | Milestone reports M1–M13, PRD, deploy runbook, eval artifacts |
| `docker/` | Dockerfiles + compose |
| `report.md` | Comprehensive technical & system report |

## Key documents

- `Docs/M13_ACCURACY_CALIBRATION.md` — canonical accuracy/calibration report
  (thresholds, TTA/trim gates, latency, pending live protocol §13).
- `Docs/M12_WEBCAM_ACCURACY.md` — webcam-domain root causes and fixes.
- `Docs/M11_GATE_109REAL.md` / `Docs/M10_GATE_100REAL.md` — promotion gates.
- `Docs/24_Model_Versioning_Experiment_Log_SignBridge_AI.md` — lineage and
  experiment register.
- `Docs/DEPLOY_RUNBOOK.md` — deploy, rollback, backup.
- `SignBridge_AI_Final_Project_Report.docx` — academic final report (patched
  to 4.0.0/M13; pre-patch backup in `Docs/eval/`).

## Evidence artifacts

Fresh evaluation outputs live in `Docs/eval/` (frozen-val/test reports,
policy/calibration JSON, webcam replay results, gate evidence). Numbers in
this README and the milestone docs are traceable to those files.
