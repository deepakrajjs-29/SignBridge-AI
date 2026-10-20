<!-- Source: 24_Model_Versioning_Experiment_Log_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# SIGNBRIDGE AI

## MODEL VERSIONING & EXPERIMENT LOG

*Camera-Based Indian Sign Language Recognition System*

| Field | Value |
| --- | --- |
| Document ID | SBAI-MVEL-001 |
| Document Number | 24_Model_Versioning_Experiment_Log |
| Version | 1.0 |
| Status | [Draft / Review / Approved] |
| Prepared By | [Enter name] |
| Reviewed By | [Enter name] |
| Approved By | [Enter name] |
| Date | [Enter date] |

*Editable project documentation • SignBridge AI*

## Table of Contents

1. Purpose

2. Scope

3. Objectives

4. Versioning Principles

5. Model Lifecycle

6. Model Artifact Structure

7. Model Naming Convention

8. Semantic Versioning Rules

9. Model Status Definitions

10. Model Registry

11. Model Metadata

12. Model Lineage

13. Dataset Version Tracking

14. Feature Version Tracking

15. Experiment Identification

16. Experiment Naming Convention

17. Experiment Lifecycle

18. Experiment Log Requirements

19. Experiment Configuration

20. Hyperparameter Log

21. Training Run Log

22. Validation Log

23. Evaluation Log

24. Error and Confusion Log

25. Robustness Experiment Log

26. Threshold Calibration Log

27. Model Comparison Log

28. Model Selection Record

29. Approval and Promotion Workflow

30. Deployment Version Tracking

31. Rollback and Recovery

32. Reproducibility Requirements

33. Artifact Integrity

34. Storage and Retention

35. Access Control

36. Security and Privacy

37. Experiment Reproducibility Checklist

38. Change Impact Analysis

39. Failed Experiment Handling

40. Monitoring Post-Deployment

41. Example Experiment Register

42. Example Model Registry

43. Standard Experiment Log Template

44. Standard Model Version Record

45. Traceability

46. Editable Project Parameters

47. Assumptions and Constraints

48. Open Questions

49. Acceptance Checklist

50. Related Documents

51. Version History and Approval

## 1. Purpose

This document defines how SignBridge AI machine-learning models and training experiments are uniquely identified, recorded, compared, approved, promoted, deployed, monitored, and retired. It establishes model lineage from dataset and feature versions through training experiments to production deployments and provides reusable editable logs for project execution.

## 2. Scope

- Offline model development and experimentation.
- Model artifact naming and semantic versioning.
- Dataset, feature, code, configuration, and environment lineage.
- Training, validation, test, robustness, and threshold experiments.
- Model registry and promotion states.
- Deployment, rollback, retirement, and archival.
- Experiment reproducibility, integrity, security, privacy, and auditability.
## 3. Objectives

- Make every model artifact uniquely identifiable.
- Make every experiment reproducible from recorded metadata.
- Prevent accidental use of an unapproved or incompatible model.
- Support objective comparison of model candidates.
- Maintain a clear lineage between data, code, experiments, models, and deployments.
- Provide a historical record of why a model was selected or rejected.
## 4. Versioning Principles

| Principle | Rule |
| --- | --- |
| Immutable artifacts | A released model artifact is never silently overwritten. |
| Traceability | Every model points to dataset, feature, code, and experiment versions. |
| Compatibility | Model input schema and class mapping must be compatible with runtime. |
| Reproducibility | Required training metadata is stored with each experiment. |
| Human approval | Promotion to production requires explicit review. |
| Integrity | Checksums identify exact artifacts. |
| Rollback | Previously approved versions remain recoverable. |
| Least privilege | Only authorized users/processes can promote or retire models. |

## 5. Model Lifecycle

| Stage | Meaning | Allowed Use |
| --- | --- | --- |
| Development | Model under active experimentation | Training/evaluation only |
| Candidate | Experiment has produced a usable artifact | Controlled testing |
| Validated | Evaluation requirements completed | Review/staging |
| Approved | Human review completed | Eligible for deployment |
| Deployed | Approved version active in an environment | Production inference |
| Retired | No longer active but retained for traceability | Rollback/archive |
| Rejected | Failed acceptance or review | No deployment |
| Archived | Retained for historical/research purposes | Reference only |

## 6. Model Artifact Structure

| Artifact | Contents |
| --- | --- |
| Model weights | Trained neural-network parameters |
| Architecture/config | Model structure and runtime settings |
| Class mapping | Stable class IDs and labels |
| Feature configuration | Feature version and input dimensions |
| Preprocessing metadata | Normalization/scaling requirements |
| Training metadata | Dataset, split, hyperparameters, seed |
| Evaluation summary | Accuracy, F1, confusion matrix reference, latency |
| Version metadata | Model ID/version/status |
| Integrity | SHA-256 or approved checksum |
| Documentation | Model card/release notes where required |

