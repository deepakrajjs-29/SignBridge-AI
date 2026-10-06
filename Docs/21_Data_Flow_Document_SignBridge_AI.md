<!-- Source: 21_Data_Flow_Document_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# SIGNBRIDGE AI

## DATA FLOW DOCUMENT

*Camera-Based Indian Sign Language Recognition System*

| Field | Value |
| --- | --- |
| Document ID | SBAI-DFD-001 |
| Document Number | 21_Data_Flow_Document |
| Version | 1.0 |
| Status | [Draft / Review / Approved] |
| Prepared By | [Enter name] |
| Reviewed By | [Enter name] |
| Approved By | [Enter name] |
| Date | [Enter date] |

*Editable project documentation • SignBridge AI*

## Table of Contents

1. Document Purpose

2. Scope

3. Data Flow Objectives

4. System Context

5. Data Flow Modeling Conventions

6. Level 0 Context Data Flow

7. Level 1 System Data Flow

8. Level 2 Recognition Data Flow

9. Level 2 Dataset and Training Data Flow

10. Level 2 Feedback and History Data Flow

11. Data Sources

12. Data Destinations

13. Data Stores

14. External Entities

15. Data Flow Inventory

16. Process Inventory

17. Data Store Inventory

18. Data Structure Definitions

19. Camera Input Flow

20. Landmark Extraction Flow

21. Preprocessing and Feature Engineering Flow

22. AI Inference Flow

23. Prediction and Confidence Flow

24. API Request/Response Flow

25. WebSocket Real-Time Flow

26. Database Flow

27. Model Management Flow

28. Dataset Collection and Training Flow

29. Feedback Flow

30. History Flow

31. Error and Recovery Data Flow

32. Security and Privacy Data Flow

33. Data Validation Rules

34. Data Retention and Deletion Flow

35. Data Quality Controls

36. Performance and Throughput

37. Failure Scenarios

38. Data Flow Traceability

39. DFD-to-Architecture Mapping

40. DFD-to-API Mapping

41. DFD-to-Database Mapping

42. DFD-to-UI Mapping

43. DFD-to-AI Mapping

44. Testing and Verification

45. Editable Project Parameters

46. Assumptions and Constraints

47. Open Questions

48. Acceptance Checklist

49. Related Documents

50. Version History and Approval

## 1. Document Purpose

This Data Flow Document (DFD) defines how data moves through SignBridge AI from camera capture and user interaction through computer-vision processing, feature engineering, AI inference, API services, database persistence, feedback, and user-facing results. It provides a common data-flow reference for development, testing, security, and project review.

## 2. Scope

- Camera-based real-time Indian Sign Language recognition.
- Frame acquisition, hand/landmark extraction, preprocessing, temporal sequence construction, and AI inference.
- Sign-to-text result delivery through the application and backend API.
- Optional persistence of sessions, predictions, feedback, and model metadata.
- Dataset collection, annotation, training, validation, and model deployment flows.
- Error, privacy, security, retention, and recovery data flows.
## 3. Data Flow Objectives

- Make every important input, transformation, storage operation, and output explicit.
- Separate transient real-time recognition data from persistent application data.
- Support traceability between DFD processes and the PRD, SRS, API, database, AI, and UI specifications.
- Identify privacy-sensitive flows and minimize unnecessary persistence.
- Provide a basis for test-case design and system integration.
## 4. System Context

At the highest level, SignBridge AI receives visual input from a camera, extracts hand/body landmarks, transforms them into model-ready temporal features, performs sign classification, and returns a recognition result to the user interface. Backend services provide model metadata, session management, persistence, feedback, and optional real-time streaming support.

| External Entity | Input to SignBridge AI | Output from SignBridge AI |
| --- | --- | --- |
| End User / Signer | Camera interaction, recognition controls, feedback | Recognized sign, text, confidence, status, messages |
| Camera Device | Frames/video stream | Camera status/errors |
| Browser / Client | API/WebSocket requests | JSON responses/stream events |
| Administrator / Operator | Model/configuration actions | Status, model metadata, deployment result |
| Training Pipeline | Dataset, labels, training configuration | Trained model artifacts/metrics |
| Optional TTS Service | Recognized text | Speech playback/status |

