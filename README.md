# SignBridge AI — MVP (Phase 0 scaffold)

Merged-hybrid repo. Source of truth: `plan.md` + `Docs/*.md` + `Docs/00_MVP_SCOPE_ADDENDUM.md`.
MVP-50 vocab: `data/dataset/annotations/class_map.csv` (30 words + 10 digits + 10 letters).

## Layout
- `frontend/` React+TS + Tailwind (P1 shell → P5 full UI)
- `backend/` FastAPI (P1 skeleton → P4 full APIs)
- `ai/{preprocessing,features,models,evaluation}/` deterministic CV/ML pipeline
- `models/` versioned artifacts (`SBAI-MDL-ISL-X.Y.Z`)
- `data/dataset/{raw,processed,annotations}/` + `CURATION-v1.0` manifest (P2)
- `database/migrations/` Alembic
- `configs/ scripts/ tests/ docs/ deploy/ docker/`

## Gates
M0 (P0) → M1 (P1) → M2 (P2) → M3 (P3) → M4 (P4) → M5 (P5) → M6 (P6) → M7 (P7 RC) → M8 (P8 prod).
No phase starts until prior gate signed per `plan.md`.