## 7. Model Naming Convention

Recommended format: SBAI-MDL-<DOMAIN>-<MAJOR>.<MINOR>.<PATCH>.

| Part | Example | Meaning |
| --- | --- | --- |
| Project | SBAI | SignBridge AI |
| Artifact type | MDL | Model |
| Domain | ISL | Indian Sign Language recognition |
| Major | 1 | Breaking class/input/architecture contract change |
| Minor | 1 | Backward-compatible model improvement |
| Patch | 1 | Bug fix/retraining with unchanged contract |

Example: SBAI-MDL-ISL-1.2.0

## 8. Semantic Versioning Rules

| Change | Version Impact | Example |
| --- | --- | --- |
| Class set changed incompatibly | Major | 1.x → 2.0 |
| Feature schema changed incompatibly | Major | 1.x → 2.0 |
| Inference contract changed | Major | 1.x → 2.0 |
| Improved model, same contract | Minor | 1.1 → 1.2 |
| Retraining with corrected bug/data while contract remains stable | Patch or Minor | 1.2.0 → 1.2.1 |
| Threshold-only configuration change | Separate config version or patch | 1.2.0 + CFG-2 |
| Documentation-only change | No model version change | — |

## 9. Model Status Definitions

| Status | Entry Criteria | Exit Criteria |
| --- | --- | --- |
| Development | Experiment active | Candidate/Rejected |
| Candidate | Artifact generated and loads successfully | Validated/Rejected |
| Validated | Evaluation completed | Approved/Rejected |
| Approved | Human review completed | Deployed/Retired |
| Deployed | Activated in target environment | Retired/Rolled back |
| Retired | No longer active | Archived |
| Rejected | Acceptance failed | Archived or new experiment |

## 10. Model Registry

The model registry is the authoritative index of model artifacts, metadata, lifecycle state, deployment state, and lineage.

| Registry Field | Required |
| --- | --- |
| Model ID | Yes |
| Model version | Yes |
| Status | Yes |
| Artifact URI/path | Yes |
| Checksum | Yes |
| Dataset version | Yes |
| Feature version | Yes |
| Code commit | Yes |
| Experiment ID | Yes |
| Metrics | Yes |
| Class mapping version | Yes |
| Created/approved/deployed timestamps | Yes |
| Reviewer/approver | Yes where applicable |

## 11. Model Metadata

| Metadata Category | Examples |
| --- | --- |
| Identity | Model ID, version, name |
| Architecture | LSTM/GRU/Temporal Transformer |
| Input | Sequence length, feature dimension |
| Output | Class count, class mapping |
| Training | Optimizer, LR, batch size, epochs |
| Dataset | Dataset ID/version/split |
| Performance | Accuracy, precision, recall, macro F1 |
| Runtime | Latency, FPS, memory |
| Governance | Status, owner, approval |
| Integrity | Checksum, artifact size |

## 12. Model Lineage

Required lineage: Dataset Version → Split Version → Feature Version → Code Commit → Experiment ID → Training Run → Model Artifact → Evaluation Report → Approval → Deployment.

Actual model lineage: 1.0.0 (MVP-era) → 2.0.0 (100-class SYNTHETIC stub; production gates NOT cleared) → 3.0.0 (100-class REAL; test 0.8109/0.8062, n=3326; gate Docs/M10_GATE_100REAL.md) → 4.0.0 (109-class REAL ACTIVE; test 0.8129/0.8079, n=3629; gate Docs/M11_GATE_109REAL.md).

| Lineage Node | Identifier Example |
| --- | --- |
| Dataset | tensors_109_real.npz (CURATION-v4.0; 14,826 real ISL500 sequences) |
| Split | SPLIT-109 (annotations/SPLIT-4.0.json + split_idx_109.npz; signer-disjoint 8,800/2,397/3,629) |
| Feature | FV-1.0 (189-D; seq_len 45) |
| Code | Uncommitted M13 working-tree state — commit SHA not pinned in this record |
| Experiment | EXP-2026-004 |
| Run | EXP-2026-004-{lstm,gru}-full history CSVs |
| Model | SBAI-MDL-ISL-4.0.0 (arch ENSEMBLE(LSTM128-LSTM64,GRU128-GRU64)+mirror-TTA,Softmax109; 109 classes ISL_001..ISL_109) |
| Evaluation | Docs/M11_GATE_109REAL.md + Docs/eval/08_final_test.json |
| Approval | M11 gate: Candidate, serving authorized — 0.90 release gates remain open debt (not Approved) |
| Deployment | active_model SBAI-MDL-ISL-4.0.0 (models/registry.json) |

## 13. Dataset Version Tracking

- Record exact dataset snapshot used by every training experiment.
- Store dataset manifest or immutable reference.
- Record additions, removals, relabeling, and quality changes.
- Never refer only to 'latest dataset' in a reproducibility record.
- Document whether data was augmented and which augmentation configuration was used.
## 14. Feature Version Tracking