## 5. Data Flow Modeling Conventions

| Notation | Meaning | SignBridge AI Example |
| --- | --- | --- |
| External Entity | Actor or system outside the process boundary | Camera, End User, Browser |
| Process | Transforms or acts on data | P1 Landmark Extraction |
| Data Flow | Movement of data between entities/processes/stores | Frame Stream |
| Data Store | Persistent or controlled storage | D1 Model Registry |
| Transient Data | Short-lived in-memory data | Current Frame, Landmark Sequence |
| Persistent Data | Data retained beyond a request/session | Prediction Record |

DFD identifiers use E for external entities, P for processes, D for data stores, and F for named data flows.

## 6. Level 0 Context Data Flow

The Level 0 context view treats SignBridge AI as one logical process. The main external flows are camera frames into the system, user/API commands into the system, and recognition results/status back to the client.

| Flow ID | Source | Destination | Data | Direction |
| --- | --- | --- | --- | --- |
| F-001 | Camera Device | SignBridge AI | Video frames / frame metadata | Inbound |
| F-002 | End User | SignBridge AI | Start/stop/settings/feedback actions | Inbound |
| F-003 | Browser / Client | SignBridge AI | API/WebSocket requests | Inbound |
| F-004 | SignBridge AI | Browser / Client | Recognition result/status | Outbound |
| F-005 | SignBridge AI | End User | Text/status/optional speech | Outbound |
| F-006 | Training Pipeline | SignBridge AI | Model artifact/metadata | Inbound |
| F-007 | SignBridge AI | Administrator | Model/system status | Outbound |

## 7. Level 1 System Data Flow

The main runtime pipeline is divided into capture, vision processing, feature processing, inference, result handling, API/session management, persistence, and presentation.

| Process | Process Name | Primary Input | Primary Output |
| --- | --- | --- | --- |
| P1 | Capture & Session Initialization | Camera/client request | Active session + frames |
| P2 | Frame Quality & Hand Tracking | Frames | Validated landmarks |
| P3 | Preprocessing & Feature Engineering | Landmarks | Feature sequence |
| P4 | AI Inference | Feature sequence + model | Class probabilities |
| P5 | Prediction Post-processing | Probabilities | Label + confidence + state |
| P6 | API / Stream Service | Result/session data | REST/WS response |
| P7 | Persistence & History | Session/prediction/feedback | Database records |
| P8 | UI Presentation | API/stream result | User-visible result |

## 8. Level 2 Recognition Data Flow

1. Camera produces a frame or short video segment.
1. Capture process timestamps the frame and associates it with the active session.
1. Frame-quality logic checks availability, resolution, blur/visibility, and tracking readiness.
1. MediaPipe-based landmark extraction detects one or both hands as configured.
1. Landmarks are validated and normalized.
1. Spatial and temporal features are generated.
1. Frames are accumulated into a fixed or controlled-length sequence.
1. The model receives the feature tensor and produces class probabilities.
1. Post-processing applies confidence thresholds and temporal smoothing.
1. The system emits a recognized, uncertain, no-sign, tracking-lost, processing, or error state.
1. The result is returned to the UI through REST or WebSocket mechanisms.
1. Persistent records are written only when configured by the applicable privacy and storage policy.

| Flow | From | To | Data |
| --- | --- | --- | --- |
| F-101 | Camera | P1 | Frame |
| F-102 | P1 | P2 | Timestamped frame |
| F-103 | P2 | P3 | Validated landmarks |
| F-104 | P3 | P4 | Feature sequence/tensor |
| F-105 | P4 | P5 | Class probabilities |
| F-106 | P5 | P6 | Prediction result |
| F-107 | P6 | P8 | UI result/event |
| F-108 | P6 | D2 | Optional session/prediction record |

## 9. Level 2 Dataset and Training Data Flow

