# Phase 0 — Milestones, Risks, M0 Gate

## Milestones
- M0 P0 Scope frozen (this gate) — Business Owner
- M1 P1 Stack running — QA
- M2 P2 Data frozen (CURATION-v1.0, SPLIT-1.0) — AI/ML
- M3 P3 Model approved (SBAI-MDL-ISL-1.0.0) — AI/ML + QA (Sec/Priv non-veto)
- M4 P4 APIs contract-green — Technical + Security
- M5 P5 UI E2E-green — QA
- M6 P6 Integrated MVP — Technical
- M7 P7 RC v0.5 — QA + Sec/Priv veto
- M8 P8 Prod v1.0 — Business Owner

## Risk watch (top 5)
| ID | Risk | KRI | Mitigation |
|---|---|---|---|
| R1 | Accuracy <90% on frozen test | val macro-F1 trend (T3.1) | GRU challenger parallel; confusion-driven class cuts to v1.1 |
| R2 | Unseen-signer drop | cross-dataset ISL500→INCLUDE delta (T3.3) | pooled 22-signer splits; aug policy frozen in T2.4 |
| R3 | Scope creep (admin/history/TTS) | UC/US tag drift | 00 addendum binding; any change needs Business Owner CR |
| R4 | Latency >200ms p95 | inference probe (T3.3) | co-located inference; TFLite fallback task queued |
| R5 | Tracking loss in poor light | robustness battery (T3.3) | quality-reject + UX re-frame guidance |

## M0 verification checklist
- [ ] `data/dataset/annotations/class_map.csv` = 50 rows, IDs ISL_001…050 (30 words + 10 digits + 10 letters)
- [ ] Repo layout + `.github/workflows/ci.yml` + `.env.example` + `backend/requirements.txt` + `frontend/package.json` + `configs/baseline.yaml` present
- [ ] `Docs/00_MVP_SCOPE_ADDENDUM.md` present and referenced from `plan.md` flow
- [ ] `pytest -q` / `npm test` stubs acknowledged (real suites land P1+)
- [ ] Business Owner sign-off recorded below

Sign-off: Owner-approved via agent gate 2026-09-27 (option: "Approve M0, start Phase 1"). MVP-50 locked as class_map.csv v1.
CR-001 (owner-approved swap, post-T2.1 manifest): 27 classes with zero/thin coverage (Sorry/Bye/Home/Welcome/Name/Money/Love/Zero–Nine/A–S letters) replaced with verified in-vocabulary ISL500 words → class_map.csv v2 (50 dynamic words, 50/50 OK in CURATION-v1.0 manifest v2, 8,734 rows). Digits/letters deferred to v1.1. M0 scope updated, IDs ISL_001…050 unchanged.