| Feature Version | Required Information |
| --- | --- |
| FV-1.0 | Landmark normalization rules, spatial/temporal features, tensor shape |
| Change record | Added/removed/modified features |
| Compatibility | Models trained against this feature version |
| Preprocessing code | Commit/reference |
| Scaling | Scaler/statistics source if used |

## 15. Experiment Identification

Every meaningful training or evaluation run should have a unique experiment identifier.

| ID Type | Pattern | Example |
| --- | --- | --- |
| Experiment | EXP-YYYY-NNN | EXP-2026-001 |
| Training Run | RUN-YYYY-EXP-RR | RUN-2026-001-03 |
| Evaluation | EVAL-YYYY-NNN | EVAL-2026-007 |
| Robustness | ROB-YYYY-NNN | ROB-2026-002 |
| Calibration | CAL-YYYY-NNN | CAL-2026-003 |
| Deployment | DEP-YYYY-NNN | DEP-2026-004 |

## 16. Experiment Naming Convention

Recommended format: EXP-<YEAR>-<SEQUENCE>-<SHORT_DESCRIPTION>.

| Example | Meaning |
| --- | --- |
| EXP-2026-001-LSTM-BASE | Initial LSTM baseline |
| EXP-2026-002-GRU-BASE | GRU baseline |
| EXP-2026-003-FEAT-VEL | Velocity feature experiment |
| EXP-2026-004-AUG-TIME | Temporal augmentation experiment |
| EXP-2026-005-THRESH | Confidence threshold experiment |

## 17. Experiment Lifecycle

1. Create experiment record before the run.
1. Freeze or identify dataset and feature versions.
1. Record intended hypothesis and success criteria.
1. Execute training/evaluation.
1. Capture logs, metrics, artifact, and environment metadata.
1. Review results against the predefined criteria.
1. Mark experiment as Completed, Failed, Aborted, or Superseded.
1. Link any resulting model candidate to the experiment.
## 18. Experiment Log Requirements

| Field | Required | Purpose |
| --- | --- | --- |
| Experiment ID | Yes | Unique reference |
| Objective/Hypothesis | Yes | Reason for experiment |
| Dataset version | Yes | Data lineage |
| Feature version | Yes | Input lineage |
| Code commit | Yes | Implementation lineage |
| Configuration | Yes | Reproduction |
| Metrics | Yes | Comparison |
| Artifact | Yes if produced | Model output |
| Environment | Yes | Runtime reproduction |
| Decision | Yes | Keep/reject/further study |
| Reviewer | Recommended | Independent review |

## 19. Experiment Configuration

| Category | Parameters to Record |
| --- | --- |
| Data | Dataset, split, class count, sample counts |
| Features | Feature version, normalization, sequence length |
| Architecture | Model type, layers, hidden units |
| Optimization | Optimizer, LR, scheduler |
| Training | Batch, epochs, patience |
| Regularization | Dropout, weight decay |
| Augmentation | Methods and probabilities |
| Thresholding | Calibration method/threshold |
| Runtime | Framework/library versions |
| Hardware | CPU/GPU/RAM |

## 20. Hyperparameter Log

| Hyperparameter | Value | Search Range | Selected |
| --- | --- | --- | --- |
| Sequence length | [Enter] | 30–60 | [ ] |
| Hidden units | [Enter] | 32–128 | [ ] |
| Layers | [Enter] | 1–3 | [ ] |
| Dropout | [Enter] | 0.2–0.4 | [ ] |
| Learning rate | [Enter] | 1e-4–1e-3 | [ ] |
| Batch size | [Enter] | 16–64 | [ ] |
| Epochs | [Enter] | 50–150 | [ ] |
| Patience | [Enter] | 10–20 | [ ] |
| Weight decay | [Enter] | Optional | [ ] |
| Augmentation strength | [Enter] | Controlled range | [ ] |

## 21. Training Run Log

| Run Field | Value |
| --- | --- |
| Run ID | [Enter RUN ID] |
| Experiment ID | [Enter EXP ID] |
| Start Time | [Enter] |
| End Time | [Enter] |
| Dataset Version | [Enter] |
| Feature Version | [Enter] |
| Code Commit | [Enter] |
| Model Architecture | [Enter] |
| Epochs Completed | [Enter] |
| Best Epoch | [Enter] |
| Best Validation Metric | [Enter] |
| Final Training Loss | [Enter] |
| Final Validation Loss | [Enter] |
| Artifact Path | [Enter] |
| Checksum | [Enter] |
| Run Status | [Completed / Failed / Aborted] |

## 22. Validation Log

| Metric | Training | Validation | Notes |
| --- | --- | --- | --- |
| Loss | [ ] | [ ] | [ ] |
| Accuracy | [ ] | [ ] | [ ] |
| Precision | [ ] | [ ] | [ ] |
| Recall | [ ] | [ ] | [ ] |
| Macro F1 | [ ] | [ ] | [ ] |
| Per-class minimum | [ ] | [ ] | [ ] |
| Epoch of best score | — | [ ] | [ ] |