| Stage | Input | Transformation | Output |
| --- | --- | --- | --- |
| Collection | Raw sign videos/frames | Capture and signer metadata | Raw dataset |
| Quality Review | Raw dataset | Remove corrupt/invalid samples | Quality-approved dataset |
| Annotation | Approved samples | Assign sign class/metadata | Labeled dataset |
| Preprocessing | Labeled samples | Landmarks/features/sequences | Model-ready dataset |
| Split | Model-ready dataset | Signer-aware train/validation/test split | Dataset partitions |
| Training | Training partition | Model optimization | Candidate model |
| Validation | Validation partition | Hyperparameter/threshold selection | Validated model |
| Evaluation | Test partition | Independent metrics | Evaluation report |
| Registry | Approved model | Version and metadata registration | Deployable model artifact |

## 10. Level 2 Feedback and History Data Flow

- User submits optional feedback against a prediction or session.
- Feedback is validated and linked to the relevant prediction/session identifier.
- Feedback is persisted only according to the approved privacy and retention policy.
- History requests query authorized session/prediction records.
- UI displays historical recognition information without exposing restricted internal metadata.
- Aggregated feedback may be used for controlled model improvement after review and consent requirements are satisfied.
## 11. Data Sources

| Source | Data Type | Volatility | Sensitivity | Default Persistence |
| --- | --- | --- | --- | --- |
| Camera | Frames/video | Very high | Potentially sensitive | No |
| MediaPipe | Landmarks/tracking state | Very high | Potentially sensitive | No |
| Dataset | Labeled sign samples | Low | Controlled | Yes |
| Model | Weights/configuration | Low | Controlled | Yes |
| Client | Commands/preferences | Medium | User-related | As required |
| Feedback | Rating/comment/correction | Low | User-related | Optional |
| System | Logs/metrics | High | Operational | Controlled |

## 12. Data Destinations

- Recognition UI: current label, confidence, status, and optional speech output.
- Session database: session metadata when persistence is enabled.
- Prediction database: structured recognition results when persistence is enabled.
- Feedback database: user corrections/feedback when enabled.
- Model registry: model artifact metadata and deployment state.
- Operational logs/monitoring: technical events subject to privacy controls.
## 13. Data Stores

| ID | Data Store | Purpose | Key Data | Retention |
| --- | --- | --- | --- | --- |
| D1 | Dataset Storage | Training/evaluation data | Samples, labels, signer metadata | [Enter policy] |
| D2 | Application Database | Runtime persistence | Users, sessions, predictions, feedback | [Enter policy] |
| D3 | Model Registry | Model lifecycle | Version, checksum, metrics, artifact location | Version lifecycle |
| D4 | Configuration Store | Runtime configuration | Thresholds, feature/model settings | Versioned |
| D5 | Logs/Monitoring | Operations | Errors, latency, health metrics | [Enter policy] |
| D6 | Backup Storage | Recovery | Approved backups | [Enter policy] |

## 14. External Entities

| ID | Entity | Role in Data Flow |
| --- | --- | --- |
| E1 | End User / Signer | Provides signs and interacts with recognition controls |
| E2 | Camera Device | Provides visual input |
| E3 | Browser / Frontend | Sends commands and receives results |
| E4 | Administrator / Operator | Manages system/model operations |
| E5 | Training Pipeline | Produces evaluated model artifacts |
| E6 | Optional TTS Service | Converts recognized text to speech |

## 15. Data Flow Inventory

| ID | Flow | Source | Destination | Primary Process/Store |
| --- | --- | --- | --- | --- |
| F-001 | Video Frame | Camera | Capture | P1 |
| F-002 | Session Command | Client | Session Manager | P1 |
| F-003 | Timestamped Frame | P1 | Vision Processor | P2 |
| F-004 | Validated Landmarks | P2 | Feature Engine | P3 |
| F-005 | Feature Tensor | P3 | Model | P4 |
| F-006 | Class Probabilities | P4 | Post Processor | P5 |
| F-007 | Prediction Result | P5 | API/Stream | P6 |
| F-008 | UI Result | P6 | Frontend | P8 |
| F-009 | Session Record | P6 | Database | D2 |
| F-010 | Prediction Record | P6 | Database | D2 |
| F-011 | Feedback Record | Frontend | Feedback Service | P7 |
| F-012 | Model Metadata | D3 | P4/P6 | P4/P6 |
| F-013 | Training Data | D1 | Training Pipeline | Training |
| F-014 | Model Artifact | Training Pipeline | D3 | D3 |

