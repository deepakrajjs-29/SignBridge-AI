<!-- Source: 30_Bug_Defect_Log_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# SIGNBRIDGE AI

## BUG & DEFECT LOG

*Defect Registration, Triage, Resolution, Verification and Release Tracking*

| Field | Value |
| --- | --- |
| Document ID | SBAI-BDL-001 |
| Document Number | 30_Bug_Defect_Log |
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

4. Defect Management Principles

5. Defect ID Convention

6. Defect Categories

7. Severity Definitions

8. Priority Definitions

9. Defect Status Lifecycle

10. Source and Detection Methods

11. Defect Workflow

12. Defect Intake Rules

13. Defect Description Standards

14. Reproduction Standards

15. Evidence Requirements

16. Environment and Version Capture

17. Triage Rules

18. Ownership and Assignment

19. Root Cause Analysis

20. Impact Analysis

21. Workaround and Mitigation

22. Fix Development Rules

23. Fix Verification and Retesting

24. Regression Verification

25. Closure Rules

26. Reopen Rules

27. Duplicate Defects

28. Deferred and Accepted Defects

29. Security Defects

30. Privacy Defects

31. AI/ML Defects

32. Computer Vision Defects

33. API and Database Defects

34. UI/UX Defects

35. Performance Defects

36. Deployment Defects

37. Defect Metrics

38. Release Defect Gate

39. Defect Aging and Escalation

40. Defect Review Meeting

41. Defect Register Template

42. Initial Defect Register

43. Retest Record

44. Root Cause Record

45. Release Defect Summary

46. Defect Automation and Tooling

47. Editable Defect Parameters

48. Defect Checklist

49. Assumptions and Open Questions

50. Related Documents

51. Version History and Approval

## 1. Purpose

This Bug & Defect Log defines the controlled process for identifying, recording, triaging, assigning, fixing, verifying, closing, and reporting defects in SignBridge AI. It provides a reusable defect register and ensures that defects remain traceable to test cases, requirements, components, model versions, releases, and evidence.

## 2. Scope

- Frontend and UI defects.
- Camera, MediaPipe, landmark, preprocessing, and computer vision defects.
- AI/model, dataset, feature, inference, and evaluation defects.
- REST/WebSocket API defects.
- Database and data-integrity defects.
- Security and privacy defects.
- Performance, load, concurrency, and resource defects.
- Deployment, infrastructure, configuration, and release defects.
- Documentation and configuration defects that materially affect system behavior.
## 3. Objectives

- Provide one controlled record for every confirmed defect.
- Enable reproducible defect investigation.
- Separate severity from priority.
- Track ownership and lifecycle state.
- Capture root cause and corrective action.
- Ensure every fix is retested and regression-checked.
- Support release decisions with objective defect data.
- Identify recurring defect patterns and quality risks.
## 4. Defect Management Principles

| Principle | Rule |
| --- | --- |
| Reproducibility | A defect should include enough information to reproduce it where possible. |
| Evidence | Record relevant logs, screenshots, requests, model versions, and test data. |
| Traceability | Link defect to test, requirement, component, release, and fix. |
| No blame | Focus on system/process root cause, not individual blame. |
| Severity ≠ priority | Impact and urgency are tracked separately. |
| Controlled closure | Only authorized owners/reviewers close defects. |
| Regression protection | Confirmed defects should receive regression coverage when practical. |
| Security/privacy | Potential critical security or privacy issues are escalated immediately. |

## 5. Defect ID Convention

| ID Type | Format | Example |
| --- | --- | --- |
| Defect | BUG-YYYY-NNNN | BUG-2026-0001 |
| Security | SECBUG-YYYY-NNN | SECBUG-2026-001 |
| Privacy | PRIBUG-YYYY-NNN | PRIBUG-2026-001 |
| Model | MLBUG-YYYY-NNN | MLBUG-2026-001 |
| Performance | PERFBUG-YYYY-NNN | PERFBUG-2026-001 |
| Release blocker | RELBUG-YYYY-NNN | RELBUG-2026-001 |

## 6. Defect Categories

