<!-- Source: 11_Testing_Evaluation_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# SIGNBRIDGE AI

## 11 — TESTING & EVALUATION

Indian Sign Language Recognition System

| Field | Value |
| --- | --- |
| Document ID | SB-11-TE |
| Version | 1.0 |
| Status | Draft / Review |
| Project | SignBridge AI |
| Document Type | Testing & Evaluation Specification |
| Prepared By | [Enter name / team] |
| Reviewed By | [Enter reviewer] |
| Approved By | [Enter approver] |
| Date | [Enter date] |

Purpose: Define the verification, validation, model evaluation, performance, security, usability, and acceptance approach for SignBridge AI. All numeric values marked as targets are proposed engineering targets and must be confirmed during project execution.

## 1. Document Purpose

This document defines how SignBridge AI will be tested from raw input and landmark processing through AI inference, API services, user interface behavior, and end-to-end recognition. It provides repeatable procedures for demonstrating correctness, robustness, performance, and readiness for deployment.

## 2. Testing Objectives

- Verify that each software component performs according to its specification.
- Validate that the complete pipeline correctly converts camera input into ISL predictions.
- Measure model quality using accuracy, precision, recall, F1-score, macro F1, and confusion matrix analysis.
- Evaluate real-time performance including inference latency, FPS, CPU/GPU usage, and memory.
- Assess robustness under practical changes in lighting, background, signer position, speed, and partial occlusion.
- Verify API, database, UI/UX, security, privacy, and accessibility requirements.
- Provide evidence for release approval and identify defects or model limitations before deployment.
## 3. Scope

| In Scope | Out of Scope / Future |
| --- | --- |
| Camera capture and permissions | Full sign-language translation of unrestricted continuous conversations |
| Hand/pose landmark extraction | Automatic generation of a complete linguistic grammar model |
| Preprocessing and feature engineering | Clinical or certified accessibility claims |
| Static and dynamic ISL recognition | Hardware-specific optimization not selected for deployment |
| AI inference and confidence handling | Unvalidated sign classes outside the approved dataset |
| REST/WebSocket APIs | Third-party services not included in the release |
| Web/application UI | Production-scale global infrastructure beyond agreed deployment scope |
| Database, logging, feedback | Features explicitly marked future in the PRD/SRS |

## 4. Test Strategy

- Testing follows a layered approach: unit → component → integration → system → acceptance.
- AI evaluation is performed on held-out data and signer-independent test data where available.
- Automated tests are preferred for repeatable software behavior; manual tests are retained for camera, usability, and visual interaction scenarios.
- Every release candidate must pass critical functional tests before model-performance and acceptance testing.
- Regression tests are repeated whenever model, preprocessing, API, database, or UI behavior changes.
## 5. Testing Levels

| Level | Purpose | Typical Tools / Evidence |
| --- | --- | --- |
| Unit | Validate individual functions, classes, transformations, and utilities. | Pytest, assertions, coverage report |
| Component | Validate preprocessing, landmark extraction, inference, API modules, UI components. | Pytest, mocked inputs, frontend tests |
| Integration | Verify communication between CV, model, API, database, and UI. | API tests, integration fixtures, WebSocket tests |
| System | Validate the complete user-to-prediction workflow. | End-to-end tests, browser automation |
| Acceptance | Confirm business/project requirements and release criteria. | Acceptance checklist, stakeholder sign-off |

## 6. Functional Testing

- Verify application startup, navigation, camera permission handling, and recognition session creation.
- Verify valid signs produce an appropriate class prediction when the signer is visible and tracking is successful.
- Verify uncertain predictions are handled using the configured confidence threshold.
- Verify no-sign and tracking-lost states do not incorrectly produce a confident sign.
- Verify recognition history, feedback, settings, and supported-sign pages where implemented.
- Verify text-to-speech output when the optional audio feature is enabled.
## 7. Test Environment