## 16. Process Inventory

| ID | Process | Description |
| --- | --- | --- |
| P1 | Capture & Session Initialization | Creates session context and receives frames |
| P2 | Frame Quality & Landmark Tracking | Extracts and validates landmarks |
| P3 | Preprocessing & Feature Engineering | Normalizes and constructs temporal features |
| P4 | AI Inference | Runs the selected model |
| P5 | Prediction Post-processing | Applies smoothing, thresholds, and state logic |
| P6 | API / Real-Time Stream Service | Delivers results and manages runtime API flows |
| P7 | Persistence / Feedback Service | Writes and retrieves authorized persistent data |
| P8 | UI Presentation | Renders status, result, confidence, and controls |
| P9 | Training & Evaluation Pipeline | Builds, evaluates, and registers models |

## 17. Data Store Inventory

| Store | Owner/Component | Access Pattern | Protection |
| --- | --- | --- | --- |
| D1 | Dataset Pipeline | Read/write during controlled dataset operations | Access control + backup |
| D2 | Backend/Database | Transactional reads/writes | Authentication + authorization + encryption |
| D3 | Model Registry | Versioned reads/writes | Integrity checks + restricted write access |
| D4 | Configuration | Controlled read/write | Environment separation |
| D5 | Monitoring | Append/read | Restricted operational access |
| D6 | Backup | Recovery operations | Restricted access + encryption |

## 18. Data Structure Definitions

| Data Object | Core Fields | Notes |
| --- | --- | --- |
| Frame | frame_id, timestamp, image dimensions, session_id | Transient by default |
| Landmark Set | hand_id, landmark_id, x, y, z, visibility | Normalized before model input |
| Feature Sequence | sequence_id, frame_count, feature_vector[] | Model input structure |
| Prediction | prediction_id, session_id, label, confidence, status, timestamp, model_version | Persistence configurable |
| Session | session_id, start_time, end_time, client metadata, status | Avoid unnecessary device/user identifiers |
| Feedback | feedback_id, prediction_id, type, correction, comment, timestamp | Optional |
| Model Metadata | model_version, checksum, classes, metrics, deployment_state | Controlled lifecycle |

## 19. Camera Input Flow

- Request camera permission only when recognition requires it.
- Acquire frames at the configured target frame rate.
- Attach timestamps and session context.
- Perform basic frame validation before expensive processing.
- Discard unusable frames without persisting them by default.
- Stop capture when the user ends recognition or a critical camera error occurs.
## 20. Landmark Extraction Flow

1. Receive validated frame.
1. Run hand/pose landmark detection according to configured model settings.
1. Determine detected hand count and tracking confidence.
1. Validate landmark completeness and coordinate ranges.
1. Mark tracking-lost when landmarks are unavailable for the configured tolerance.
1. Pass valid landmarks to preprocessing.
## 21. Preprocessing and Feature Engineering Flow

| Step | Input | Operation | Output |
| --- | --- | --- | --- |
| 21.1 | Landmarks | Missing-data validation | Valid landmark set |
| 21.2 | Landmarks | Translation normalization | Centered coordinates |
| 21.3 | Landmarks | Scale normalization | Scale-normalized coordinates |
| 21.4 | Coordinates | Spatial features | Distances/angles/orientation |
| 21.5 | Frame sequence | Temporal differences | Velocity/acceleration/trajectory |
| 21.6 | Feature stream | Sequence management | Fixed-length feature sequence |
| 21.7 | Sequence | Scaling/formatting | Model tensor |

## 22. AI Inference Flow