## 23. Evaluation Log

| Metric | Test Result | Target | Pass/Review |
| --- | --- | --- | --- |
| Accuracy | 0.812896 (frozen test, n=3629, single touch; predecessor 3.0.0: 0.8109, n=3326) | ≥90% target | NOT MET — open release debt (M11) |
| Macro F1 | 0.807865 (3.0.0: 0.8062) | ≥0.90 target | NOT MET — open release debt (M11) |
| Precision | 0.818957 (macro, frozen test) | [Enter target] | Recorded (M13 §7) |
| Recall | 0.812188 (macro, frozen test) | [Enter target] | Recorded (M13 §7) |
| Latency | Ensemble p50 288.99 / p95 318.42 ms (VAL); p50 374.85 / p95 575.22 ms (TEST), per sign window CPU | <200 ms preferred | Exceeds preferred (ensemble); single-model probes 61.86 ms (LSTM) / 64.4 ms (GRU) meet |
| Throughput | Not measured as FPS | ≥15 FPS target | Not measured |
| Model size | Not recorded | [Enter limit] | Not measured |

VAL companion metrics (n=2397, fitted VAL-only, M13 §7): argmax 0.833125, macro-F1 0.828963, ECE 0.028272, Brier 0.250855. Decision policy (accept_threshold 0.57, provisional 0.00, smoothing 5, tta_windows 1, temperature 1.0): commit precision 0.903357 @ coverage 0.820192 (VAL) and 0.895290 @ 0.813172 (TEST); FAR accepted 0.096643 (VAL) / 0.104710 (TEST); VAL counts recognized 1966 / provisional 431 / uncertain 0 / no-sign 0. Sources: Docs/M13_ACCURACY_CALIBRATION.md §7; Docs/eval/08_final_val.json, 08_final_test.json.

All target values are configurable engineering targets and must not be recorded as achieved until measured.

## 24. Error and Confusion Log

| Field | Entry |
| --- | --- |
| Experiment/Model | [Enter] |
| Top confused class pair | [Enter] |
| Confusion count/rate | [Enter] |
| Likely cause | [Data / Landmark / Feature / Model / Threshold / Other] |
| Evidence | [Enter] |
| Proposed action | [Enter] |
| Follow-up experiment | [EXP-ID] |
| Owner | [Enter] |
| Status | [Open / Resolved] |

## 25. Robustness Experiment Log

| Condition | Baseline | Candidate | Change | Decision |
| --- | --- | --- | --- | --- |
| Lighting | [ ] | [ ] | [ ] | [ ] |
| Background | [ ] | [ ] | [ ] | [ ] |
| Distance | [ ] | [ ] | [ ] | [ ] |
| Signing speed | [ ] | [ ] | [ ] | [ ] |
| Occlusion | [ ] | [ ] | [ ] | [ ] |
| Camera variation | [ ] | [ ] | [ ] | [ ] |
| Hand position | [ ] | [ ] | [ ] | [ ] |

## 26. Threshold Calibration Log

| Field | Value |
| --- | --- |
| Calibration ID | M13 calibration record (Docs/M13_ACCURACY_CALIBRATION.md; scripts/calibrate_v4.py) |
| Model Version | SBAI-MDL-ISL-4.0.0 |
| Calibration Dataset | SPLIT-109 validation set (n=2397), fitted VAL-only; frozen test touched once |
| Objective | Fit accept/provisional thresholds, smoothing, TTA windows, and temperature on VAL |
| Candidate Thresholds | accept sweep on VAL; temperature candidates fitted and compared by ECE |
| Selected Threshold | accept_threshold 0.57; provisional_threshold 0.00; smoothing 5; tta_windows 1; temperature 1.0 (identity — calibration fit rejected, already calibrated) |
| Recognition Rate | VAL counts: recognized 1966 / provisional 431 / uncertain 0 / no-sign 0 (n=2397) |
| Uncertain Rate | 0 (VAL) |
| No-Sign Rate | 0 (VAL) |
| False Positive Behavior | FAR accepted 0.096643 (VAL) / 0.104710 (TEST); commit precision 0.903357 @ coverage 0.820192 (VAL), 0.895290 @ 0.813172 (TEST); ECE 0.028272 VAL / 0.022447 TEST |
| Reviewer | Not recorded (artifact: models/SBAI-MDL-ISL-4.0.0/calibration.json + policy.json) |

## 27. Model Comparison Log