| Area | Configuration |
| --- | --- |
| Client OS | [Windows / Linux / macOS / Android / iOS — confirm] |
| Browser | [Chrome / Edge / Firefox / Safari — confirm supported versions] |
| Camera | [Webcam / mobile camera; resolution and FPS to be confirmed] |
| Backend | Python + FastAPI + Uvicorn |
| AI/CV | MediaPipe + OpenCV + NumPy + selected ML framework |
| Database | PostgreSQL or MySQL as approved |
| Network | [Local / LAN / Cloud; latency target to be confirmed] |
| Hardware | [CPU / RAM / GPU / mobile device details] |
| Test Dataset | [Dataset version and test-set identifier] |

## 8. Unit Testing

- Test coordinate normalization, scaling, feature calculation, sequence padding/truncation, and tensor construction.
- Test confidence threshold logic and temporal smoothing functions.
- Test input validation, schema validation, error handling, and response formatting.
- Test database CRUD operations and constraints.
- Test UI state transitions and reusable components where automated frontend tests are available.
Target: ≥80% automated code coverage for core backend/preprocessing logic; final threshold: [Confirm].

## 9. Preprocessing & Feature Engineering Tests

| Test Area | Expected Result |
| --- | --- |
| Frame extraction | Frames are decoded in correct order without unexpected duplication or corruption. |
| Resize/color conversion | Input is converted to the configured dimensions and color representation. |
| Landmark extraction | Valid landmarks are produced when a supported hand/sign is visible. |
| Missing landmarks | Missing or low-confidence landmarks are handled without pipeline failure. |
| Normalization | Translation/scale normalization reduces signer-position and size variation. |
| Temporal features | Velocity/acceleration features preserve expected sequence length and dimensions. |
| Sequence construction | Model receives the configured tensor shape. |
| Augmentation | Augmentations remain within realistic ISL movement constraints. |
| Feature leakage | No information from validation/test data is used to fit training transforms. |

## 10. Computer Vision / Camera Tests

- Verify camera permission denial, acceptance, revocation, and re-entry behavior.
- Test hand detection with one hand, two hands, different hand positions, and supported distances.
- Test tracking stability during normal movement and temporary hand disappearance.
- Test different camera resolutions and frame rates within the supported configuration.
- Record failure cases caused by blur, extreme lighting, cluttered backgrounds, or severe occlusion.
## 11. AI Model Evaluation

The recognition model must be evaluated on a frozen, held-out test set that is not used for training or hyperparameter selection. Whenever possible, the test split must contain signers not present in training data to measure generalization to unseen users.

| Metric | Definition / Purpose | Target / Acceptance |
| --- | --- | --- |
| Accuracy | Correct predictions divided by total predictions. | ≥90% target; [Confirm final] |
| Precision | Correct positive predictions relative to all positive predictions. | ≥0.90 target per agreed evaluation |
| Recall | Correct positive predictions relative to all actual positives. | ≥0.90 target per agreed evaluation |
| F1-score | Harmonic mean of precision and recall. | ≥0.90 target |
| Macro F1 | Average F1 across classes, treating classes equally. | ≥0.90 target |
| Confusion Matrix | Identifies class-level confusions and weak classes. | No critical class failure |
| Inference Latency | Time from ready model input to prediction result. | <200 ms preferred target |
| Real-time FPS | Processed frames per second during recognition. | ≥15 FPS target; [Confirm] |
| Model Size | Serialized model footprint. | [Confirm deployment limit] |

## 12. Dataset Evaluation Protocol

- Maintain separate training, validation, and test partitions.
- Suggested baseline split: 70% training, 15% validation, 15% testing; revise if the final dataset protocol specifies otherwise.
- Avoid signer leakage: samples from the same signer should not be distributed across train and test when measuring signer-independent generalization.
- Report class distribution and identify under-represented classes.
- Document the exact dataset version, class list, number of signers, and number of sequences used for every reported result.
## 13. Robustness Testing

