<!-- Source: 32_Known_Issues_Limitations_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# SIGNBRIDGE AI

## KNOWN ISSUES & LIMITATIONS

*Known constraints, unresolved issues, operational boundaries, and mitigation guidance*

| Field | Value |
| --- | --- |
| Document ID | SBAI-KIL-001 |
| Document Number | 32 |
| Version | 1.0 |
| Status | Draft / Editable |
| Project | SignBridge AI |
| Prepared By | [Enter Name / Team] |
| Reviewed By | [Enter Reviewer] |
| Approved By | [Enter Approver] |
| Effective Date | [Enter Date] |
| Last Updated | [Enter Date] |

## Table of Contents

1. 1. Purpose
1. 2. Scope
1. 3. Definitions
1. 4. Issue and Limitation Classification
1. 5. Known Issues Register
1. 6. Functional Limitations
1. 7. AI/ML Limitations
1. 8. Dataset Limitations
1. 9. Computer Vision and Tracking Limitations
1. 10. Real-Time Performance Limitations
1. 11. API, Database, and Integration Limitations
1. 12. UI/UX and Accessibility Limitations
1. 13. Security, Privacy, and Ethical Limitations
1. 14. Deployment and Environment Limitations
1. 15. Device and Browser Compatibility Limitations
1. 16. Operational and Maintenance Limitations
1. 17. Workarounds and Mitigations
1. 18. Issue Prioritization and Resolution Policy
1. 19. Release Disclosure Requirements
1. 20. Known Limitations Acceptance
1. 21. Traceability to Project Documents
1. 22. Version History
1. 23. Review and Approval
## 1. Purpose

This document records known issues, technical constraints, functional boundaries, AI/ML limitations, environmental dependencies, and unresolved conditions associated with SignBridge AI. It provides a transparent reference for developers, testers, reviewers, maintainers, project stakeholders, and end users.

The document is intended to distinguish expected limitations from defects. A limitation describes a known boundary or constraint of the current system, while an issue may represent an unresolved defect, usability problem, integration problem, or operational concern.

## 2. Scope

- Camera-based Indian Sign Language recognition and related accessibility workflows.
- Video/image capture, hand/body landmark extraction, preprocessing, sequence construction, and model inference.
- Frontend, backend/API, database, model-serving, and integration layers.
- Real-time performance, device compatibility, deployment environments, and operational behavior.
- Known security, privacy, accessibility, and ethical constraints.
- Documented workarounds, mitigation actions, and release disclosure requirements.
## 3. Definitions

| Term | Definition |
| --- | --- |
| Known Issue | A recognized problem or undesirable behavior that has not yet been fully resolved. |
| Limitation | A known technical, functional, environmental, or model boundary that may be expected under defined conditions. |
| Workaround | A temporary or alternative procedure that reduces the impact of an issue or limitation. |
| Mitigation | An engineering, process, or operational control intended to reduce likelihood or impact. |
| Blocked Scenario | A condition under which a required feature cannot reliably complete its intended function. |
| Low Confidence | A model output whose confidence is below the configured acceptance threshold. |
| Out of Scope | A capability intentionally not supported by the current release or requirements. |
| Known Limitation ID | A unique identifier used to track a documented limitation, e.g., LIM-001. |

## 4. Issue and Limitation Classification

| Class | Description | Typical Response |
| --- | --- | --- |
| Critical Issue | Prevents a core workflow, causes severe security/privacy impact, or threatens data integrity. | Immediate escalation, containment, and release review. |
| High Issue | Significantly degrades a core capability or affects many supported scenarios. | Prioritize before production release where applicable. |
| Medium Issue | Affects usability, accuracy, compatibility, or secondary workflows without fully blocking the system. | Plan remediation and track to a target release. |
| Low Issue | Minor inconvenience, cosmetic problem, or low-impact edge case. | Backlog and resolve based on priority. |
| Known Limitation | Expected boundary rather than an implementation defect. | Document, mitigate, disclose, and reassess. |
| Accepted Limitation | Known limitation formally accepted for a defined release or environment. | Record owner, rationale, scope, and review date. |

## 5. Known Issues Register

The following baseline register is editable. Replace, add, or retire entries as project evidence changes.