| Model | Accuracy | Macro F1 | Latency | FPS | Robustness | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SBAI-MDL-ISL-3.0.0 (100-class real ensemble) | 0.8109 (test n=3326) | 0.8062 | Not measured | Not measured | Not measured | Retired — superseded by 4.0.0 (gate M10) |
| SBAI-MDL-ISL-4.0.0 (109-class real ensemble + mirror-TTA) | 0.8129 (test n=3629) | 0.8079 | p50 374.85 / p95 575.22 ms (TEST, per sign window CPU) | Not measured | Webcam-replay proxy full_sign 0.822/0.736 (M12) | ACTIVE — gate M11; 0.90 release gates open |
| SBAI-MDL-ISL-4.1.0 candidate (GRU + time-jitter, EXP-2026-005) | Not scored to frozen test (val 0.816854 < required 0.833125) | Not scored (val 0.814275 < required 0.828963) | Not measured | Not measured | Not measured | Rejected — FAILED promotion gates, DISCARDED |
| Selected — SBAI-MDL-ISL-4.0.0 + M13 policy (accept 0.57) | 0.812896 argmax; commit precision 0.895290 @ coverage 0.813172 (TEST) | 0.807865 | p50 288.99 / p95 318.42 ms (VAL ensemble) | Not measured | Protocol M13 §13 pending | Deployed policy (Docs/M13 §7) |

## 28. Model Selection Record

| Field | Value |
| --- | --- |
| Selection ID | [SEL-YYYY-NNN] |
| Candidate Model | [Enter version] |
| Baseline Model | [Enter version] |
| Primary Reason | [Enter] |
| Accuracy Evidence | [Report ID] |
| Macro F1 Evidence | [Report ID] |
| Robustness Evidence | [Report ID] |
| Runtime Evidence | [Benchmark ID] |
| Risks/Limitations | [Enter] |
| Decision | [Selected / Rejected / More Study] |
| Reviewer | [Enter] |
| Date | [Enter] |

## 29. Approval and Promotion Workflow

1. Experiment is completed and artifact integrity is verified.
1. Independent evaluation is completed.
1. Model card/release notes are prepared.
1. Model is compared with the approved baseline.
1. Reviewer checks dataset, feature, code, and metric lineage.
1. Authorized approver marks the model Approved.
1. Deployment process promotes the exact approved artifact.
1. Registry records deployment environment and timestamp.

| Gate | Required Evidence |
| --- | --- |
| Candidate | Load test + artifact |
| Validated | Evaluation report |
| Approved | Human review/sign-off |
| Deployed | Deployment record + smoke test |
| Production | Monitoring enabled + rollback available |

## 30. Deployment Version Tracking

| Deployment Field | Value |
| --- | --- |
| Deployment ID | [DEP-ID] |
| Environment | [Dev / QA / Staging / Production] |
| Model Version | [Enter] |
| Artifact Checksum | [Enter] |
| Deployment Date | [Enter] |
| Application Version | [Enter] |
| API Version | [Enter] |
| Feature Version | [Enter] |
| Configuration Version | [Enter] |
| Operator | [Enter] |
| Smoke Test | [Pass/Fail] |
| Rollback Version | [Enter] |

## 31. Rollback and Recovery

- Retain the previously approved production model.
- Record exact artifact checksum for active and rollback versions.
- Rollback only to a model compatible with the deployed feature/API contract.
- Run health and smoke tests after rollback.
- Record rollback reason and impact.
- Open a follow-up investigation/experiment when the cause is model-related.
- Do not delete the failed production version; mark it appropriately in the registry.
## 32. Reproducibility Requirements

| Item | Required Evidence |
| --- | --- |
| Data | Immutable dataset/split reference |
| Features | Feature version and configuration |
| Code | Git commit/tag |
| Environment | Dependency lock/container |
| Seed | Random seed(s) where applicable |
| Config | Complete hyperparameter file |
| Run | Training logs |
| Artifact | Model file + checksum |
| Evaluation | Metrics/report |
| Decision | Selection/approval record |

## 33. Artifact Integrity

- Generate a cryptographic checksum for each released model artifact.
- Verify checksum after transfer and before deployment.
- Store artifact size and format.
- Keep the artifact immutable once approved.
- Reject artifacts whose checksum does not match the registry.
- Optionally sign release artifacts in higher-security environments.
## 34. Storage and Retention

| Artifact/Record | Suggested Retention |
| --- | --- |
| Production models | Retain for lifecycle + rollback period |
| Approved models | Long-term project retention |
| Rejected models | [Enter policy] |
| Experiment logs | [Enter policy; recommended project lifecycle] |
| Training checkpoints | [Enter policy] |
| Evaluation reports | Long-term traceability |
| Dataset manifests | Long-term version references |
| Deployment records | Long-term audit/reference |

## 35. Access Control

| Role | Read Experiments | Create Experiments | Approve Model | Deploy Model | Retire Model |
| --- | --- | --- | --- | --- | --- |
| Developer | Yes | Yes | No | No | No |
| ML Engineer | Yes | Yes | No/As assigned | No/As assigned | No |
| Reviewer | Yes | Optional | Yes | No | No |
| Administrator/Operator | Yes | Optional | Yes if authorized | Yes | Yes |
| CI/CD Service | Limited | No | No | Only approved artifact | No |