| Condition | Test Method | Expected Observation |
| --- | --- | --- |
| Lighting | Test normal, low, bright, and uneven lighting. | Recognition remains usable within defined operating limits. |
| Background | Use plain and moderately cluttered backgrounds. | Limited performance degradation. |
| Distance | Move signer closer/farther within supported range. | Tracking remains stable within configured range. |
| Movement Speed | Perform signs slowly, normally, and quickly. | Model handles supported speed variation. |
| Hand Position | Vary horizontal/vertical placement. | Normalization reduces position sensitivity. |
| Occlusion | Introduce realistic partial occlusion. | System reports uncertainty/tracking loss rather than false confidence. |
| Camera Motion | Introduce small camera movement. | Pipeline remains stable or clearly reports tracking loss. |
| Multiple People | Place non-target persons in view. | System follows the supported target-selection behavior. |

## 14. Negative & Boundary Testing

- No person or no visible hand.
- Unsupported sign or class.
- Very short or incomplete sequence.
- Excessively long input sequence.
- Corrupted image/video input.
- Invalid API payload or missing required field.
- Unsupported media type or oversized upload.
- Expired/invalid session identifier.
- Database unavailable or model service unavailable.
- Confidence exactly at, below, and above the configured threshold.
## 15. API Testing

| Endpoint / Area | Validation |
| --- | --- |
| GET /health | Service availability and health response. |
| GET /api/v1/model | Model version and deployment metadata. |
| POST /api/v1/predict | Valid and invalid prediction payloads. |
| POST /api/v1/predict/sequence | Sequence shape, length, and feature validation. |
| POST /api/v1/predict/image | Image type, size, decode, and prediction handling. |
| POST /api/v1/predict/video | Video format, duration/size limits, and processing response. |
| POST /api/v1/session | Session creation and identifier validation. |
| DELETE /api/v1/session/{id} | Authorized session deletion. |
| GET /api/v1/classes | Class list and metadata consistency. |
| WebSocket /api/v1/stream | Connection, message format, prediction stream, disconnect/reconnect. |

## 16. API Contract Validation

- Validate request and response schemas against the approved API contract.
- Verify HTTP status codes for success, client errors, authorization errors, rate limits, and server errors.
- Verify error responses do not expose stack traces, secrets, tokens, or unnecessary internal details.
- Verify API versioning and backward compatibility requirements.
- Verify rate limits and request-size limits where configured.
## 17. UI/UX Testing

- Verify camera permission and recognition states are understandable and actionable.
- Verify prediction result, confidence/uncertainty messaging, and status indicators are readable.
- Verify controls work using mouse, keyboard, and supported touch interactions.
- Verify responsive layouts across supported screen sizes.
- Verify history and settings behavior where implemented.
- Verify text-to-speech controls and feedback behavior where enabled.
- Verify error, empty, loading, tracking-lost, and no-sign states.
## 18. Accessibility Testing

- Use sufficient visual contrast for text and interactive controls.
- Provide clear labels and focus states for interactive elements.
- Support keyboard navigation where applicable.
- Do not rely only on color to communicate recognition status.
- Ensure status messages are understandable without requiring precise visual inspection.
- Validate accessibility against the project’s selected standard, e.g., WCAG 2.1 AA, where applicable.
## 19. Performance Testing

| Measure | Target | Actual Result |
| --- | --- | --- |
| Prediction latency | <200 ms preferred | [Enter result] |
| Recognition throughput | ≥15 FPS target | [Enter result] |
| API response time | [Confirm by endpoint] | [Enter result] |
| Memory usage | [Confirm device limit] | [Enter result] |
| CPU/GPU utilization | [Confirm operating range] | [Enter result] |
| Concurrent users | [Confirm expected load] | [Enter result] |
| Startup time | [Confirm target] | [Enter result] |