| ID | Known Issue / Limitation | Area | Severity | Mitigation / Workaround | Status |
| --- | --- | --- | --- | --- | --- |
| LIM-001 | Recognition accuracy may decrease for signers or signing styles not adequately represented in the training data. | AI/ML | High | Expand signer diversity; collect additional data; validate signer-independent performance. | Open |
| LIM-002 | Low-light, backlit, cluttered, or visually complex scenes may reduce landmark quality and recognition reliability. | Computer Vision | High | Improve capture guidance, preprocessing, and robustness testing. | Open |
| LIM-003 | Fast or abrupt signing may cause temporal sequence loss or incomplete landmark tracking. | AI/ML / CV | High | Tune sequence handling, tracking, sampling, and temporal model. | Open |
| LIM-004 | Occlusion of hands or body landmarks can reduce recognition confidence. | Computer Vision | High | Add occlusion-aware data and fallback behavior. | Open |
| LIM-005 | Recognition latency may vary across devices because inference depends on CPU/GPU capability. | Performance | Medium | Benchmark supported devices and optimize inference pipeline. | Open |
| LIM-006 | Model confidence does not guarantee semantic correctness for every visually similar sign. | AI/ML | High | Use thresholds, confusion analysis, and explicit uncertain-state handling. | Open |
| LIM-007 | Browser camera permissions or unsupported devices may prevent capture. | Platform | Medium | Provide permission guidance and compatibility checks. | Open |
| LIM-008 | Network or backend availability may affect server-dependent workflows. | Integration | Medium | Add timeout, retry, health checks, and graceful failure states. | Open |
| LIM-009 | Dataset imbalance may result in uneven performance across sign classes. | Dataset | High | Measure per-class metrics and rebalance or augment data. | Open |
| LIM-010 | Text-to-sign or related generation features may have vocabulary and coverage constraints. | Functional | Medium | Clearly define supported vocabulary and provide unsupported-input feedback. | Open |
| LIM-011 | Environmental differences between development, testing, and deployment may produce performance variation. | Deployment | Medium | Use reproducible environments and deployment validation. | Open |
| LIM-012 | AI-generated code or rapid iterative changes may introduce regressions if insufficiently reviewed. | Engineering | High | Apply AI Coding Rules, code review, automated tests, and traceability. | Open |

## 6. Functional Limitations

- The system should only claim recognition capabilities supported by the approved model, vocabulary, and requirements.
- Signs outside the supported class set may be returned as unknown, low-confidence, or unsupported rather than being treated as valid predictions.
- Continuous free-form conversation may not be equivalent to isolated sign classification; segmentation and temporal context can affect results.
- Similar-looking signs may remain difficult to distinguish under limited visual information.
- Text-to-sign functionality, if enabled, may depend on available sign assets, vocabulary coverage, sequencing rules, and content mapping.
- Text-to-audio functionality depends on the selected text-to-speech engine, language support, and runtime availability.
- User-facing confidence or status indicators are not a substitute for semantic verification.
## 7. AI/ML Limitations

- Model performance is dependent on training-data quality, class balance, signer diversity, recording conditions, and labeling accuracy.
- Accuracy measured on a fixed test set does not guarantee equal real-world performance across all users or environments.
- The model may confuse visually similar signs, particularly when discriminative motion or hand configuration is poorly captured.
- Generalization to unseen signers, camera positions, backgrounds, clothing, lighting conditions, and signing speeds must be validated empirically.
- Confidence scores should be interpreted as model outputs rather than calibrated guarantees of correctness unless calibration has been validated.
- Model updates can improve some classes while reducing performance on others; every promoted model therefore requires regression evaluation.
- Changes in preprocessing, landmark extraction, sequence length, class mapping, or model architecture may invalidate compatibility with previous model artifacts.
## 8. Dataset Limitations

- Dataset coverage may not represent the full linguistic and regional diversity of Indian Sign Language.
- Participant count, signer diversity, camera conditions, and class distribution may limit generalization.
- Labels may contain ambiguity or annotation error; quality assurance and review are required before model training.
- Duplicate or near-duplicate samples across train, validation, and test sets can inflate reported performance if not controlled.
- Signer-aware or subject-independent splitting is required when the objective is to measure generalization to unseen signers.
- Augmentation can improve robustness but cannot fully replace real-world diversity.
- Dataset licenses, consent, provenance, retention, and permitted use must be tracked independently of model metrics.
## 9. Computer Vision and Tracking Limitations

- Landmark detection may degrade when hands are outside the frame, heavily occluded, blurred, too small, or poorly illuminated.
- Multiple people in the frame may create ambiguity unless the application explicitly supports multi-person tracking.
- Camera angle, distance, field of view, and device orientation can affect landmark geometry.
- Background clutter and visual similarity between the signer and surroundings can reduce tracking stability.
- Rapid motion may introduce motion blur and temporal discontinuity.
- Dropped frames or variable frame rates can affect sequence consistency.
## 10. Real-Time Performance Limitations