- Functional
- UI/UX
- Camera
- Computer Vision
- MediaPipe/Landmark
- Preprocessing/Feature Engineering
- Sequence Processing
- AI/Model
- Dataset/Data
- API/REST
- WebSocket
- Database
- Security
- Privacy
- Accessibility
- Performance
- Load/Stress
- Deployment/Infrastructure
- Configuration
- Documentation
## 7. Severity Definitions

| Severity | Definition | Typical Example |
| --- | --- | --- |
| Critical | System/security/privacy failure with severe impact or release-blocking consequence. | Unauthorized data exposure; production-wide failure; severe integrity issue. |
| High | Major functionality broken or significant quality/security impact. | Core recognition unavailable; critical API flow broken. |
| Medium | Important defect with limited scope or workaround. | History filter fails; secondary feature malfunction. |
| Low | Minor impact, cosmetic, or non-blocking issue. | Spacing, wording, minor UI inconsistency. |

## 8. Priority Definitions

| Priority | Definition |
| --- | --- |
| P0 | Immediate attention; release/operation should stop until resolved or explicitly accepted. |
| P1 | High urgency; normally resolved before relevant release. |
| P2 | Planned for current/near-term iteration. |
| P3 | Backlog/low urgency. |

Priority may differ from severity. For example, a medium-severity issue affecting a release-critical feature may be P1.

## 9. Defect Status Lifecycle

| Status | Meaning |
| --- | --- |
| New | Defect submitted and awaiting triage. |
| Triaged | Reviewed and categorized. |
| Assigned | Owner identified. |
| In Progress | Investigation/fix underway. |
| Blocked | Cannot proceed due to dependency. |
| Fixed | Developer indicates corrective change is implemented. |
| Ready for Retest | Build/version available for verification. |
| Retest Failed | Fix did not resolve defect or introduced related issue. |
| Verified | Fix confirmed by testing. |
| Closed | Defect lifecycle completed. |
| Reopened | Previously verified/closed defect has recurred. |
| Deferred | Intentionally postponed. |
| Rejected | Not considered a valid defect after review. |
| Duplicate | Covered by another defect. |
| Cannot Reproduce | Unable to reproduce with available evidence; retained for monitoring. |

## 10. Source and Detection Methods

| Source | Examples |
| --- | --- |
| Automated test | CI/unit/API/E2E failure |
| Manual test | QA/tester discovery |
| User feedback | Reported usability/function issue |
| Monitoring | Runtime alert/log/metric |
| Security review | Security assessment/scan |
| Privacy review | Data-flow/privacy assessment |
| Model evaluation | Accuracy/F1/confusion/robustness regression |
| Performance benchmark | Latency/FPS/resource regression |
| Code review | Static inspection |
| Deployment | Smoke/health-check failure |

## 11. Defect Workflow

1. Detect and capture evidence.
1. Create defect record.
1. Check for duplicate.
1. Reproduce or validate the report.
1. Assign category, severity, and priority.
1. Assign owner.
1. Analyze impact and root cause.
1. Implement corrective change.
1. Run targeted verification.
1. Run relevant regression tests.
1. Retest and capture evidence.
1. Close or reopen.
1. Include in release/quality reporting.
## 12. Defect Intake Rules

- Create one defect for one distinct problem unless multiple failures share one root cause.
- Use a clear, specific title.
- Include actual and expected results.
- Include exact reproduction steps.
- Record software/model/data versions.
- Attach sanitized evidence.
- Link the failed test case when applicable.
- Do not include passwords, tokens, or unnecessary personal data.
## 13. Defect Description Standards

| Field | Required Guidance |
| --- | --- |
| Title | Concise symptom + affected area. |
| Summary | What happened. |
| Expected | What should happen. |
| Actual | What actually happened. |
| Impact | Who/what is affected. |
| Frequency | Always/intermittent/rare. |
| Reproduction | Numbered reproducible steps. |
| Scope | Affected environments/versions. |
| Evidence | Logs/screenshots/request IDs. |
| Workaround | Available mitigation if any. |

## 14. Reproduction Standards

1. Start from a clean or documented state.
1. Record exact application/API/model/data versions.
1. Use the same or equivalent test data.
1. Record configuration and environment.
1. Follow minimal reproduction steps.
1. Record whether the issue is deterministic or intermittent.
1. Attempt reproduction in a controlled environment when practical.
## 15. Evidence Requirements