## 20. Load & Stress Testing

- Measure system behavior at expected concurrent request levels.
- Gradually increase load until latency, error rate, or resource usage exceeds the approved threshold.
- Verify recovery after temporary overload or service restart.
- Test repeated WebSocket connections and disconnect/reconnect cycles.
- Verify database connection pooling and API rate limiting under load.
- Document the maximum tested load and the observed bottleneck.
## 21. Security Testing

- Validate authentication and authorization for protected endpoints where implemented.
- Test malformed payloads, oversized inputs, injection attempts, and unauthorized resource access.
- Verify HTTPS/WSS in deployment environments requiring encrypted transport.
- Verify secrets and credentials are stored outside source code.
- Verify logs do not contain unnecessary personal or sensitive data.
- Test session isolation and access-control boundaries.
- Verify uploaded media is validated and handled according to the retention policy.
## 22. Privacy Testing

- Verify camera access occurs only after required user permission.
- Verify raw camera/video data is not persisted unless explicitly required and disclosed.
- Verify dataset and feedback records follow the project’s approved privacy policy.
- Verify deletion/retention behavior for sessions and user-generated data.
- Document what information is stored, why it is stored, and the retention period.
## 23. Database Testing

- Validate primary keys, foreign keys, uniqueness, required fields, and allowed values.
- Verify session, prediction, model version, feedback, and audit records are created correctly.
- Verify indexes support expected query patterns.
- Test transaction rollback and recovery from failed writes.
- Verify backup and restore procedures on the approved environment.
## 24. Regression Testing

A regression suite must be maintained for all previously discovered defects and all critical user flows. Regression testing is required after model updates, preprocessing changes, API contract changes, database migrations, major UI changes, and dependency upgrades.

- Critical functional test cases must pass before release.
- Previously fixed defects must remain closed.
- Model metrics must not regress beyond the approved tolerance.
- API response schemas must remain compatible unless a versioned change is approved.
## 25. Usability Testing

- Recruit representative users/signers where feasible.
- Measure task completion, recognition feedback, error recovery, and perceived ease of use.
- Observe whether users understand camera permission, recognition status, uncertainty, and retry actions.
- Collect structured feedback using a predefined questionnaire or rating scale.
- Document usability findings separately from AI accuracy so the two evaluation dimensions are not conflated.
## 26. Test Case Template

| Field | Description |
| --- | --- |
| Test Case ID | Unique identifier, e.g., TC-API-001 |
| Requirement ID | Related PRD/SRS/API/UI/model requirement |
| Title | Short description of the test |
| Preconditions | Required system/data/environment state |
| Input | Test data, media, API payload, or user action |
| Steps | Ordered execution steps |
| Expected Result | Expected observable behavior |
| Actual Result | Observed behavior |
| Status | Pass / Fail / Blocked / Not Run |
| Severity | Critical / High / Medium / Low |
| Evidence | Screenshot, log, metric, report, or recording reference |
| Tester / Date | Person and execution date |

## 27. Representative Test Cases

| ID | Test | Expected Result | Priority |
| --- | --- | --- | --- |
| TC-FN-001 | Open application | Home/recognition interface loads without blocking error. | High |
| TC-CAM-001 | Grant camera permission | Camera preview becomes available. | Critical |
| TC-CAM-002 | Deny camera permission | Clear permission guidance is displayed. | High |
| TC-PP-001 | Process valid landmarks | Expected feature tensor is produced. | Critical |
| TC-AI-001 | Recognize known sign | Correct class is returned within target conditions. | Critical |
| TC-AI-002 | Low-confidence sign | System displays uncertain state rather than false certainty. | Critical |
| TC-AI-003 | No sign | No-sign status is returned. | High |
| TC-API-001 | Valid prediction request | 200-series response with valid prediction schema. | Critical |
| TC-API-002 | Invalid payload | 4xx response with structured error. | High |
| TC-UI-001 | Recognition result display | Prediction and status are clearly presented. | High |
| TC-SEC-001 | Unauthorized access | Protected resource is rejected. | High |
| TC-DB-001 | Store prediction | Valid prediction is persisted with required relationships. | Medium |
| TC-PERF-001 | Measure inference latency | Latency meets approved target. | High |
| TC-REG-001 | Run critical regression suite | All critical tests pass. | Critical |