- Load the approved active model version.
- Receive a model-compatible feature tensor.
- Run inference using the configured runtime.
- Generate class probabilities or logits.
- Select candidate class and confidence.
- Pass output to temporal smoothing and confidence/state logic.
- Record model version with a persisted prediction when persistence is enabled.
## 23. Prediction and Confidence Flow

| Condition | Result State | Typical Output |
| --- | --- | --- |
| Confidence >= threshold and tracking valid | Recognized | Label + confidence |
| Confidence below threshold | Uncertain | Candidate + uncertainty |
| No valid sign detected | No Sign | Status only |
| Landmarks unavailable beyond tolerance | Tracking Lost | Status + recovery prompt |
| Inference in progress | Processing | Processing status |
| Unexpected processing failure | Error | Safe error response |

Thresholds and state-transition tolerances are editable project parameters and must be validated during testing.

## 24. API Request/Response Flow

| Endpoint/Channel | Inbound Data | Processing | Outbound Data |
| --- | --- | --- | --- |
| GET /health | Health request | Service health check | Health status |
| GET /api/v1/model | Model query | Read model registry | Model metadata |
| POST /api/v1/predict | Frame/feature request | Validate → process → infer | Prediction JSON |
| POST /api/v1/predict/sequence | Feature sequence | Validate → infer | Prediction JSON |
| POST /api/v1/session | Session metadata | Create session | Session ID |
| GET /api/v1/classes | Class query | Read class registry | Supported classes |
| WS /api/v1/stream | Frame/events | Continuous recognition | Prediction/status events |

## 25. WebSocket Real-Time Flow

1. Client opens authenticated/authorized WebSocket connection where required.
1. Server creates or associates a recognition session.
1. Client sends frame or feature messages according to the agreed protocol.
1. Server validates message structure and rate.
1. Vision/preprocessing/inference pipeline processes the message.
1. Server emits recognition state/result events.
1. Client updates the UI without waiting for a full page refresh.
1. Connection closure releases transient session resources.
## 26. Database Flow

| Operation | Source | Destination | Stored Data |
| --- | --- | --- | --- |
| Create session | Session service | D2 | Session metadata |
| Write prediction | Prediction service | D2 | Label, confidence, status, model version |
| Read history | UI/API | D2 | Authorized prior records |
| Write feedback | UI/API | D2 | Feedback and correction |
| Read model metadata | API/model service | D3 | Version, metrics, status |
| Write audit event | Security/admin service | D2/D5 | Controlled operational event |

## 27. Model Management Flow

1. Training pipeline creates a candidate model.
1. Evaluation produces independent metrics and artifacts.
1. Model metadata, version, checksum, and class mapping are registered.
1. Approval/deployment gate verifies acceptance criteria.
1. Deployment service activates the selected model version.
1. Runtime loads the active model and records its version in inference context.
1. Rollback restores a previously approved model if required.
## 28. Dataset Collection and Training Data Flow

- Collect samples under documented consent and dataset governance procedures.
- Attach label, signer/session metadata, capture conditions, and dataset version.
- Run quality control and remove unusable or duplicate samples.
- Create signer-aware training/validation/testing partitions.
- Extract landmarks and engineered features.
- Train candidate models and retain reproducible configuration.
- Evaluate on held-out data and register only approved models.
## 29. Feedback Flow

| Input | Validation | Storage | Use |
| --- | --- | --- | --- |
| Correct/incorrect selection | Verify prediction/session reference | D2 if enabled | Quality analysis |
| Correct label | Validate supported class | D2 | Dataset/model improvement review |
| Comment | Length/content validation | D2 if allowed | Usability analysis |
| No feedback | No action | None | No unnecessary storage |

## 30. History Flow

1. User requests history.
1. API authenticates/authorizes the request as applicable.
1. Backend queries only permitted records.
1. Sensitive fields are filtered according to policy.
1. Results are paginated/limited.
1. Frontend renders history without exposing internal identifiers unnecessarily.
## 31. Error and Recovery Data Flow