- Evidence must be relevant and sanitized.
- Capture screenshots for UI defects when useful.
- Capture request/response details for API defects without secrets.
- Capture logs and correlation IDs for backend defects.
- Capture model/dataset/feature versions for AI defects.
- Capture benchmark output and hardware for performance defects.
- Do not attach raw camera/video or sensitive personal data unless explicitly authorized.
## 16. Environment and Version Capture

| Field | Value |
| --- | --- |
| Application Version | [Enter] |
| API Version | [Enter] |
| Model Version | [Enter] |
| Dataset Version | [Enter] |
| Feature Version | [Enter] |
| Frontend Build | [Enter] |
| Backend Build | [Enter] |
| Database Version | [Enter] |
| OS | [Enter] |
| Browser | [Enter] |
| Hardware | [Enter] |
| Network | [Enter] |
| Configuration Profile | [Enter] |

## 17. Triage Rules

- Confirm whether the issue is reproducible or sufficiently evidenced.
- Identify affected functionality and users.
- Assess security/privacy/data integrity impact first.
- Assign severity based on impact, not effort to fix.
- Assign priority based on urgency, release relevance, and risk.
- Identify dependencies and owner.
- Escalate critical security/privacy/data-loss issues immediately.
## 18. Ownership and Assignment

| Role | Responsibility |
| --- | --- |
| Reporter | Provides accurate reproduction/evidence. |
| QA/Test Owner | Validates defect and retest. |
| Developer | Investigates and implements fix. |
| AI/ML Owner | Handles model/data/feature defects. |
| Security Owner | Reviews security defects. |
| Privacy Owner | Reviews privacy-sensitive defects. |
| Release Owner | Assesses release impact. |
| Project Owner | Resolves priority/deferment decisions. |

## 19. Root Cause Analysis

Root cause analysis should identify the underlying condition that allowed the defect, not merely the visible symptom.

| Root Cause Category | Examples |
| --- | --- |
| Requirements | Ambiguous/missing requirement |
| Design | Incorrect architecture/algorithm |
| Implementation | Logic or coding error |
| Integration | Interface mismatch |
| Data | Bad label, leakage, schema/data-quality issue |
| Model | Training/generalization/calibration issue |
| Configuration | Incorrect environment setting |
| Dependency | Library/runtime incompatibility |
| Testing | Missing or insufficient test |
| Deployment | Infrastructure/release configuration |
| Process | Review or change-control gap |

## 20. Impact Analysis

- Identify affected users/workflows.
- Identify affected environments.
- Identify whether data integrity is at risk.
- Identify security/privacy impact.
- Identify model accuracy or fairness impact where relevant.
- Identify performance/resource impact.
- Identify dependent components and releases.
- Determine whether rollback is needed.
## 21. Workaround and Mitigation

| Field | Guidance |
| --- | --- |
| Workaround | Temporary action reducing impact. |
| Mitigation | Control reducing risk until permanent fix. |
| Limitations | State what remains broken. |
| Owner | Person/team responsible. |
| Expiry | Date/version by which workaround should be reviewed. |

## 22. Fix Development Rules

- Fix the root cause where practical.
- Keep the fix within approved architecture.
- Add or update regression tests.
- Do not weaken existing security/privacy controls.
- Do not introduce unrelated refactoring.
- Update documentation/contracts if behavior changes.
- Record the fixing commit/PR/build.
## 23. Fix Verification and Retesting

1. Verify the corrected behavior against the original reproduction.
1. Run the linked test case.
1. Run relevant component regression tests.
1. Check for side effects.
1. Record the tested build/model/data version.
1. Attach evidence.
1. Mark Verified only when acceptance conditions are met.
## 24. Regression Verification

- Run direct regression tests for the affected component.
- Run dependent integration tests.
- Run critical end-to-end tests for core flows.
- Run model evaluation when the defect affects AI behavior.
- Run performance tests when the defect/fix touches a hot path.
- Document any intentionally excluded regression scope.
## 25. Closure Rules

| Closure Condition | Required Evidence |
| --- | --- |
| Verified fix | Retest passed. |
| Documentation update | Affected documentation updated if required. |
| Traceability | Requirement/test/fix linkage maintained. |
| No open blocker | No unresolved release-blocking dependency. |
| Owner approval | Authorized tester/reviewer confirms closure. |