- End-to-end latency includes capture, landmark extraction, preprocessing, sequence buffering, inference, postprocessing, and UI rendering.
- Performance targets should be measured on representative hardware rather than assumed from development-machine results.
- Higher model complexity may improve recognition quality while increasing latency or memory usage.
- Thermal throttling, background applications, browser load, and power-saving modes can reduce sustained performance.
- Network-dependent inference introduces additional latency and variability compared with local inference.
- Performance benchmarks must report hardware, software versions, input configuration, batch/sequence settings, and measurement method.
## 11. API, Database, and Integration Limitations

- API behavior depends on schema compatibility between frontend, backend, model service, and database layers.
- Breaking API or model-contract changes may require coordinated frontend/backend/model deployment.
- Transient network failures can interrupt requests or create timeouts.
- Database availability, connection limits, migrations, or schema mismatches can affect application functionality.
- External services such as speech synthesis or storage may introduce availability, quota, latency, or compatibility constraints.
- Error responses should not expose secrets, internal stack traces, sensitive user data, or unnecessary model details.
## 12. UI/UX and Accessibility Limitations

- Camera-based interaction may be difficult for users with limited device access, poor camera placement, or restricted mobility.
- Instructions and visual feedback must remain understandable without relying exclusively on color.
- Recognition uncertainty must be communicated clearly so users are not misled by incorrect predictions.
- Responsive behavior may vary across screen sizes and browsers.
- Accessibility support depends on the implemented keyboard, screen-reader, contrast, typography, audio, and interaction requirements.
- The system is an assistive technology and should not be represented as a replacement for human interpreters in contexts requiring high-stakes or legally certified interpretation.
## 13. Security, Privacy, and Ethical Limitations

- Camera and video data can contain sensitive personal information; collection, processing, storage, and retention must follow the approved privacy design.
- The system should minimize collection and avoid retaining raw media unless there is a documented requirement and appropriate authorization.
- Model and application outputs may be inaccurate and must not be treated as authoritative in high-risk decisions without appropriate human verification.
- Dataset consent and permitted-use requirements may limit redistribution, retraining, or publication of certain samples.
- Logs should avoid unnecessary personal data and must be access-controlled.
- Bias and unequal performance across signer groups should be treated as measurable model risks requiring monitoring and mitigation.
## 14. Deployment and Environment Limitations

- Local development, staging, and production environments may differ in hardware, operating system, runtime, network, and dependency versions.
- Containerized or reproducible deployment reduces but does not eliminate infrastructure-specific differences.
- Model artifacts must be compatible with the deployed runtime and preprocessing pipeline.
- Insufficient compute resources can cause slow inference, memory pressure, or service instability.
- Production deployment requires health checks, logging, rollback capability, configuration management, and release validation.
## 15. Device and Browser Compatibility Limitations

| Environment | Potential Limitation | Validation / Workaround |
| --- | --- | --- |
| Low-end mobile/desktop | Reduced FPS, increased latency, memory pressure. | Use optimized models, lower resolution where acceptable, and test resource limits. |
| Older browsers | Camera API, WebRTC, WebGL/WebGPU, or media feature incompatibility. | Maintain a supported-browser matrix and provide upgrade guidance. |
| Mobile browsers | Permission prompts, background throttling, orientation changes. | Handle permissions and lifecycle events explicitly. |
| Integrated webcams | Variable resolution, exposure, focus, and frame rate. | Provide capture guidance and test representative devices. |
| External cameras | Driver or permission differences. | Validate device enumeration and provide fallback instructions. |
| Restricted networks | Backend/API/TTS access may fail. | Use timeout handling and clear offline/unavailable states. |

## 16. Operational and Maintenance Limitations

- Model quality can degrade relative to new real-world conditions if the dataset is not periodically reviewed and expanded.
- Dependency updates may change computer-vision, browser, framework, or model-runtime behavior.
- Operational logs and metrics require retention and access policies appropriate to the data they contain.
- Known issues may become obsolete after a model, dataset, browser, or architecture change and therefore require periodic review.
- Maintenance work must preserve model/version traceability and avoid undocumented changes to production behavior.
## 17. Workarounds and Mitigations

