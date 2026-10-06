# SignBridge AI — MVP Implementation Plan v3 (phase-by-phase, chronological)

> Source of truth: 39 spec docs in `Docs/*.md` + 17 resolved conflicts (Batch 1 Q1–Q9, Batch 2 Q10–Q17) + owner waivers (no self-recording).
> Locked baselines: **LSTM (45×189) + GRU challenger, TF/Keras, Python 3.11+, PG + SQLAlchemy/Alembic, React+TS + Tailwind, single-server Docker, `/predict` family + `/tts` + `/text-to-sign` + `/session` + `/stream`, Doc-08 DB + `sign_assets`, responsive-web + full history + full admin UI in MVP, gates ≥90% acc / ≥0.90 macro-F1 / <200ms / ≥15fps / ≥80% coverage / 0 Criticals**, split auth (open `GET /health|/model|/classes`, JWT/OAuth on the rest), memory frames + DB predictions/history, isolated-sign only, merged hybrid repo, unified IDs (`SBAI-MDL-ISL-X.Y.Z`, `EXP-YYYY-NNN`, `TC-FUN…`), retention 90/180/30/30, RACI (Project=scope, Technical=arch, AI/ML=model, QA=gates, Security/Privacy=veto, Business Owner=sign-off).
> Locked training scope: **MVP-50 = 30 daily words + 10 digits (0–9) + 10 high-use letters in one Softmax(50)**; datasets = filtered ISL500 (primary) + INCLUDE/INCLUDE-50 (tuning/benchmark) + selective ISLRTC letters/digits; only LSTM (+GRU) trains — scaler/threshold fitted, MediaPipe/MMPose frozen, TTS off-the-shelf, text-to-sign = lookup. Full 180 GB NOT required — MVP ≈ 8–15 GB (smoke ≈ 1–2 GB).

Repo (merged hybrid, Conflict 14):

```text
signbridge-ai/ frontend/ backend/ ai/{preprocessing,features,models,evaluation}/
models/ data/dataset/{raw,processed,annotations} database/migrations/
configs/ scripts/ tests/ docs/ deploy/ docker/ .env.example
```

Phase order is strictly chronological: each phase starts only after the previous phase's verification gate passes. Within a phase, tasks run in listed order unless marked [parallelizable].

---

## Phase 0 — Planning & Setup (entry; no dependencies)

**Purpose:** freeze what gets built so downstream work never re-debates scope, vocab, stack, or IDs.

**Task T0.1 — Freeze MVP-50 vocabulary + class map (Owner: Project + AI/ML).**
Select 30 daily words/greetings (dynamic), 10 digits 0–9, 10 high-use letters (e.g. A,B,C,E,H,I,L,N,O,S). Assign `label → ISL_001…ISL_050` in `data/dataset/annotations/class_map.csv`. Apply cut rule: any class with <15 clips across ≥10 pooled signers moves to v1.1 queue. Patch glossary: `sequence` = 45-frame buffer for exactly one isolated sign (kills the sequence-vs-sentence ambiguity, Conflict 13).

**Task T0.2 — Create repo + CI + branch protection (Owner: Technical).**
Scaffold merged-hybrid layout above. Protect `main`/`develop`, enforce Conventional commits (`feat/fix/refactor/test/docs/perf/security/chore`), stand up CI (ruff/black, mypy, pytest, jest, secrets-scan, Hadolint). [parallelizable with T0.1 after layout agreed].

**Task T0.3 — Lock env + dependencies (Owner: Technical).**
Write `.env.example` (`APP_ENV, DATABASE_URL, MODEL_VERSION=SBAI-MDL-ISL-1.0.0, SEQ_LEN=45, FEAT_DIM=189, CORS_ORIGINS`). Pin `requirements.txt` (TF/Keras, MediaPipe, OpenCV, FastAPI, Uvicorn, SQLAlchemy, Alembic, PyJWT, numpy/scipy) + `package.json` (React+TS, Tailwind, axios, WS client, Jest/RTL/Playwright). Pin Python 3.11. [parallelizable with T0.1].

**Task T0.4 — Close all 17 conflict flags in docs (Owner: Project).**
Flip UC-07/10/11/12/13 + US-014/015/016/017/018/025 to MVP; write canonical API list into `07_API_Contract.md`; write DB baseline into `08`; write retention (90/180/30/30) + RACI; delete every `[Enter]/[Confirm]/[Define]` on MVP paths. Depends on T0.1 (vocab + IDs must exist first).