## 26. Reopen Rules

- Reopen when the same defect recurs.
- Reopen when the fix only masks the symptom.
- Reopen when acceptance criteria are not actually met.
- Create a new defect when the behavior is materially different, while linking the original.
- Record recurrence evidence and affected versions.
## 27. Duplicate Defects

1. Compare title, symptom, component, version, and reproduction.
1. Identify the earliest/master defect.
1. Mark duplicate status and link to master defect.
1. Preserve original evidence.
1. Do not lose reporter context.
1. Track duplicate counts for quality analysis where useful.
## 28. Deferred and Accepted Defects

| Decision | Required Information |
| --- | --- |
| Deferred | Reason, target release, risk, owner. |
| Accepted risk | Explicit approver, rationale, mitigation. |
| Won't fix | Reason and affected scope. |
| Known issue | User/release communication if applicable. |

Critical security, privacy, or data-integrity defects should not be silently accepted as routine backlog items.

## 29. Security Defects

- Escalate suspected vulnerabilities immediately.
- Limit disclosure to authorized personnel.
- Do not publish exploit details unnecessarily.
- Record affected components and versions.
- Assess credential/data exposure.
- Rotate exposed secrets where applicable.
- Require security review before closure for material security defects.
## 30. Privacy Defects

- Assess whether personal, camera, landmark, or history data was exposed or retained incorrectly.
- Identify scope and affected data.
- Preserve evidence without unnecessary sensitive copies.
- Apply containment and deletion where appropriate.
- Review retention, consent, access, and logging controls.
- Require privacy review for material privacy defects.
## 31. AI/ML Defects

| Defect Type | Examples |
| --- | --- |
| Accuracy | Incorrect sign classification. |
| Class mapping | Wrong label for output index. |
| Confidence | Overconfident wrong prediction. |
| Temporal | Incorrect sequence interpretation. |
| Data | Label/split/quality issue. |
| Feature | Normalization or feature calculation error. |
| Training | Leakage, unstable training, wrong loss/config. |
| Inference | Tensor/model compatibility issue. |
| Robustness | Unexpected degradation under conditions. |
| Fairness | Material performance disparity requiring investigation. |
| Versioning | Wrong model/feature/dataset artifact deployed. |

## 32. Computer Vision Defects

- Landmarks missing or incorrectly mapped.
- Hand-selection logic fails.
- Coordinate normalization incorrect.
- Tracking loss not handled.
- Frame conversion/resolution errors.
- Performance degradation in frame loop.
- Camera resource leak.
- Multiple-person behavior incorrect.
## 33. API and Database Defects

| Area | Examples |
| --- | --- |
| API | Wrong status code, schema mismatch, validation failure. |
| WebSocket | Dropped events, incorrect lifecycle, message ordering. |
| Database | Constraint failure, incorrect transaction, query error. |
| Migration | Upgrade/rollback failure. |
| Data integrity | Incorrect session/prediction relationship. |
| Retention | Data not deleted according to policy. |

## 34. UI/UX Defects

- Incorrect recognition state display.
- Unclear error/recovery message.
- Camera permission flow failure.
- Incorrect result presentation.
- Responsive layout issue.
- Accessibility failure.
- Unexpected loading/focus behavior.
- History/settings inconsistency.
## 35. Performance Defects

| Defect | Evidence |
| --- | --- |
| Latency regression | p50/p95/p99 comparison. |
| FPS regression | Measured real-time FPS. |
| Memory leak | Memory over time. |
| CPU/GPU spike | Resource profile. |
| API throughput regression | RPS/error/latency. |
| Database slowdown | Query timing/plan. |
| Startup regression | Initialization time. |

## 36. Deployment Defects

- Container build/startup failure.
- Incorrect environment configuration.
- Migration failure.
- Model artifact mismatch.
- Health-check failure.
- TLS/networking failure.
- Scaling/resource configuration issue.
- Rollback failure.
- Monitoring/logging failure.
## 37. Defect Metrics