| Scenario | Recommended Workaround | Owner | Status |
| --- | --- | --- | --- |
| Low confidence | Repeat the sign in a well-lit area with the full hand/body region visible. | [Owner] | Available |
| Poor tracking | Move the camera farther/closer as instructed and keep signing region within frame. | [Owner] | Available |
| Unsupported sign | Show unsupported/unknown feedback instead of forcing a prediction. | [Owner] | Available |
| High latency | Reduce input resolution or use a supported device/runtime configuration. | [Owner] | Planned |
| Backend unavailable | Display service-unavailable state and retry according to policy. | [Owner] | Planned |
| Browser incompatibility | Use a supported browser/device from the compatibility matrix. | [Owner] | Available |
| Model regression | Rollback to the last approved model artifact. | [Owner] | Planned |

## 18. Issue Prioritization and Resolution Policy

1. Every known issue should receive a unique ID and classification.
1. Critical security, privacy, data-integrity, and core-function failures must be escalated immediately.
1. Issues affecting model correctness should include reproducible evidence, affected model/version, dataset or input context, and relevant metrics where available.
1. A limitation should not be reclassified as a defect solely because it is undesirable; the approved requirement and intended scope must be considered.
1. Resolved issues must be verified through retesting and regression testing where applicable.
1. Retired limitations must retain historical traceability rather than being silently deleted.
## 19. Release Disclosure Requirements

- Release documentation should disclose material known issues and limitations that may affect user expectations.
- Release notes should identify affected versions and relevant workarounds when available.
- Any known Critical or High issue must be reviewed during release readiness assessment.
- Model releases should disclose applicable evaluation scope, supported classes, and important environmental constraints.
- User-facing documentation should avoid claims of universal or guaranteed recognition accuracy.
## 20. Known Limitations Acceptance

| Limitation ID | Accepted For Version | Accepted By | Rationale | Review Date | Status |
| --- | --- | --- | --- | --- | --- |
| LIM-[ID] | [Version] | [Name] | [Reason for acceptance] | [Date] | Open |
| LIM-[ID] | [Version] | [Name] | [Reason for acceptance] | [Date] | Open |
| LIM-[ID] | [Version] | [Name] | [Reason for acceptance] | [Date] | Open |

## 21. Traceability to Project Documents

| Related Document | Relationship |
| --- | --- |
| 01 Project PRD | Defines product scope, goals, user needs, and expected capabilities that establish limitation boundaries. |
| 02 SRS | Provides functional and non-functional requirements against which issues and limitations are assessed. |
| 03 System Architecture | Defines architectural dependencies and component boundaries relevant to technical limitations. |
| 04 Dataset Specification | Defines dataset scope, provenance, participant coverage, labels, splits, and quality constraints. |
| 05 AI Model Specification | Defines model scope, inputs, outputs, metrics, and compatibility constraints. |
| 06 Preprocessing & Feature Engineering | Defines landmark processing and feature pipeline assumptions. |
| 07 API Contract | Defines integration behavior, schemas, errors, and compatibility expectations. |
| 09 UI/UX Specification | Defines user interaction, accessibility, feedback, and usability expectations. |
| 11 Testing & Evaluation | Defines validation, metrics, test coverage, and release quality gates. |
| 12 Deployment | Defines runtime, infrastructure, release, rollback, and operational constraints. |
| 13 Security, Privacy & Ethics | Defines controls and boundaries for sensitive data and responsible system use. |
| 23 Model Training Specification | Defines training process, evaluation, reproducibility, and model promotion constraints. |
| 24 Model Versioning & Experiment Log | Provides model/experiment traceability for issue investigation. |
| 25 Performance Benchmark | Provides empirical latency, FPS, throughput, and resource measurements. |
| 30 Bug & Defect Log | Tracks implementation defects separately from documented product limitations. |
| 31 Risk Register | Tracks potential future impact and mitigation for material technical and operational risks. |

## 22. Version History

| Version | Date | Author | Change Description |
| --- | --- | --- | --- |
| 1.0 | [Enter Date] | [Enter Name] | Initial Known Issues & Limitations document. |
| 1.1 | [Enter Date] | [Enter Name] | [Enter changes] |
| 1.2 | [Enter Date] | [Enter Name] | [Enter changes] |

## 23. Review and Approval

| Role | Name | Signature / Approval | Date |
| --- | --- | --- | --- |
| Prepared By | [Enter Name] | [Enter] | [Date] |
| Reviewed By | [Enter Name] | [Enter] | [Date] |
| Technical Lead | [Enter Name] | [Enter] | [Date] |
| Project Owner | [Enter Name] | [Enter] | [Date] |
| Approved By | [Enter Name] | [Enter] | [Date] |

*Document Control Note: This document is editable and should be updated whenever a known issue is resolved, a limitation changes, a new release introduces a material constraint, or validation evidence changes the understanding of system behavior.*
