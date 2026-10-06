# Migrations (M1)
- M1 uses `Base.metadata.create_all` via `database/seed_m1.py` (SQLite-local verified, PG-ready through `DATABASE_URL`).
- P4 introduces full Alembic revisions (`alembic init` + versioned `upgrade/downgrade` per change); M1 round-trip equivalence proven by re-runnable drop/create + seed asserting 50 classes / 50 assets.
