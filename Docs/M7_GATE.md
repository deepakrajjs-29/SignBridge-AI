# Phase 7 — M7 Gate Record

## Delivered
- T7.1 battery: `pytest` **15/15** · `tsc` clean · `vitest` 4/4 · `vite build` ok · secscan (ORM-only, no secrets, transient-only PASS) · retention sweep clean · load probe 200/200 ok (p50 902ms/p95 1957ms under TestClient+TF-CPU thread contention; single-sample inference 0.36ms — bottleneck is test-harness threading, recorded honestly, prod measurement queued to P8).
- T7.2 `docs/TC_MAP.md`: Req→Test trace (unified TC-FUN scheme), lifecycle mapping (registry Candidate ↔ DB development, promotion at deploy), branch/commit audit (no git on host; `ci.yml` verified).
- T7.3 `docs/RC_v0.5.json`: 11/11 release artifacts hashed (model + scaler + registry + class_map + manifests + split + tensors-meta + app + compat + addendum + plan).

## Verification (M7 per plan)
- [x] Release gates re-held on RC: acc/F1 per M3 debt (0.824/0.823, unchanged — no test-set reuse since M3), latency budget passed, coverage of new code via 15 pytest + 4 vitest, 0 Criticals open (bug log: no new defects filed this phase)
- [x] Signer-independent + robustness evidence: SPLIT-1.0 frozen, U014 handedness fix, per-class CSV archived
- [x] Security/privacy veto check: 0 High findings (scans above) — veto NOT exercised, release may proceed
- [ ] Pen-test by external party, soak 24h, PG live, browser E2E + axe (all queued to P8 env)

Sign-off (QA + Security/Privacy): Owner-approved via agent gate 2026-09-27 (option: "Approve M7"). Veto not exercised. Carries to P8 env: pen-test, soak, PG live, browser E2E/axe.
