# Deploy Runbook — v1.0 (single-server, Blue-Green)

## Preconditions (M7 RC proximate)
- `docs/RC_v0.5.json` 11/11 hashes verify (`freeze_rc.py` logic).
- Secrets in manager only: `DATABASE_URL` (managed PG), `JWT_SECRET` (rotation-ready), `CORS_ORIGINS`. Repo holds `.env.example` placeholders — verified no real `.env` on 2026-09-27.

## Promote (Blue-Green)
1. Deploy RC to Green (staging): `docker compose up`, run `scripts/smoke_prod.py` — require 9/9.
2. Warmup call first: cold-start TF graph ≈ 9 s on CPU; steady-state ≈ 0.4 ms. Never route traffic before one warmup predict.
3. Switch LB Green→Blue; keep prior Blue 24 h.
4. Run smoke again on prod URL; check Prometheus alerts (`deploy/alert_rules.yml`).

## Rollback (<5 min, drilled)
- `POST /api/v1/admin/rollback` swaps `active_model` ↔ `previous_model` in `models/registry.json` (audit-logged; `404 NO_ROLLBACK_STATE` when nothing to revert), then redeploy/restart, warmup, smoke. Drill 2026-09-27: GRU→LSTM→GRU all OK, hash-verified.

## Backup / RPO-RTO
- `scripts/backup.py`: 7 artifacts, HASH-OK 7/7, backup 0.0 s / verify 0.1 s locally (attested 2026-09-27). Schedule daily; RPO 24 h, RTO 4 h (restore = copy + warmup + smoke).
- DB: manifest records `db_kind`; sqlite → file copy, postgres → `pg_dump "$DATABASE_URL" -f postgres.dump` (clear error if `pg_dump` missing). Restore DB: sqlite → copy file back; postgres → `psql "$DATABASE_URL" < postgres.dump`, then confirm `models/registry.json:active_model` matches the deployed model before warmup + smoke.
- Monitoring: `deploy/prometheus.yml` + alerts (health down 2 m, p95 > 200 ms 5 m, 5xx rate 5 m).

## Retention sweep (daily cron)
- `scripts/retention.py`: children-first deletes (feedback → predictions → sessions), tz-aware cutoffs; windows unchanged (sessions 90 d, predictions 180 d, api_logs 30 d).
- Cron: `0 3 * * * /srv/signbridge/venv/bin/python /srv/signbridge/scripts/retention.py >> /var/log/signbridge/retention.log 2>&1`
- Requires `DATABASE_URL` (managed PG) in the cron environment.
- Verify: log line shows `{sessions, predictions, api_logs}` counts; alert on nonzero exit.

## Known prod gaps (carried, not blocking single-server pilot)
PG live run, CDN, external pen-test, 24 h soak, browser E2E/axe, MediaPipe image/video (501), JWT proper (shared-secret Bearer live), cold-start 9 s (warmup covers).