## 28. Defect Classification

| Severity | Meaning | Example |
| --- | --- | --- |
| Critical | Blocks core recognition, causes data/security loss, or prevents release. | Application cannot perform prediction at all. |
| High | Major feature failure with significant user or model impact. | Valid signs consistently fail for a supported class. |
| Medium | Functional issue with workaround or limited scope. | History display fails for some records. |
| Low | Minor issue with limited functional impact. | Non-critical alignment or wording issue. |

## 29. Model Acceptance Criteria

- Final model is trained only on the approved dataset version and documented preprocessing pipeline.
- No critical data leakage is identified between training and evaluation partitions.
- Accuracy and macro F1 meet or exceed the approved project thresholds.
- Per-class performance is reviewed; severe confusion between critical classes is investigated.
- Signer-independent performance is reported when signer-separated data is available.
- Inference latency and memory fit the target deployment environment.
- Model version, training configuration, dataset version, and evaluation results are archived.
## 30. System Acceptance Criteria

- Critical functional tests pass.
- Critical and high-severity unresolved defects are zero unless formally accepted.
- API contract tests pass.
- Core UI recognition flow passes on supported browsers/devices.
- Privacy and security requirements are satisfied for the intended deployment.
- Performance meets approved thresholds or deviations are documented and accepted.
- Model evaluation report is complete and reproducible.
- Stakeholder approval is recorded.
## 31. Evaluation Report Structure

1. Evaluation objective and release/model version.
1. Dataset version, class count, sample count, signer count, and split methodology.
1. Experimental environment and hardware/software versions.
1. Preprocessing and model configuration.
1. Overall accuracy, precision, recall, F1, and macro F1.
1. Confusion matrix and class-wise analysis.
1. Signer-independent results, if available.
1. Robustness results.
1. Latency, FPS, memory, and resource utilization.
1. Known limitations, failed tests, defects, and corrective actions.
1. Final acceptance status and approval.
## 32. Test Evidence & Traceability

- Each test case should map to one or more requirements from the PRD/SRS or supporting specifications.
- Store test reports, screenshots, logs, model evaluation files, confusion matrices, and performance measurements with the relevant release.
- Use stable identifiers for requirements, test cases, model versions, dataset versions, and builds.
- Maintain a traceability matrix to demonstrate that critical requirements have corresponding tests.
## 33. Recommended Test Automation

- Backend/unit/integration tests: Pytest.
- API validation: Pytest + HTTP client or equivalent API test framework.
- Frontend tests: Jest/React Testing Library or the selected project framework.
- End-to-end browser testing: Playwright or equivalent.
- Model evaluation: Python scripts/notebooks with versioned configuration.
- Performance/load testing: Locust, k6, or an approved equivalent.
- CI pipeline: run unit, API, and critical regression tests on every merge; run heavier model/performance suites on release candidates.
## 34. Continuous Integration / Release Gate

| Gate | Required Evidence | Release Rule |
| --- | --- | --- |
| Build | Successful application/backend build | Pass |
| Unit Tests | Automated test report | No critical failures |
| Integration/API | API and service test report | No critical failures |
| UI/E2E | Critical workflow report | Pass |
| AI Evaluation | Metrics + confusion matrix | Approved thresholds met |
| Performance | Latency/FPS/resource report | Approved thresholds met |
| Security | Security test findings | No unresolved critical findings |
| Acceptance | Signed acceptance checklist | Approved |

## 35. Editable Project Parameters