| Failure | Detected By | Data Flow Action | User/System Result |
| --- | --- | --- | --- |
| Camera unavailable | Client/capture | Stop frame flow | Permission/device guidance |
| Tracking lost | Vision processor | Emit status, discard invalid input | Tracking recovery state |
| Invalid feature tensor | Feature validator | Reject request | Validation error |
| Model unavailable | Inference service | Fail safely | Service/model error |
| API timeout | Client/API | Retry where safe | Transient error state |
| Database unavailable | Persistence layer | Do not block core transient recognition unless required | Persistence warning |
| WebSocket disconnect | Stream service | Release session resources | Reconnect guidance |

## 32. Security and Privacy Data Flow

- Camera frames remain transient by default and are not persisted unless explicitly required and authorized.
- Landmarks are treated as potentially sensitive data and are minimized and protected.
- API requests use HTTPS/WSS in deployed environments.
- Authentication and authorization are applied to protected administrative/persistent operations.
- Secrets are never embedded in frame payloads, logs, client code, or model inputs.
- Logs should contain operational identifiers rather than raw camera frames or unnecessary personal information.
- Data export, deletion, and retention operations follow the approved privacy policy.
## 33. Data Validation Rules

| Data | Validation |
| --- | --- |
| Frame | Supported format, dimensions, timestamp, size/rate limits |
| Landmarks | Expected landmark count, coordinate range, tracking validity |
| Feature Vector | Expected dimension, numeric values, finite values, sequence length |
| Prediction Request | Schema validation, payload size, session authorization |
| Prediction Response | Label from supported classes, confidence in valid range, status enum |
| Session | Valid ID, lifecycle state, timestamps |
| Feedback | Valid type, bounded text, referenced prediction/session |
| Model | Version format, checksum, class mapping, compatibility |

## 34. Data Retention and Deletion Flow

1. Identify whether data is transient or persistent.
1. Apply the configured retention period to each persistent data category.
1. Expire records using controlled scheduled processes where applicable.
1. Delete or anonymize eligible records according to policy.
1. Remove associated indexes/backups according to the approved deletion procedure.
1. Record only the minimum operational audit information needed to demonstrate compliance.
## 35. Data Quality Controls

- Frame-level validation before landmark extraction.
- Landmark completeness and tracking-quality checks.
- Feature dimension and numeric-validity checks.
- Sequence length and temporal consistency checks.
- Dataset label and signer metadata validation.
- Train/validation/test leakage checks.
- Model input/output contract validation.
- Database referential integrity and schema constraints.
- API schema validation and bounded payload checks.
## 36. Performance and Throughput

| Metric | Target / Guideline | Measurement Point |
| --- | --- | --- |
| Recognition latency | Preferred <200 ms where feasible | Frame/sequence to result |
| Real-time processing | Target >=15 FPS | Runtime pipeline |
| API response | Define per endpoint | API gateway/service |
| WebSocket event delay | Low enough for interactive feedback | Client ↔ server |
| Database writes | Asynchronous where safe | Persistence layer |
| Model load time | Define environment-specific target | Deployment/startup |

These are engineering targets, not measured results. Final values must be established through the Testing & Evaluation document.

## 37. Failure Scenarios

| Scenario | Expected Data Behavior | Recovery |
| --- | --- | --- |
| No hand detected | No-sign/tracking state; no invalid tensor | Wait for valid landmarks |
| Partial hand detection | Validate configured tolerance | Continue or tracking-lost |
| Rapid sign movement | Temporal pipeline handles sequence variation | Smoothing/retry |
| Occlusion | Confidence may decrease | Uncertain/tracking state |
| Poor lighting | Frame/landmark quality may fail | User guidance |
| Multiple people | Apply configured single-user policy | Ignore unsupported detections or request single signer |
| Model mismatch | Reject incompatible model input | Load compatible version |
| Storage outage | Keep transient recognition independent where possible | Retry persistence safely |

## 38. Data Flow Traceability