## 36. Security and Privacy

- Do not place secrets, API keys, or credentials in experiment logs.
- Do not include unnecessary raw signer images/video in experiment records.
- Reference controlled datasets rather than copying sensitive data into logs.
- Restrict model artifact and experiment storage access.
- Keep audit records for model promotion and deployment actions where required.
- Treat signer metadata and model evaluation data as potentially sensitive.
- Review external experiment-tracking services before uploading project data.
## 37. Experiment Reproducibility Checklist

☐ Experiment ID assigned before execution.

☐ Dataset version recorded.

☐ Split version recorded.

☐ Feature version recorded.

☐ Code commit recorded.

☐ Environment/dependency versions recorded.

☐ Training configuration recorded.

☐ Random seeds recorded where applicable.

☐ Training logs captured.

☐ Validation metrics captured.

☐ Test evaluation captured separately.

☐ Artifact checksum recorded.

☐ Model lineage complete.

☐ Decision and reviewer recorded.

## 38. Change Impact Analysis

| Change | Potential Impact | Required Action |
| --- | --- | --- |
| New class | Model output contract | Major model version + retraining |
| Feature added | Model input schema | New feature version + retraining |
| Feature removed | Model input schema | Compatibility review + retraining |
| Preprocessing change | Input distribution | New feature/preprocessing version + evaluation |
| Training data expansion | Model behavior | New experiment + evaluation |
| Hyperparameter change | Model weights | New experiment/run |
| Model architecture change | Runtime/model contract | New model version |
| Threshold change | Prediction behavior | Calibration record/config version |
| Bug fix in training code | Training behavior | New experiment and version |
| Deployment configuration change | Runtime behavior | Deployment/config record |

## 39. Failed Experiment Handling

- Mark the experiment Failed or Aborted rather than deleting it.
- Record failure reason and diagnostic evidence.
- Retain useful logs and configuration.
- Do not register an invalid artifact as Approved.
- Create a follow-up experiment with a new ID.
- Link the follow-up experiment to the failed run when relevant.
## 40. Monitoring Post-Deployment

| Signal | Purpose |
| --- | --- |
| Prediction confidence distribution | Detect drift or unstable behavior |
| Recognition error/feedback rate | Identify quality changes |
| Latency | Detect runtime degradation |
| Throughput/FPS | Detect performance degradation |
| Error rate | Detect service/model failures |
| Model version usage | Confirm intended deployment |
| Rollback events | Track production instability |
| Data drift indicators | Identify input-distribution changes where measurable |

## 41. Example Experiment Register

| EXP ID | Objective | Model | Dataset | Key Metric | Decision |
| --- | --- | --- | --- | --- | --- |
| EXP-2026-001 | LSTM baseline (MVP-era) | 1.0.0 | v1.0.0 (synthetic-era) | Not recorded in current gate docs | Superseded by 2.0.0 lineage step |
| EXP-2026-002 | GRU baseline (MVP-era) | 1.0.x challenger | v1.0.0 (synthetic-era) | Not recorded in current gate docs | Superseded |
| EXP-2026-003 | 100-class REAL train + LSTM/GRU ensemble promotion | 3.0.0 | CURATION-v3.0 real, SPLIT-3.0 (test n=3326) | Ensemble test acc 0.8109 / macro-F1 0.8062; LSTM challenger 0.7721/0.7664; GRU 0.7676/0.7627 | Kept — promoted as 3.0.0 (gate Docs/M10_GATE_100REAL.md) |
| EXP-2026-004 | 109-class REAL train; LSTM vs GRU challengers + deployed ensemble | 4.0.0 | tensors_109_real.npz, SPLIT-109 8,800/2,397/3,629 | Ensemble test acc 0.8129 / macro-F1 0.8079; GRU winner 0.8057/0.8012; LSTM challenger 0.7567/0.7506 | Kept — promoted as 4.0.0 ACTIVE (gate Docs/M11_GATE_109REAL.md; 0.90 gates open) |
| EXP-2026-005 | GRU + time-jitter retrain (candidate 4.1.0) | 4.1.0 candidate | tensors_109_real.npz, SPLIT-109 | val macro-F1 0.814275 / val acc 0.816854, both below required 0.828963 / 0.833125 | FAILED promotion gates — DISCARDED; backups models/_backup_4.0.0_pretrain/ + data/dataset/_backup_pretrain/ |

Rejected gates (closed investigations, no promotion; numbers from M13 and Docs/eval): TTA tta_windows=3 — gate FAIL (Δacc −0.0359 vs windows=1; p95 371.65 ms > 300 ms budget) → tta_windows stays 1 (Docs/eval/05_val_w1.json, 05_val_w3.json); motion-energy static trim — webcam-replay full_sign 0.835 → 0.768 (visible-correct 0.741 → 0.613) FAIL → reverted (Docs/eval/10_p1trim_gate_after.txt); temperature calibration fit — rejected, T=1.0 identity kept because model already calibrated (VAL ECE 0.028272).

