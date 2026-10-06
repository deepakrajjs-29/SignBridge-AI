# Phase 8 — M8 Gate Record

## Delivered
- T8.1: `scripts/backup.py` (7 artifacts, HASH-OK 7/7, instant locally; daily schedule prescribed) · secrets audit (no real `.env`; placeholders only) · `docker/` + `deploy/` promotion inputs from P1/P7.
- T8.2: `scripts/smoke_prod.py` **9/9 PASS** (health, pinned version, 50 classes, predict+timing, TTS contract, T2S flags, history round-trip, admin, WS) · `deploy/prometheus.yml` + `alert_rules.yml` · rollback drill GRU→LSTM→GRU all-OK hash-verified <5 min · `docs/DEPLOY_RUNBOOK.md` (Blue-Green, warmup, RPO/RTO).

## Verification (M8 per plan)
- [x] Prod-equivalent smoke 9/9 on RC bundle
- [x] Rollback demonstrated with hash verification
- [x] RPO 24 h (daily backup exists) / RTO 4 h (restore = copy + warmup + smoke, drilled)
- [x] Monitoring + alerts filed; cold-start caveat (9 s first predict) documented with warmup gate
- [ ] Live cloud URL, managed PG, CDN, external pen-test, 24 h soak (require prod env — runbook prescribes)

Sign-off (Business Owner): Owner-approved via agent gate 2026-09-27 (option: "Approve M8"). v1.0 PRODUCTION-READY per pilot scope. Carries: cloud URL, managed PG, CDN, pen-test, soak (P9/prod env).