| Parameter | Current Value | Final Value |
| --- | --- | --- |
| Target accuracy | ≥90% | [Confirm] |
| Target macro F1 | ≥0.90 | [Confirm] |
| Preferred inference latency | <200 ms | [Confirm] |
| Target real-time FPS | ≥15 FPS | [Confirm] |
| Train/validation/test split | 70/15/15 suggested | [Confirm] |
| Minimum automated code coverage | ≥80% for core logic | [Confirm] |
| Supported browsers/devices | [Define] | [Confirm] |
| Maximum API payload size | [Define] | [Confirm] |
| Concurrent user target | [Define] | [Confirm] |
| Data retention period | [Define] | [Confirm] |
| Release defect threshold | No unresolved Critical; High by approval | [Confirm] |

## 36. Dependencies

- 01_Project_PRD — product goals, scope, features, and success criteria.
- 02_SRS — functional and non-functional requirements.
- 03_System_Architecture — component and data-flow behavior.
- 04_Dataset_Specification — dataset composition and evaluation splits.
- 05_AI_Model_Specification — model inputs, architecture, training, and metrics.
- 06_Preprocessing_Feature_Engineering — preprocessing and feature definitions.
- 07_API_Contract — endpoint, schema, and error behavior.
- 08_Database_Schema — persistence and data integrity requirements.
- 09_UI_UX_Specification — interface and accessibility expectations.
- 10_Technology_Stack — implementation environment and testing tools.
## 37. Risks & Mitigation

| Risk | Potential Impact | Mitigation |
| --- | --- | --- |
| Dataset leakage | Inflated evaluation results | Signer-independent split and dataset audit. |
| Class imbalance | Weak minority-class recognition | Balanced collection, class metrics, targeted augmentation. |
| Overfitting | Poor unseen-signer performance | Regularization, validation, augmentation, early stopping. |
| Camera variability | Tracking/prediction degradation | Robustness tests across supported devices and conditions. |
| Latency growth | Poor real-time UX | Profiling, model optimization, efficient preprocessing. |
| Dependency changes | Unexpected regressions | Version pinning and regression testing. |
| Privacy failure | Unintended data exposure | Minimize storage, access control, secure logs, retention rules. |

## 38. Final Evaluation Checklist

- ☐ Requirements traced to test cases.
- ☐ Test environment documented.
- ☐ Unit and integration tests completed.
- ☐ Critical functional tests passed.
- ☐ AI evaluation completed on frozen test data.
- ☐ Signer-independent evaluation completed where applicable.
- ☐ Confusion matrix and class-wise results reviewed.
- ☐ Robustness tests completed.
- ☐ Performance/load tests completed.
- ☐ Security and privacy checks completed.
- ☐ Accessibility/usability checks completed.
- ☐ Regression suite passed.
- ☐ Defects reviewed and dispositioned.
- ☐ Model and dataset versions archived.
- ☐ Acceptance approval recorded.
## 39. Version History

| Version | Date | Author | Change Description | Status |
| --- | --- | --- | --- | --- |
| 1.0 | [Enter date] | [Enter name] | Initial Testing & Evaluation specification. | Draft |
| 1.1 | [Enter date] | [Enter name] | [Enter changes] | [Review/Approved] |
| 2.0 | [Enter date] | [Enter name] | [Major revision if required] | [Review/Approved] |

## 40. Approval

| Role | Name | Signature | Date |
| --- | --- | --- | --- |
| Project Lead | [Enter] | [Signature] | [Date] |
| AI/ML Lead | [Enter] | [Signature] | [Date] |
| Software Lead | [Enter] | [Signature] | [Date] |
| QA/Test Lead | [Enter] | [Signature] | [Date] |
| Project Reviewer | [Enter] | [Signature] | [Date] |

> Document control note: Values shown as targets or placeholders must be finalized against the approved project requirements and actual experimental results before release.