| Metric | Purpose |
| --- | --- |
| Open defects | Current defect backlog. |
| Critical/High open | Release risk indicator. |
| Defect arrival rate | New defects per period. |
| Defect closure rate | Resolved defects per period. |
| Defect aging | Time defects remain open. |
| Reopen rate | Fix quality indicator. |
| Duplicate rate | Detection/process quality. |
| Escaped defects | Production quality indicator. |
| Defect density | Defects per scope/unit. |
| Root-cause distribution | Identify systemic problem areas. |

## 38. Release Defect Gate

| Gate | Initial Rule |
| --- | --- |
| Critical defects | 0 unresolved unless explicitly approved by authorized governance. |
| High defects | [Enter release rule] |
| Security critical | 0 unresolved. |
| Privacy critical | 0 unresolved. |
| Data-integrity critical | 0 unresolved. |
| Core E2E defects | All P0 cases pass. |
| Regression | Required suite passes. |
| Known issues | Documented and approved. |
| Rollback | Available for release. |

## 39. Defect Aging and Escalation

| Age | Suggested Action |
| --- | --- |
| 0–2 days | Normal triage/fix flow. |
| 3–7 days | Owner review. |
| 8–14 days | Escalate to project/release owner if P1/P2. |
| >14 days | Formal review of risk, deferment, or escalation. |
| Critical any age | Immediate escalation based on impact. |

Aging thresholds are editable project parameters.

## 40. Defect Review Meeting

- Review new critical/high defects.
- Review blocked defects.
- Review aging defects.
- Review reopened defects.
- Review production/escaped defects.
- Review recurring root causes.
- Confirm release impact and owners.
- Record decisions and action items.
## 41. Defect Register Template

| Field | Value |
| --- | --- |
| Defect ID | BUG-YYYY-NNNN |
| Title | [Short defect title] |
| Category | [Category] |
| Severity | [Critical/High/Medium/Low] |
| Priority | [P0/P1/P2/P3] |
| Status | [New/Triaged/etc.] |
| Reporter | [Name] |
| Owner | [Name] |
| Detected Date | [Date] |
| Environment | [Environment] |
| App/API Version | [Version] |
| Model Version | [Version] |
| Dataset/Feature Version | [Version] |
| Requirement/Test Case | [ID] |
| Component/Module | [ID] |
| Expected Result | [Enter] |
| Actual Result | [Enter] |
| Reproduction Steps | [Enter] |
| Evidence | [Link/path] |
| Impact | [Enter] |
| Root Cause | [Enter] |
| Workaround | [Enter] |
| Fix | [Enter] |
| Fix Commit/PR | [Enter] |
| Fix Version | [Enter] |
| Retest Result | [Pass/Fail] |
| Regression Result | [Pass/Fail] |
| Closure Date | [Date] |
| Approver | [Name] |

## 42. Initial Defect Register

| Defect ID | Title | Severity | Priority | Status | Owner | Linked Test | Release |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BUG-2026-0001 | [Enter defect] | [Enter] | [Enter] | New | [Enter] | [TC-XXX] | [vX.X] |
| BUG-2026-0002 | [Enter defect] | [Enter] | [Enter] | New | [Enter] | [TC-XXX] | [vX.X] |
| BUG-2026-0003 | [Enter defect] | [Enter] | [Enter] | New | [Enter] | [TC-XXX] | [vX.X] |
| BUG-2026-0004 | [Enter defect] | [Enter] | [Enter] | New | [Enter] | [TC-XXX] | [vX.X] |

## 43. Retest Record

| Field | Value |
| --- | --- |
| Defect ID | [BUG-YYYY-NNNN] |
| Fix Version | [Enter] |
| Retest Build | [Enter] |
| Tester | [Enter] |
| Original Reproduction | [Re-run] |
| Expected Result | [Enter] |
| Actual Result | [Enter] |
| Status | [Pass/Fail] |
| Evidence | [Enter] |
| Regression Suite | [Pass/Fail] |
| Date | [Enter] |

## 44. Root Cause Record

| Field | Value |
| --- | --- |
| Defect ID | [BUG-YYYY-NNNN] |
| Observed Symptom | [Enter] |
| Root Cause Category | [Requirements/Design/Implementation/Data/etc.] |
| Root Cause | [Enter] |
| Contributing Factors | [Enter] |
| Detection Gap | [Enter] |
| Corrective Action | [Enter] |
| Preventive Action | [Enter] |
| Regression Test | [TC-XXX] |
| Owner | [Enter] |
| Date | [Enter] |