## 42. Example Model Registry

Real registry shape (models/registry.json; active_model = SBAI-MDL-ISL-4.0.0):

| Model Version | Status | Dataset | Feature | Macro F1 | Latency | Checksum |
| --- | --- | --- | --- | --- | --- | --- |
| SBAI-MDL-ISL-2.0.0 | Rejected — registered SYNTHETIC-trained stub; production gates NOT cleared | SYNTHETIC (stub eval only; acc 1.0 is invalid for release) | FV-1.0 | n/a (synthetic) | Not recorded | sha256_lstm fbe041e38921485c4b7596ac1ddf92c2400f8adb9660ec03d11c457cceb70a66 |
| SBAI-MDL-ISL-3.0.0 | Retired — superseded by 4.0.0 (gate M10) | CURATION-v3.0 real, SPLIT-3.0 (test n=3326) | FV-1.0 | 0.8062 (acc 0.8109) | Not recorded | sha256_lstm bb4b09ee92f76d2ecb19a182f74eea6c6a0ff4d808bb39ca5909d792338591de |
| SBAI-MDL-ISL-4.0.0 | ACTIVE (serving; status Candidate per M11 — 0.90 gates open) | tensors_109_real.npz, SPLIT-109 8,800/2,397/3,629 (test n=3629) | FV-1.0 (189-D, T=45) | 0.8079 (acc 0.8129) | p50 288.99 / p95 318.42 ms (VAL); p50 374.85 / p95 575.22 ms (TEST), per sign window CPU | sha256_lstm 3d2a8a0d8afa06fd7c84bd0320e60db5d7355ace84fea48c857feba05ad4a052 |

Registry facts: arch "ENSEMBLE(LSTM128-LSTM64,GRU128-GRU64)+mirror-TTA,Softmax109"; 109 classes ISL_001..ISL_109; seq_len 45; feat_dim 189; export_parity_200 true; previous_model SBAI-MDL-ISL-3.0.0; per-version detail under models{} in models/registry.json.

## 43. Standard Experiment Log Template

| Field | Value |
| --- | --- |
| Experiment ID | [EXP-YYYY-NNN] |
| Experiment Name | [Enter] |
| Date | [Enter] |
| Owner | [Enter] |
| Objective/Hypothesis | [Enter] |
| Success Criteria | [Enter] |
| Dataset Version | [Enter] |
| Split Version | [Enter] |
| Feature Version | [Enter] |
| Code Commit | [Enter] |
| Model Architecture | [Enter] |
| Hyperparameters | [Enter/reference config] |
| Augmentation | [Enter] |
| Environment | [Enter] |
| Hardware | [Enter] |
| Training Run ID | [Enter] |
| Validation Results | [Enter] |
| Test Results | [Enter] |
| Robustness Results | [Enter] |
| Artifact | [Enter] |
| Checksum | [Enter] |
| Decision | [Enter] |
| Reviewer | [Enter] |

## 44. Standard Model Version Record

| Field | Value |
| --- | --- |
| Model ID | [SBAI-MDL-ISL-...] |
| Version | [Major.Minor.Patch] |
| Model Name | [Enter] |
| Status | [Development/Candidate/Validated/Approved/Deployed/Retired] |
| Architecture | [Enter] |
| Dataset Version | [Enter] |
| Feature Version | [Enter] |
| Class Mapping Version | [Enter] |
| Training Experiment | [EXP-ID] |
| Evaluation Report | [EVAL-ID] |
| Accuracy | [Enter] |
| Macro F1 | [Enter] |
| Latency | [Enter] |
| FPS | [Enter] |
| Artifact URI | [Enter] |
| Checksum | [Enter] |
| Approval | [Name/date] |
| Deployment | [DEP-ID] |
| Rollback Version | [Enter] |

## 45. Traceability

| Versioning/Experiment Element | Related Document |
| --- | --- |
| Dataset lineage | 04 Dataset Specification |
| Model architecture | 05 AI Model Specification |
| Training configuration | 23 Model Training Specification |
| Feature lineage | 06 Preprocessing & Feature Engineering |
| Model/API compatibility | 07 API Contract |
| Model metadata storage | 08 Database Schema |
| Technology/runtime | 10 Technology Stack |
| Evaluation evidence | 11 Testing & Evaluation |
| Deployment tracking | 12 Deployment |
| Security/privacy | 13 Security, Privacy & Ethics |
| AI-assisted experiment workflow | 14 Vibe Coding Master Specification |
| Development milestones | 15 Development Roadmap |
| Requirement traceability | 20 Requirements Traceability Matrix |
| Data movement | 21 Data Flow Document |
| Component boundaries | 22 Component & Module Design |

