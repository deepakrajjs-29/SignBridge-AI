# SignBridge AI — Final Submission Checklist (2026-10-20 09:16)

## Deliverables (paths)
| Item | Path | Status |
|---|---|---|
| Academic final report (DOCX) | `SignBridge_AI_Final_Project_Report.docx` | DONE — text/tables 4.0.0/M13; Fig 5.6 regenerated from fresh test per-class CSV |
| Pre-patch DOCX backup | `Docs/eval/SignBridge_AI_Final_Project_Report.pre-M13-backup.docx` | DONE |
| Technical report | `report.md` | DONE — 109-class, 4.0.0 ensemble, M13, honest gate debt |
| README | `README.md` | DONE |
| Canonical accuracy report | `Docs/M13_ACCURACY_CALIBRATION.md` | DONE (§13.4 webcam results PENDING user run) |
| Webcam root-cause report | `Docs/M12_WEBCAM_ACCURACY.md` | DONE |
| Webcam protocol pack | `Docs/eval/webcam_attempt_deck.md` + `Docs/eval/webcam_truth.csv` | READY (user fills displayed_*) |
| Webcam report JSON | `Docs/eval/webcam_report.json` | PENDING — generated only from genuine rows |
| Institutional docs | `Docs/11…`, `Docs/24…`, `Docs/25…`, `Docs/32…` | DONE |
| Deploy runbook | `Docs/DEPLOY_RUNBOOK.md` | DONE (v1.1) |
| Model + policy | `models/SBAI-MDL-ISL-4.0.0*`, `policy.json`, `calibration.json` | DONE, unchanged this hour |
| Backups | `models/_backup_4.0.0_pretrain/`, `data/dataset/_backup_pretrain/`, `Docs/eval/policy_4.0.0_original.json` | INTACT |
| Eval evidence | `Docs/eval/01,05,06,08,10_*` | INTACT |

## Verification (fresh, this hour)
| Check | Result |
|---|---|
| Backend pytest | 123 passed |
| Frontend vitest | 48 passed |
| `tsc --noEmit` | CLEAN |
| GET /health | ok |
| GET /api/v1/model | SBAI-MDL-ISL-4.0.0, 109 classes, ensemble arch |
| GET frontend :3000 | 200 |
| Registry active_model | SBAI-MDL-ISL-4.0.0 |
| Git branch / working tree | main, 213 uncommitted entries preserved (no commits made) |

## Outstanding items (do not mark complete)
1. **M13 §13 live-camera protocol** — user-run (camera). Fill `webcam_truth.csv` from screen; then:
   ```
   py -3 scripts/eval_webcam_report.py --truth Docs/eval/webcam_truth.csv --out Docs/eval/webcam_report.json
   ```
   Partial CSVs are valid (blank rows = unjudged). Remaining unfilled rows get documented PENDING in M13 §13.4.
2. **DOCX figures 1.1 / 3.2 / 5.3 / 5.4 / 5.5** — still legacy-visual (captions/text corrected). Fig 5.5 training curves need EXP-2026-004 history.csv which does not exist on disk; regeneration deferred (no fabrication).
3. **DOCX TOC / List-of-Figures page numbers** — may drift (no Word repagination here).
4. **Open ≥0.90 accuracy gate debt** — recorded honestly (M11, Docs/25, Docs/32, report.md). Out of scope this hour per instruction.
5. **Git commit** — NOT made (preserve-only instruction; commit only if you explicitly request).

## Rollback (if needed)
- Weights: restore `models/_backup_4.0.0_pretrain/`
- Policy: copy `Docs/eval/policy_4.0.0_original.json` → `models/SBAI-MDL-ISL-4.0.0/policy.json`, delete `calibration.json`
- DOCX: restore `Docs/eval/SignBridge_AI_Final_Project_Report.pre-M13-backup.docx`

## Webcam report command (after CSV fill)
```
py -3 scripts/eval_webcam_report.py --truth Docs/eval/webcam_truth.csv --out Docs/eval/webcam_report.json
```
Then paste real numbers into `Docs/M13_ACCURACY_CALIBRATION.md` §13.4. Nothing fabricated.
