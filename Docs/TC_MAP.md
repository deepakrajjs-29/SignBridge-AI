# T7.2 — Requirement → Test Trace (unified TC-FUN scheme, Doc-29)

| Req / Use case | Tests | Evidence |
|---|---|---|
| FR-CAM permission/start-stop (UC-02) | TC-FUN-cam: Live view enable/deny copy (static) + API session open/close | `test_api_p4.py::test_session_lifecycle`, Live.tsx |
| FR-VIS landmarks/normalize (UC-03) | TC-PRE-landmark: H5 shape/validation/canonicalize unit-equivalents | build logs (7438 built, 0 skipped), `landmarks.py` |
| FR-AI predict + threshold (UC-03/04/05) | TC-AI-predict, TC-PRE-seq, TC-API-predict, TC-WS-stream | `test_api_p4.py`, `test_ws.py`, `test_report.json` (0.824) |
| FR-OUT states (UC-05) | TC-FUN-states: 7-state machine render | Live.tsx STATES + M5 checklist |
| FR-SES history (UC-12) | TC-DB-history, TC-API-history | `test_history.py` (log→list→delete→404) |
| FR-TXT TTS + text-to-sign (UC-07/13) | TC-API-tts (501 contract), TC-API-t2s (supported/unsupported) | `test_api_p4.py` |
| FR-ADM model mgmt (UC-10/11) | TC-SEC-admin (401/403/RBAC/audit) | `test_api_p4.py::test_admin_rbac_and_audit` |
| NFR perf (<200ms, ≥15fps) | TC-PERF-latency (0.36ms/sample), TC-LOAD-burst (200/200) | M3 registry, loadprobe output |
| NFR security/privacy | TC-SEC-scan (ORM-only, no secrets), TC-PRI-transient | secscan output, retention sweep |
| NFR retention (90/180/30/30) | TC-DB-retention | `retention.py` sweep `{'sessions':0,...}` |

## Lifecycle mapping
Registry `Candidate/Validated/Approved/Deployed` ↔ DB `ModelVersion.status`
(`development/staging/active/retired`): current `SBAI-MDL-ISL-1.0.0` = registry **Candidate** ↔ DB **development** (seed) — promotion to `staging`/`Approved` happens at M8X deploy; mapping enforced in `routers/admin.py` audit actions.

## Branch/commit audit
Workspace is not a git repo (host constraint, recorded since M0). On `git init`: `main` (+`develop`), `feature/*`, `fix/*`, `hotfix/*`, Conventional commits per CI (`ci.yml` lints backend + frontend + secrets-scan). Verified: `ci.yml` present; commit history N/A until init.