## 46. Editable Project Parameters

| Field | Value |
| --- | --- |
| Model ID Prefix | [SBAI-MDL-ISL] |
| Experiment ID Prefix | [EXP] |
| Training Run Prefix | [RUN] |
| Evaluation Prefix | [EVAL] |
| Deployment Prefix | [DEP] |
| Versioning Scheme | [Semantic Versioning] |
| Artifact Checksum | [SHA-256 / Other] |
| Primary Metric | [Macro F1 / Accuracy / Other] |
| Target Accuracy | [>=90% initial target] |
| Target Macro F1 | [>=0.90 initial target] |
| Latency Target | [<200 ms preferred] |
| Throughput Target | [>=15 FPS] |
| Experiment Tracker | [Enter tool] |
| Model Registry | [Enter tool/location] |
| Artifact Store | [Enter location] |
| Experiment Retention | [Enter policy] |
| Model Retention | [Enter policy] |
| Approval Authority | [Enter role] |
| Rollback Window | [Enter duration] |
| Production Monitoring | [Enter configuration] |

## 47. Assumptions and Constraints

- Model versioning must remain compatible with the model input feature contract.
- Dataset and feature versions are separate from model versions.
- Model performance values are not considered valid until measured and recorded.
- Only approved artifacts may be deployed to production.
- Experiment logs may contain project-sensitive metadata and require controlled access.
- Version changes must be traceable to documented technical changes.
- Final tooling for experiment tracking and registry may be selected later.
## 48. Open Questions

[ ] Which experiment-tracking platform will be adopted?

[ ] Will a dedicated model registry be used or will a controlled repository/object store be sufficient?

[ ] What is the final artifact storage location?

[ ] Who has authority to approve production model versions?

[ ] What retention period will apply to failed experiments?

[ ] Will model cards be mandatory for every production release?

[ ] Will automatic rollback be enabled or remain operator-controlled?

[ ] Which production monitoring signals will trigger model review?

## 49. Acceptance Checklist

☐ Every model has a unique version and immutable artifact.

☐ Every experiment has a unique experiment ID.

☐ Dataset, feature, code, and configuration lineage is captured.

☐ Model status lifecycle is defined.

☐ Registry fields are defined.

☐ Training and evaluation logs are standardized.

☐ Model comparison and selection records are available.

☐ Approval and deployment gates are defined.

☐ Rollback records are supported.

☐ Artifact checksums are recorded.

☐ Security/privacy controls are documented.

☐ Post-deployment monitoring requirements are defined.

☐ Editable experiment/model templates are included.

## 50. Related Documents

| Document | Relationship |
| --- | --- |
| 04 Dataset Specification | Dataset versions and lineage |
| 05 AI Model Specification | Model architecture and outputs |
| 06 Preprocessing & Feature Engineering | Feature version lineage |
| 07 API Contract | Inference/model interface compatibility |
| 08 Database Schema | Model and deployment metadata |
| 10 Technology Stack | Training/runtime technologies |
| 11 Testing & Evaluation | Evaluation evidence |
| 12 Deployment | Deployment and rollback |
| 13 Security, Privacy & Ethics | Data/model governance |
| 14 Vibe Coding Master Specification | AI-assisted development controls |
| 15 Development Roadmap | Model development milestones |
| 20 Requirements Traceability Matrix | Requirement traceability |
| 21 Data Flow Document | Data movement |
| 22 Component & Module Design | Module boundaries |
| Docs/M10_GATE_100REAL.md | 3.0.0 promotion gate record (100-class real; 0.8109/0.8062, n=3326) |
| Docs/M11_GATE_109REAL.md | 4.0.0 promotion gate record (109-class real; 0.8129/0.8079, n=3629; open 0.90 release-gate debt) |
| Docs/M12_WEBCAM_ACCURACY.md | Webcam-replay offline proxy accuracy evidence |
| Docs/M13_ACCURACY_CALIBRATION.md | Canonical accuracy/calibration/policy record (thresholds, ECE/Brier, decision policy, eval artifacts) |
| Docs/eval/*.json, *.txt | Raw evaluation harness artifacts (VAL/TEST finals, TTA gate, webcam-replay, trim gate) |
| 23 Model Training Specification | Training process |

## 51. Version History and Approval

| Version | Date | Author | Change Summary | Status |
| --- | --- | --- | --- | --- |
| 0.1 | [Enter date] | [Enter name] | Initial model versioning and experiment log | Draft |
| 1.0 | [Enter date] | [Enter name] | Baseline approved document | [Draft / Review / Approved] |

| Approval Role | Name | Signature | Date |
| --- | --- | --- | --- |
| Prepared By | [Enter name] | [Signature] | [Date] |
| Reviewed By | [Enter name] | [Signature] | [Date] |
| Approved By | [Enter name] | [Signature] | [Date] |