| DFD Element | Related Requirement/Document | Traceability Purpose |
| --- | --- | --- |
| P1 Capture | PRD/SRS/UC-02 | Camera/session behavior |
| P2 Vision | AI Model Spec / Preprocessing Spec | Landmark extraction |
| P3 Features | Preprocessing Spec | Feature generation |
| P4 Inference | AI Model Spec | Model execution |
| P5 Post-processing | SRS / AI Model Spec | Confidence/state behavior |
| P6 API | API Contract | Data transport |
| P7 Persistence | Database Schema | Data storage |
| P8 UI | UI/UX Specification | User presentation |
| P9 Training | Dataset + AI Model Specification | Model lifecycle |

## 39. DFD-to-Architecture Mapping

| DFD Process | Architecture Layer | Typical Component |
| --- | --- | --- |
| P1 | Client/Application | Camera capture + session manager |
| P2 | Computer Vision | OpenCV + MediaPipe |
| P3 | AI preprocessing | Feature engineering pipeline |
| P4 | AI/ML | LSTM/GRU/Temporal Transformer runtime |
| P5 | Application/AI service | Prediction post-processor |
| P6 | Backend | FastAPI + WebSocket |
| P7 | Data | PostgreSQL/MySQL + ORM |
| P8 | Frontend | React/Next.js + TypeScript |
| P9 | MLOps/Training | Training/evaluation scripts + model registry |

## 40. DFD-to-API Mapping

| DFD Flow/Process | API Mapping |
| --- | --- |
| Health/status | GET /health |
| Model metadata | GET /api/v1/model |
| Single prediction | POST /api/v1/predict |
| Sequence prediction | POST /api/v1/predict/sequence |
| Image prediction | POST /api/v1/predict/image |
| Video prediction | POST /api/v1/predict/video |
| Session lifecycle | POST /api/v1/session and DELETE /api/v1/session/{id} |
| Supported classes | GET /api/v1/classes |
| Real-time stream | WS /api/v1/stream |

## 41. DFD-to-Database Mapping

| Data Flow | Database Entity |
| --- | --- |
| User/session context | users / recognition_sessions |
| Prediction result | predictions |
| Model metadata | model_versions / model_deployments |
| User correction | feedback |
| Operational events | api_logs / audit_logs |
| Dataset records | External dataset store; separate from runtime DB unless explicitly designed |

## 42. DFD-to-UI Mapping

| UI Screen/State | Primary Data Flow |
| --- | --- |
| Home | Application initialization/status |
| Camera Permission | Camera permission flow |
| Recognition | Frame → landmarks → features → inference |
| Recognition Result | Prediction → post-processing → UI |
| Uncertain | Confidence/status flow |
| No Sign | Detection/state flow |
| Tracking Lost | Landmark tracking recovery flow |
| History | Database → API → UI |
| Supported Signs | Class registry → API → UI |
| Settings | Configuration/preferences flow |
| Feedback | UI → API → feedback store |

## 43. DFD-to-AI Mapping

| AI Stage | Data In | Data Out |
| --- | --- | --- |
| Landmark Extraction | Frame | Landmark set |
| Normalization | Landmark set | Normalized landmarks |
| Spatial Features | Normalized landmarks | Spatial feature vector |
| Temporal Features | Feature sequence | Velocity/acceleration/trajectory |
| Sequence Builder | Feature stream | Model tensor |
| Model Inference | Model tensor + model | Class probabilities |
| Post-processing | Probabilities + state | Prediction state |

## 44. Testing and Verification

- Verify each DFD process independently using unit/component tests.
- Verify end-to-end frame-to-result flow using integration tests.
- Verify API payloads against the API Contract.
- Verify persistence mappings against the Database Schema.
- Verify state transitions for recognized, uncertain, no-sign, tracking-lost, and error conditions.
- Measure latency/FPS and validate against approved targets.
- Test privacy behavior to confirm frames are not persisted by default.
- Use traceability to link DFD elements to test cases and acceptance criteria.

| Verification Area | Evidence |
| --- | --- |
| Camera flow | Camera integration test |
| Landmark flow | Landmark extraction test report |
| Feature flow | Feature shape/value tests |
| AI flow | Model evaluation report |
| API flow | API contract test results |
| Database flow | Schema/integration test results |
| UI flow | End-to-end UI test evidence |
| Privacy flow | Retention/deletion/storage verification |