## 45. Release Defect Summary

| Metric | Value |
| --- | --- |
| Release | [vX.X] |
| Total Defects | [Enter] |
| New | [Enter] |
| Closed | [Enter] |
| Open | [Enter] |
| Critical Open | [Enter] |
| High Open | [Enter] |
| Medium Open | [Enter] |
| Low Open | [Enter] |
| Reopened | [Enter] |
| Deferred | [Enter] |
| Escaped to Production | [Enter] |
| Security Defects | [Enter] |
| Privacy Defects | [Enter] |
| Model Defects | [Enter] |
| Release Decision | [Approved / Hold / Conditional] |

## 46. Defect Automation and Tooling

- Use issue/test-management integration where available.
- Link automated test failures to defects where practical.
- Capture CI build IDs.
- Use static analysis/security scanners for automated detection.
- Use performance benchmark reports for regression detection.
- Track model evaluation failures as structured experiment/defect records.
- Automate aging and release-risk dashboards where practical.
## 47. Editable Defect Parameters

| Parameter | Value |
| --- | --- |
| Defect Repository Tool | [Enter] |
| Defect Owner | [Enter] |
| Critical Escalation SLA | [Enter] |
| High Priority SLA | [Enter] |
| Defect Aging Threshold | [Enter] |
| Release Critical Defect Rule | [0 unresolved / approved exception] |
| Release High Defect Rule | [Enter] |
| Security Escalation Contact | [Enter] |
| Privacy Escalation Contact | [Enter] |
| Retest Owner | [Enter] |
| Root Cause Required For | [Critical/High/All] |
| Regression Test Required | [Critical/High/All applicable] |
| Evidence Retention | [Enter] |

## 48. Defect Checklist

☐ Unique defect ID assigned

☐ Clear title and category

☐ Severity and priority assigned

☐ Environment/version recorded

☐ Expected and actual results documented

☐ Reproduction steps provided

☐ Evidence attached/sanitized

☐ Linked test/requirement recorded

☐ Owner assigned

☐ Impact assessed

☐ Root cause recorded for required defects

☐ Fix linked to commit/PR/build

☐ Retest completed

☐ Regression verified

☐ Closure/deferment decision approved

☐ Release impact recorded

## 49. Assumptions and Open Questions

- Exact defect-management platform is configurable.
- Severity and priority definitions may be adapted to organizational policy.
- Critical security/privacy/data defects require immediate escalation.
- Root-cause analysis depth may vary by severity.
- Open question: Which issue-tracking platform will be the official defect repository?
- Open question: What exact SLA applies to P0/P1 defects?
- Open question: Which roles can approve accepted-risk or deferred defects?
- Open question: Which defect metrics will be shown on the project quality dashboard?
## 50. Related Documents

| Document | Relationship |
| --- | --- |
| 02 SRS | Requirement basis |
| 03 System Architecture | Component and dependency impact |
| 11 Testing & Evaluation | Defect detection and verification |
| 13 Security, Privacy & Ethics | Security/privacy defect handling |
| 20 Requirements Traceability Matrix | Defect-to-requirement traceability |
| 25 Performance Benchmark | Performance defect evidence |
| 29 Test Case Repository | Test-to-defect linkage |
| 26 Coding Standards | Implementation quality standards |
| 27 AI Coding Rules | AI-generated code defect handling |
| 28 AI Agent Instructions | Agent verification and handoff rules |

## 51. Version History and Approval

| Version | Date | Author | Change Summary | Status |
| --- | --- | --- | --- | --- |
| 0.1 | [Enter date] | [Enter name] | Initial bug and defect log | Draft |
| 1.0 | [Enter date] | [Enter name] | Baseline approved defect management document | [Draft / Review / Approved] |

| Approval Role | Name | Signature | Date |
| --- | --- | --- | --- |
| Prepared By | [Enter name] | [Signature] | [Date] |
| Reviewed By | [Enter name] | [Signature] | [Date] |
| Approved By | [Enter name] | [Signature] | [Date] |