**Task T0.5 — Board + risk watch (Owner: Project).**
Create M0–M8 milestone board, assign every task an owner per RACI, open risk watch (accuracy shortfall, unseen-signer drop, scope creep, latency overrun, tracking loss) with KRIs (acc/F1, p95 latency, FPS, Critical count). Depends on T0.4.

**Phase 0 outcomes:** `class_map.csv` (50 rows), green CI repo, locked env/deps, zero open MVP flags in docs, owned board.
**Phase 0 verification gate (M0, signer: Business Owner):** fresh `git clone → pip install → npm install → pytest -q + npm test` green on stubs; `grep -r "\[Enter\]\|\[Confirm\]\|\[Define\]" Docs/` returns nothing on MVP paths; RTM shows zero `Future` among MVP IDs (UC-07/10/11/12/13, US-014–018/025). No Phase 1 work starts until M0 signed.

---

## Phase 1 — Foundation (depends on: P0 M0)

**Purpose:** running skeleton of API + DB + UI + containers that every later phase plugs into.

**Task T1.1 — FastAPI skeleton + error contract (Owner: Backend).**
Implement `GET /health` (no auth), `GET /api/v1/model` stub (`{model_id: signbridge-lstm-v1, seq_len: 45, feat_dim: 189}`), and the standard envelopes: success `{success, prediction:{class_id,label,confidence}, status, model_version, processing_time_ms}` and error `{success:false, error:{code,message,details}, request_id}`. Add request-id middleware + JSON logging (no frames/tokens/PII).

**Task T1.2 — PostgreSQL + Alembic v1 + seed (Owner: Backend).**
Migrate all 9 Doc-08 tables + `sign_assets(asset_id, class_id FK, type, uri)` + missing FKs (`sessions.user_id`); seed 50 `sign_classes` rows from `class_map.csv` (label UNIQUE, `sign_type` static/dynamic, handedness). Depends on T0.1 + T1.1 (needs class list + app config).

**Task T1.3 — Frontend shell (Owner: Frontend).** [parallelizable with T1.2]
Landing page, camera-permission screen, router, Tailwind design tokens, typed API client for `/health`, `/model`, `/classes`, global error/toast handling for the error envelope.

**Task T1.4 — Docker single-server + observability (Owner: Technical).**
`docker/` compose (`frontend`, `backend`, `db`), healthchecks, structured logs, `/health`-based readiness. Depends on T1.1–T1.3.

**Phase 1 outcomes:** versioned API stub, migrated + seeded PG, shell UI calling live stubs, one-command compose stack.
**Phase 1 verification gate (M1, signer: QA):** `docker compose up` → `/health 200`, `/model` returns stub version, `/classes` count == 50; Alembic `upgrade head` then `downgrade -1` then `upgrade` clean; Playwright smoke loads landing + permission screen; coverage ≥80% on new code; log-redaction test (no frame bytes/PII in logs) passes. P2 may start its download task (T2.0) in parallel with T1.2+, but T2.1+ needs M1's seeded class list.

---

## Phase 2 — Dataset & CV Pipeline (depends on: P1 M1 for class list; T2.0 download may overlap P1)

**Purpose:** frozen, leak-free `(45,189)` tensor factory from filtered public data — no self-recording per owner waiver.