## 45. Editable Project Parameters

| Field | Value |
| --- | --- |
| Target FPS | [Enter value; initial target >=15 FPS] |
| Sequence Length | [Enter frames; e.g., 30–60] |
| Recognition Confidence Threshold | [Enter value] |
| Tracking-Lost Tolerance | [Enter frames/time] |
| Persistence Enabled | [Yes / No / Configurable] |
| Raw Video Storage | [Disabled by default / Approved exception] |
| Prediction History Retention | [Enter duration] |
| Log Retention | [Enter duration] |
| Active Model Version | [Enter version] |
| API Base URL | [Enter environment-specific URL] |
| WebSocket Enabled | [Yes / No] |
| Database Provider | [PostgreSQL / MySQL / Other] |
| Dataset Version | [Enter version] |
| Environment | [Development / QA / Staging / Production] |

## 46. Assumptions and Constraints

- The primary use case is controlled camera-based ISL recognition rather than universal sign-language translation.
- Only supported and documented sign classes are expected to be recognized.
- Camera quality, lighting, signer distance, occlusion, and background can affect performance.
- Raw video persistence is disabled by default.
- Final model architecture and thresholds may change after experimentation.
- Persistent data schemas must remain aligned with the approved Database Schema.
- API changes require coordinated updates to backend, frontend, tests, and documentation.
## 47. Open Questions

[ ] Which exact ISL vocabulary/classes are included in the first production release?

[ ] Will inference run primarily on the client, server, or a hybrid architecture?

[ ] What exact sequence length and frame sampling strategy will be finalized?

[ ] Which persistent history fields are required for the MVP?

[ ] Will WebSocket streaming be enabled in the first release?

[ ] What are the final retention periods for sessions, predictions, feedback, and logs?

[ ] Which model version will be designated as the initial production baseline?

[ ] What deployment environment and hosting provider will be used?

## 48. Acceptance Checklist

☐ Level 0, Level 1, and Level 2 flows documented.

☐ All major runtime processes have defined inputs and outputs.

☐ All persistent data stores are identified.

☐ Camera-to-result data flow is traceable end to end.

☐ Training/data flow is documented separately from runtime flow.

☐ API and database mappings are included.

☐ Privacy-sensitive flows are identified.

☐ Error and recovery flows are documented.

☐ Performance targets are explicitly marked as targets.

☐ Editable parameters are provided.

☐ DFD is reviewed against PRD, SRS, Architecture, Dataset, AI, API, Database, UI/UX, and Testing documents.

☐ Open questions are resolved before final approval.

## 49. Related Documents

| Document | Relationship |
| --- | --- |
| 01 Project PRD | Product scope, goals, user needs |
| 02 SRS | Functional and non-functional requirements |
| 03 System Architecture | Components and deployment-level architecture |
| 04 Dataset Specification | Dataset structure and governance |
| 05 AI Model Specification | Model inputs, outputs, training, inference |
| 06 Preprocessing & Feature Engineering | Landmark and feature transformation pipeline |
| 07 API Contract | External/backend data interfaces |
| 08 Database Schema | Persistent data structures |
| 09 UI/UX Specification | User-facing data presentation |
| 10 Technology Stack | Implementation technologies |
| 11 Testing & Evaluation | Verification of data flows |
| 12 Deployment | Runtime deployment and infrastructure |
| 13 Security, Privacy & Ethics | Protection and responsible data handling |
| 20 Requirements Traceability Matrix | Cross-document requirement traceability |

## 50. Version History and Approval

| Version | Date | Author | Change Summary | Status |
| --- | --- | --- | --- | --- |
| 0.1 | [Enter date] | [Enter name] | Initial DFD draft | Draft |
| 1.0 | [Enter date] | [Enter name] | Baseline approved DFD | [Draft / Review / Approved] |

| Approval Role | Name | Signature | Date |
| --- | --- | --- | --- |
| Prepared By | [Enter name] | [Signature] | [Date] |
| Reviewed By | [Enter name] | [Signature] | [Date] |
| Approved By | [Enter name] | [Signature] | [Date] |
