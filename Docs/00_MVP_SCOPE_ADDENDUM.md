# 00 — MVP Scope Addendum (overrides all 39 specs where they conflict)

Status: Phase 0 T0.4 · Binding on all downstream work. Where this file contradicts any `Docs/*.md`, **this file wins**.

## 1. Scope flips (Future → MVP)
- UC-07 / US-015 / `POST /tts` + Speak button: **MVP Should** (overrules BRD/UC/US/RTM Future tags).
- UC-13 / US-025 / `POST /text-to-sign` + vocab visuals: **MVP Should**.
- UC-12 / US-014 / history screen (UI-06) + DB persistence: **MVP** (memory frames + DB predictions/history).
- UC-10 / UC-11 / US-016/017/018/021 / UI-09 admin UI + model promote/rollback: **MVP** (RBAC-gated).
- Mobile: responsive mobile-web layout + bottom nav = **MVP**; native apps + on-device inference = Future.
- Sequences: `sequence` = 45-frame buffer for **one isolated sign** (MVP); multi-sign sentence/continuous = Future (rewords PRD FR-05 / SRS FR-VIS-003).

## 2. Canonical API v1 (single source of truth)
`GET /health` · `GET /api/v1/model` · `GET /api/v1/classes` · `POST /api/v1/predict|/sequence|/image|/video` (+`/recognize` alias) · `POST /api/v1/session` + `DELETE /:id` (+`/reset` alias) · `POST /api/v1/tts` · `POST /api/v1/text-to-sign` · `WS /api/v1/stream`. PRD §16 / SRS §5.4 / Arch §11.1 divergent names are deprecated aliases only.

## 3. DB baseline
PostgreSQL-only; Doc-08 9 tables + `sign_assets(asset_id, class_id FK, type, uri)`; `class_id = ISL_001…ISL_050` (kills `CLS-001`/`sign_id` variants); missing DDL + `sessions.user_id` FK to be added in P1 T1.2. Blobs in object storage, never RDBMS.

## 4. Stack + model locks
TF/Keras, PG + SQLAlchemy/Alembic, React+TS (+Tailwind), Python 3.11, single-server Docker. LSTM `45×189 → LSTM128 → LSTM64 → Dense → Softmax(50)` primary, GRU challenger, Transformer deferred. SEQ_LEN=45, FEAT_DIM=189.

## 5. Gates, auth, retention, RACI
Gates: ≥90% acc, ≥0.90 macro-F1, <200ms p95, ≥15fps, ≥80% coverage, 0 Criticals, frozen signer-independent 70/15/15, no leakage. Auth: open `GET /health|/model|/classes`, JWT/OAuth elsewhere. Runtime transient-only; dataset via versioned curation (live-collection rule waived — no self-recording). Retention 90/180/30/30, RPO 24h/RTO 4h. RACI: Project=scope, Technical=arch, AI/ML=model, QA=gates, Security/Privacy=veto, Business Owner=final sign-off.

## 6. ID unification
Model `SBAI-MDL-ISL-X.Y.Z`, runs `EXP-YYYY-NNN`, branches `main/develop/feature/*/fix/*/hotfix/*`, Conventional commits, tests `TC-FUN…` (Doc-29 scheme). Lifecycle mapping `Candidate/Validated/Approved/Deployed ↔ staging/active` resolved in P4/P7 audit.

## 7. Training + data locks (no-recording waiver)
MVP-50 = `data/dataset/annotations/class_map.csv` **v2 (CR-001)**: 50 dynamic ISL words in one Softmax head (digits/letters deferred to v1.1 — no fingerspell video source exists in ISL500/INCLUDE/ISLRTC; ISL500 'I' is the pronoun). Sources: filtered ISL500 (primary) + INCLUDE/INCLUDE-50 via starter40 bundle (tuning/benchmark) + selective ISLRTC numbers (unused after CR-001 swap; retained on disk for v1.1). Trains: LSTM (+GRU spare). Fitted: scaler/threshold. Frozen: MediaPipe/MMPose. Untrained: TTS engine, asset lookup. Not in MVP: sentence/continuous, generation, personalization.