**Task T2.0 — Selective download (Owner: AI/ML).**
Never pull full 180 GB. ISL500 filtered to MVP-50 via `snapshot_download(allow_patterns=["Videos/<user>/<word>_*", "Landmarks/MediaPipe/<user>/<word>_*", "MappingFiles/*"])` (~2–4 GB; full 159 GB at https://huggingface.co/datasets/ISL500/ISL-DATA, research-only). INCLUDE needed categories + `Train_Test_Split/` (~1 GB smoke via INCLUDE-50, ~12 GB full; CC-BY-4.0 at https://huggingface.co/datasets/manojkumarcs/INCLUDE_Dataset). ISLRTC `Alphabets/` + `Numbers/` only (~5–8 GB of 75 GB; MIT re-encode / NDSAP original at https://huggingface.co/datasets/suneetpaul/Indian_Sign_Language_Data.gov_Rencoded). Day-1 shortcut: `isl-isolated-40words` (~1 GB, 642 clips/40 glosses) to green the loop while ISL500 streams.

**Task T2.1 — Curate → `CURATION-v1.0` (Owner: AI/ML).**
Harmonize labels across sources into `class_map.csv` spellings; tag every clip `source/signer/session`; 2nd-frame-hash dedup across mirrors; drop ISLRTC frames with overlaid pictures/text; emit `ISL-SBAI-v1.0.0` manifest + source commit hashes + checksums. Provenance note: Doc-04/23/33 live-collection rule waived by owner; reproducibility carried by curation versioning. Depends on T2.0.

**Task T2.2 — Landmark service (Owner: AI/ML).**
Reuse ISL500 shipped MediaPipe `.h5` verbatim where present; run MediaPipe Hands/Holistic only on INCLUDE/ISLRTC raw (OpenCV BGR→RGB resize, 21 pts/hand validation, wrist-relative normalization, reject on blur/low-res/tracking-lost with logged reason). Train and inference share one code path (parity). Depends on T2.1.

**Task T2.3 — Feature builder → `FV-1.0` (Owner: AI/ML).**
Per clip: spatial (pairwise distances, joint angles, bbox, orientation) + temporal (`v=(x_t−x_{t−1})/dt`, `a=(v_t−v_{t−1})/dt`, displacement, trajectory) = exactly 189 dims; uniform-sample if long / pad+mask if short to exactly 45 frames; Float32, NaN/Inf guard; emit `X(N,45,189)/y/signers/source` (~30 MB for MVP-50). Static letters encode as 45-frame holds; dynamic words as trajectories — identical shape. Depends on T2.2.

**Task T2.4 — Pooled signer-split → `SPLIT-1.0` (Owner: AI/ML).**
Pool signer IDs (ISL500 U01–U15 + INCLUDE S01–S07 ≈ 22 effective) → 70/15/15 **by signer with zero cross-split overlap**; freeze test checksums; augment train-only (translate ±0.1, scale, small rotate, speed jitter, frame-drop, coordinate noise; no handedness-flipping mirror); batch sampling weights 70% ISL500 / 20% INCLUDE / 10% ISLRTC-letters. Depends on T2.3.

**Phase 2 outcomes:** `CURATION-v1.0` + `FV-1.0` + `SPLIT-1.0`, deterministic tensor factory, frozen test set.
**Phase 2 verification gate (M2, signer: AI/ML lead + dataset QC report):** per-class clip counts ≥15 across ≥10 signers (else class cut to v1.1 with record); unit tests green (1/2-hand detect, normalization, velocity/accel math, padding/windowing, tensor `(45,189)` shape/dtype/mask); 10-sample landmark viz montage reviewed; leakage script asserts signer intersection across splits == ∅; frozen test checksums recorded. No training beyond smoke runs until M2 signed.

---

## Phase 3 — AI Model (depends on: P2 M2)

**Purpose:** the single trained artifact of the whole project plus its fitted decision policy.

**Task T3.0 — Smoke baseline (Owner: AI/ML).**
Overfit-one-batch sanity + 5-epoch run on starter-40/INCLUDE-50 (~700 clips) to prove loss decreases and serving path works before the full burn. [Do first, ~5–10 min on T4.]

**Task T3.1 — Train LSTM + GRU challenger (Owner: AI/ML).**
Architecture (locked): `Input(45,189) → LSTM-128 → Dropout 0.3 → LSTM-64 → Dense-64 ReLU → Dropout → Softmax(50)`; loss categorical/sparse cross-entropy (class-weighted if imbalanced); Adam 1e-3 + ReduceLROnPlateau/cosine; batch 32; ≤150 epochs; **early-stop patience 15 on val macro-F1**; fixed seeds; checkpoint best-only; log every run as `EXP-YYYY-NNN` (keep failures). One GRU run, identical protocol, as rollback candidate. Transformer explicitly deferred. Depends on T3.0 + M2 tensors. (~20–40 min T4 / 4–8 h CPU-only for ~1k MVP clips.)

**Task T3.2 — Calibrate decision policy on val only (Owner: AI/ML).**
Grid-search confidence threshold + temporal smoothing/debounce window on **validation split only**; emit policy file mapping scores → `Accepted / Uncertain / No-Sign / Tracking-Lost`; enforce UX rule (low-confidence never shown as definitive). Depends on T3.1.

**Task T3.3 — Frozen-test + robustness + cross-dataset eval (Owner: AI/ML + QA).**
Single scored run on frozen test: accuracy, macro-F1, per-class P/R, confusion matrix, signer-independent delta (held-out signers), robustness battery (light/backlight/clutter/occlusion/speed/distance/angle/frame-drop), latency p50/p95/p99 + sustained FPS + model size. Cross-dataset check: ISL500-trained weights scored on INCLUDE-full. Depends on T3.2.

**Task T3.4 — Register + export + parity (Owner: AI/ML).**
Register `SBAI-MDL-ISL-1.0.0` (weights + scaler + class-map + policy + dataset/split/feature/code/env versions) + SHA-256; export SavedModel (+TFLite optional); assert export≡training predictions bit-exact on 200-sample probe; write eval report + model card (intended use + limits). Depends on T3.3.

*Scope fence: trains = LSTM (+GRU spare). Fitted (no backprop) = scaler (train-only), threshold/window (val-only), confusion stats. Frozen = MediaPipe/MMPose. Untrained services = TTS engine, `sign_assets` lookup. Not in MVP = Transformer, sentence/continuous, generation, personalization.*

**Phase 3 outcomes:** approved `SBAI-MDL-ISL-1.0.0`, eval report, model card.
**Phase 3 verification gate (M3, signers: AI/ML + QA, Security/Privacy non-veto):** frozen-test **accuracy ≥90%, macro-F1 ≥0.90**, no critical-class collapse; inference **<200ms p95**, sustained **≥15 FPS** on target hardware; `GET /api/v1/model` serves the registered version string; parity probe diff == 0; eval report + `EXP` log archived. P4 prediction APIs unblock only after M3 (stubs allowed earlier).

---

## Phase 4 — Backend & DB (depends on: P3 M3 for real artifact; stubs from P1 allow early scaffolding)

**Purpose:** contract-complete server behind the canonical API.

**Task T4.1 — Prediction APIs (Owner: Backend).**
`POST /api/v1/predict | /predict/sequence | /predict/image | /predict/video` (+ `POST /api/v1/recognize` thin alias, same handler); strict validation (feat_dim must equal 189 else 422 `expected 189 got N`; NaN/Inf → 422; oversize → 413); per-IP/token rate limits + WS frame-rate caps; `processing_time_ms` in every response; no model paths/PII in errors. Depends on T3.4.

**Task T4.2 — Session + vocabulary APIs (Owner: Backend).**
`POST /api/v1/session` → `sess_*`, `DELETE /api/v1/session/{id}` (+ `/reset` alias); in-memory frames (never persisted) + DB writes for `sessions/predictions`; `GET /api/v1/classes` (== 50, from DB seed). Depends on T1.2 + T4.1.

**Task T4.3 — MVP-kept speech/vocab APIs (Owner: Backend).**
`POST /api/v1/tts` (off-the-shelf engine wrapper) and `POST /api/v1/text-to-sign` (`sign_assets` URI lookup + `unsupported_word` flag path). Depends on T1.2 (`sign_assets` rows) + T4.1.

**Task T4.4 — Admin APIs + authN/Z (Owner: Backend + Security).**
Model list/get/promote/rollback, health detail, deployment log; JWT/OAuth + RBAC (admin-only mutations), audit-log writes on every mutation; keep `GET /health|/model|/classes` open/demo per split rule. Depends on T3.4 + T4.1.

**Task T4.5 — Retention + redaction jobs (Owner: Backend).**
Nightly sweep enforcing sessions 90d / predictions 180d / api_logs 30d / backups 30d; PII/IP-hash redaction in logs. Depends on T1.2.

**Phase 4 outcomes:** all canonical endpoints live against the real model + RBAC + retention.
**Phase 4 verification gate (M4, signers: Technical + Security):** contract matrix green (200/400/401/403/404/413/415/422/429); invalid-auth → 401/403 (P0 SEC tests); dim-mismatch → 422 with `expected 189`; `TC-DB-008/TC-PRI-008` retention enforced (expired rows actually purged); audit rows written for admin mutations. P5 may scaffold against OpenAPI mocks before M4, but live UI tests need M4.

---

## Phase 5 — Frontend & UX (depends on: P4 M4 for live APIs; mock-driven scaffolding allowed earlier)

**Purpose:** complete responsive app including the voted-in history + admin screens.

**Task T5.1 — Live recognition screen (Owner: Frontend).**
Camera preview + 7-state machine (`Ready/Tracking/Recognized/Uncertain/No-Sign/Tracking-Lost/Error`) + 32–48px result label + confidence + Start/Stop/Speak/Clear/Feedback; camera ready 2–3s, UI interactions <100ms, non-blocking async inference, visible camera-active indicator.

**Task T5.2 — Result + full history (Owner: Frontend).**
Active-session conversation view + persistent history page (paginated, filterable) + per-item and wipe-all delete + privacy notice; reset/clear returns to Ready. Depends on T4.2.

**Task T5.3 — Vocabulary + text-to-sign + TTS + settings/help (Owner: Frontend).**
Searchable sign cards (static/dynamic tagged), text-to-sign visual view with unsupported-word messaging, speak/copy/repeat controls, settings (camera, threshold display, speech rate, theme, history toggle), help/onboarding, responsive mobile-web camera-first layout + bottom nav. Depends on T4.3.

**Task T5.4 — Full admin UI + accessibility (Owner: Frontend).**
RBAC-gated version list, promote/rollback buttons with confirm + audit receipt, health/deployment log viewers; WCAG 2.1 AA throughout (contrast, no color-only status, keyboard paths, screen-reader labels, visible focus, reduced-motion, 16px minimum). Depends on T4.4.

**Phase 5 outcomes:** MVP-complete responsive UI with history + admin.
**Phase 5 verification gate (M5, signer: QA):** Playwright E2E green (permission grant/deny → preview → sign → result → speak → feedback → reset → history write/delete → admin promote/rollback as admin + 403 as non-admin); axe accessibility scan clean; UI-UX checklist + User Manual §14 workflows (Basic/Audio/Reset) all pass. No integration sign-off until M5.

---

## Phase 6 — System Integration (depends on: P4 M4 + P5 M5)

**Purpose:** one working single-server system, not a set of passing parts.

**Task T6.1 — Wire the full path (Owner: Technical).**
`frontend ↔ REST + WS /api/v1/stream` (message types start/frame/prediction/status/error/stop/heartbeat) ↔ inference service (co-located container) ↔ PG; stateless FastAPI; rolling 45-frame buffer reset on tracking-lost/stop/session-end.

**Task T6.2 — End-to-end MVP journeys (Owner: Technical + QA).**
Isolated sign→text→speech, text→sign (incl. unsupported-word path), history write/delete, admin promote/rollback propagation to live traffic; every prediction carries `sequence_id + model_version`. Depends on T6.1.

**Task T6.3 — Config + compatibility record (Owner: Technical).**
Flag threshold/seq-len/fps via env without code change; record model↔preprocessing↔app compatibility triple; fail-fast on mismatch. Depends on T6.1.

**Phase 6 outcomes:** integrated single-server MVP with traced predictions.
**Phase 6 verification gate (M6, signer: Technical):** 10-sign staged script ≥90% correctly displayed end-to-end; WS drop/reconnect recovers without ghost predictions; DB chain `sessions → predictions → feedback` FK-linked for every E2E run; integration + WS suites green; `Session→DB` gate from Roadmap passes.

---

## Phase 7 — Testing & Hardening (depends on: P6 M6)

**Purpose:** prove gates on the frozen release candidate and close every test-level gap.

**Task T7.1 — Full test battery (Owner: QA + Security/Privacy).**
Unit (pytest) → component (preproc/inference/API/UI mocked) → integration → system E2E (Playwright) → acceptance; frozen-test scoring rerun; Locust/k6 load + stress + soak; security (SQLi via ORM-only, malicious upload sandbox, secrets-scan, CORS/host review) + privacy (transient-frames proof, consent copy, deletion round-trip) + a11y re-scan.

**Task T7.2 — Governance audit (Owner: QA).**
Test-ID migration to unified `TC-FUN…` scheme with RTM links (BR→UC→US→TC→evidence); model lifecycle mapping (`Candidate/Validated/Approved/Deployed` ↔ DB `staging/active`); branch/commit lint history clean.

**Task T7.3 — Freeze RC `v0.5` (Owner: Release).**
Immutable bundle: app image + `SBAI-MDL-ISL-1.0.0` + `CURATION-v1.0` + `SPLIT-1.0` + configs + checksums + eval report. Depends on T7.1–T7.2.

**Phase 7 outcomes:** release candidate with evidence pack.
**Phase 7 verification gate (M7, signers: QA + Security/Privacy veto):** all release gates re-held on RC (acc/F1/latency/FPS/coverage/0 Criticals); signer-independent + robustness reports attached; API RPS + WS events/s within budget; soak shows no memory growth; pen-test 0 High open. P8 blocked on M7 veto clearance.

---

## Phase 8 — Deployment (depends on: P7 M7)

**Purpose:** safe, observable, reversible production.

**Task T8.1 — Promote to prod (Owner: Technical + Release).**
Staging → prod via Blue-Green/Canary; HTTPS/WSS + HSTS; secrets in manager (never git); Nginx/LB; tested backups; prior approved model retained beside new for instant rollback.

**Task T8.2 — Observe + rehearse (Owner: Technical).**
Dashboards/alerts: health, API p50/p95/p99, inference <200ms, FPS, CPU/mem/GPU/VRAM, WS drops, DB connections; structured logs; smoke + full rollback drill on prod-like data.

**Phase 8 outcomes:** live `v1.0` + runbook + rollback path.
**Phase 8 verification gate (M8, signer: Business Owner):** prod smoke green (`/health`, `/model`, 1 live prediction, TTS, text-to-sign, history write/delete, admin health view); rollback to prior `SBAI-MDL` demonstrated <5 min; RPO 24h / RTO 4h attested from backup restore test. Only M8 authorizes public announcement.

---

## Phase 9 — Post-release (depends on: P8 M8; ongoing, no gate blocks it)

**Purpose:** controlled evolution without regressions.

**Task T9.1 — Drift + feedback triage (Owner: AI/ML + Project, monthly).**
Review prediction confidences, confusion hotspots, user feedback rows, latency/FPS trends; queue data adds (remaining 16 letters → next 100 words → v1.1 150-class plan).

**Task T9.2 — Controlled updates (Owner: Release).**
Any model/data/config change repeats P3→P7 gates on a new `EXP` + RC before P8 promotion. Native-app, on-device inference, and sentence/continuous translation stay research tracks, never silent hotfixes.

**Phase 9 outcomes:** monthly review notes + versioned `1.x` candidates.
**Phase 9 verification (continuous):** each candidate shows gate-comparison table (old vs new on frozen test) + rollback plan; no prod push without M7-equivalent re-sign.

---

## Appendix A — Canonical API v1 (Conflict 4)

```text
GET  /health
GET  /api/v1/model | GET /api/v1/classes
POST /api/v1/predict (+ /recognize alias) | /predict/sequence | /predict/image | /predict/video
POST /api/v1/session + DELETE /api/v1/session/{id} (+ /session/reset alias)
POST /api/v1/tts + POST /api/v1/text-to-sign
WS   /api/v1/stream?session_id=
```

## Appendix B — DB baseline (Conflict 5)

PostgreSQL-only; Doc-08 9 tables + `sign_assets(asset_id, class_id FK, type, uri)`; `class_id = ISL_001…`; add missing DDL (`feedback`, `api_logs`, `audit_logs`, `model_deployments`, `sessions.user_id` FK); blobs in object storage.

## Appendix C — MVP-50 vocabulary (locked)

30 daily words (dynamic) + 10 digits + 10 high-use letters in one Softmax(50). Cut rule enforced in T0.1/T2.4.

## Appendix D — Dataset combination (locked, no self-recording)

ISL500 filtered (~2–4 GB, primary, research-only) + INCLUDE cats + splits (~1/12 GB, CC-BY-4.0, benchmark) + ISLRTC Alphabets/Numbers only (~5–8 GB, MIT/NDSAP) + starter-40 shortcut (~1 GB). Skip for training: CISLR (eval-only), iSign/ISL-CSLTR (sentence future), Kaggle static sets (sanity only).

## Appendix E — What trains vs what doesn't (locked)

Trained: LSTM (+GRU spare). Fitted: scaler, threshold/smoothing, confusion stats. Frozen: MediaPipe/MMPose. Untrained services: TTS, asset lookup, session/auth/history/admin. Not in MVP: Transformer, sentence/continuous, generation, personalization.
