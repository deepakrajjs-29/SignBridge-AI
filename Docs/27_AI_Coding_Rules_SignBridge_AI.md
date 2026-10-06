<!-- Source: 27_AI_Coding_Rules_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# SIGNBRIDGE AI

## AI CODING RULES

*Rules for AI-Assisted Software Development and Vibe Coding*

| Field | Value |
| --- | --- |
| Document ID | SBAI-AICR-001 |
| Document Number | 27_AI_Coding_Rules |
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

3. AI Coding Philosophy

4. Core Governance Principles

5. Human Ownership Rule

6. AI Role and Boundaries

7. Approved AI Coding Tasks

8. Restricted AI Coding Tasks

9. Prohibited AI Coding Behavior

10. Source-of-Truth Hierarchy

11. Project Context Rules

12. Prompt Construction Rules

13. Prompt Template

14. Context Packaging

15. Requirements Traceability

16. Architecture Protection

17. Code Generation Rules

18. Code Modification Rules

19. Code Review Rules

20. Testing Rules for AI-Generated Code

21. Debugging Rules

22. Refactoring Rules

23. Dependency Rules

24. Security Rules

25. Privacy and Sensitive Data Rules

26. Secret Management

27. API Coding Rules

28. Database Coding Rules

29. Frontend Coding Rules

30. Computer Vision Coding Rules

31. AI/ML Coding Rules

32. Dataset and Training Rules

33. Model Inference Rules

34. Performance Rules

35. Error Handling Rules

36. Documentation Rules

37. Git and Commit Rules

38. Pull Request Rules

39. AI Code Review Checklist

40. Hallucination Prevention

41. Verification Before Claiming Success

42. Change Size and Scope Control

43. Tool and Command Execution Rules

44. CI/CD and Release Rules

45. Incident and Rollback Rules

46. AI Coding Quality Metrics

47. Editable AI Coding Parameters

48. AI Coding Workflow

49. Definition of Done

50. AI Coding Checklist

51. Assumptions and Open Questions

52. Related Documents

53. Version History and Approval

## 1. Purpose

This document defines mandatory rules for using AI coding assistants to design, generate, modify, debug, test, refactor, document, and review SignBridge AI software. It extends the project's Coding Standards and Vibe Coding Master Specification with operational rules for responsible AI-assisted development.

## 2. Scope

- Applies to all AI-generated or AI-modified source code.
- Applies to frontend, backend, API, database, computer vision, preprocessing, AI/ML, testing, deployment, scripts, and documentation code.
- Applies to code assistants, agentic coding tools, IDE assistants, chat-based coding tools, and automated code-generation workflows.
- Applies to developers, reviewers, researchers, and operators using AI during the project.
## 3. AI Coding Philosophy

| Principle | Rule |
| --- | --- |
| Assist, not replace | AI accelerates implementation; humans own engineering decisions. |
| Evidence over confidence | AI output is not accepted because it sounds correct. |
| Small changes | Prefer focused, reviewable changes. |
| Tests with code | New behavior should have relevant tests. |
| Traceability | Significant changes must map to requirements, issues, or experiments. |
| Security first | Never trade security/privacy for convenience. |
| Reproducibility | AI-assisted model/code changes should remain reproducible. |

## 4. Core Governance Principles

- Human approval is required before merging AI-generated production code.
- AI must follow the approved architecture, requirements, coding standards, and API/database/model contracts.
- AI must not silently change project scope.
- AI must not invent test results, benchmark results, deployment status, or external evidence.
- AI-generated code must pass the same quality gates as human-written code.
- Uncertain AI output must be treated as unverified.
## 5. Human Ownership Rule

The developer responsible for a change remains accountable for understanding, reviewing, testing, and approving the final implementation. Copying AI output without understanding its behavior is not considered an acceptable development practice.

## 6. AI Role and Boundaries

| AI May | AI Must Not Independently |
| --- | --- |
| Draft implementation options | Redefine project scope |
| Generate boilerplate | Replace approved architecture without review |
| Suggest tests | Merge code to protected branches |
| Explain errors | Declare unverified code production-ready |
| Suggest refactors | Disable security/privacy controls to make code work |
| Generate documentation | Expose secrets or sensitive project data |
| Analyze logs/code supplied safely | Invent benchmark/test/deployment evidence |

## 7. Approved AI Coding Tasks

- Generate boilerplate and repetitive code.
- Create unit-test scaffolding.
- Explain existing code.
- Suggest debugging hypotheses.
- Refactor code while preserving behavior.
- Generate API client/server scaffolding from approved contracts.
- Generate SQL migration drafts.
- Generate type definitions from approved schemas.
- Suggest performance optimizations for measured bottlenecks.
- Draft documentation and comments.
- Assist with model/training experiment code under human review.
## 8. Restricted AI Coding Tasks

| Task | Required Control |
| --- | --- |
| Authentication/security code | Human security review + tests |
| Privacy-sensitive processing | Explicit privacy review |
| Database migrations | Review + migration test |
| Model architecture changes | Experiment ID + evaluation |
| Feature engineering changes | Feature version + regression evaluation |
| Production deployment code | Human approval + release gate |
| Dependency upgrades | Security scan + test suite |
| Camera/video persistence | Explicit requirement and privacy review |
| High-impact behavior changes | Formal requirement/approval traceability |

## 9. Prohibited AI Coding Behavior

- Generating or committing secrets, credentials, private keys, or tokens.
- Disabling security checks merely to make tests pass.
- Deleting tests to make a build green.
- Changing acceptance criteria without authorization.
- Fabricating successful execution or benchmark results.
- Silently removing privacy controls.
- Introducing unapproved telemetry or data collection.
- Uploading confidential datasets or raw user camera data to an AI tool unless explicitly authorized.
- Bypassing code review or release controls.
- Creating hidden backdoors, undocumented admin access, or insecure bypasses.
## 10. Source-of-Truth Hierarchy

1. Approved project requirements and PRD/SRS.
1. Approved system architecture and component/module design.
1. Approved API, database, UI/UX, dataset, model, security, and deployment specifications.
1. Approved coding standards and AI coding rules.
1. Approved issue/task/experiment requirements.
1. Existing tested code and established project conventions.
1. AI suggestions.
When AI output conflicts with a higher-level source of truth, the higher-level source controls.

## 11. Project Context Rules

- Provide only the context needed for the task.
- Identify the target module/file and its interfaces.
- State constraints before asking for implementation.
- Include relevant acceptance criteria.
- Identify whether the task affects API, database, model, security, privacy, or performance contracts.
- Do not ask AI to infer missing requirements when a clarification or approved decision is required.
## 12. Prompt Construction Rules

| Prompt Element | Required Content |
| --- | --- |
| Role | State the engineering role/task. |
| Context | Relevant files, interfaces, architecture. |
| Goal | One clearly defined outcome. |
| Constraints | Technology, security, privacy, performance constraints. |
| Acceptance criteria | Testable expected behavior. |
| Non-goals | What must not change. |
| Output | Requested code/diff/tests/documentation. |
| Verification | Tests or checks to perform. |

## 13. Prompt Template

Use the following structure for significant AI coding tasks:

| Section | Template |
| --- | --- |
| Task | Implement [specific change]. |
| Context | Relevant module: [path]; contract: [document/ID]. |
| Goal | Achieve [observable behavior]. |
| Constraints | Do not change [architecture/API/schema/etc.]. |
| Acceptance | Given [condition], when [action], then [result]. |
| Tests | Add/update [test cases]. |
| Output | Return implementation + tests + changed files + assumptions. |
| Verification | Run or describe only checks that were actually executed. |

## 14. Context Packaging

- Prefer focused file excerpts over entire repositories.
- Provide interface definitions before implementation details.
- Include relevant tests.
- Include error logs without secrets.
- Mask credentials, tokens, personal information, and unnecessary raw camera data.
- State current versions of important contracts when they matter.
## 15. Requirements Traceability

Every material AI-generated change should have at least one traceable reference when practical.

| Change | Traceability |
| --- | --- |
| Feature | FR/US/UC/issue ID |
| Bug fix | Defect/issue ID + affected test |
| Model change | Experiment ID + model version |
| Feature change | Feature version + experiment/evaluation |
| API change | API contract section + tests |
| DB change | Schema/migration ID |
| Security change | Security requirement/risk ID |
| Performance change | Benchmark record |

## 16. Architecture Protection

- AI must preserve approved component boundaries unless the task explicitly authorizes architectural change.
- Do not duplicate services when an existing service is appropriate.
- Do not move business logic into UI components merely for convenience.
- Do not bypass the model registry for production inference.
- Do not bypass API/service/repository layers without documented justification.
- Architecture changes require explicit human approval.
## 17. Code Generation Rules

1. Inspect existing conventions before generating code.
1. Generate the smallest reasonable implementation.
1. Prefer existing utilities and services.
1. Add types and validation.
1. Handle expected errors.
1. Add or update tests.
1. Explain assumptions and unresolved issues.
1. Do not generate unrelated refactors.
## 18. Code Modification Rules

- Preserve unrelated behavior.
- Show the intended scope of the change.
- Prefer a patch/diff over rewriting whole files.
- Do not delete working tests without a documented reason.
- Preserve public contracts unless the task explicitly changes them.
- Review generated imports and dependencies.
- Check for unintended formatting or generated-file changes.
## 19. Code Review Rules

| Review | Reviewer Must Check |
| --- | --- |
| Behavior | Does implementation meet acceptance criteria? |
| Architecture | Are module boundaries preserved? |
| Security | Any injection, auth, secret, dependency, or unsafe behavior? |
| Privacy | Any unnecessary collection/storage/logging? |
| Testing | Are relevant cases covered? |
| Performance | Could hot paths or real-time processing regress? |
| Maintainability | Can the team understand and maintain it? |
| Traceability | Is the change linked to the right requirement/task? |

## 20. Testing Rules for AI-Generated Code

- Every new non-trivial behavior requires relevant tests.
- Test normal, boundary, invalid, and failure conditions.
- Run existing regression tests after behavior changes.
- API changes require contract tests.
- Database changes require migration/integration tests.
- Model changes require evaluation and regression checks.
- Real-time changes require performance checks when applicable.
- Never weaken a test simply because AI-generated code fails it; determine whether the code or test is wrong.
## 21. Debugging Rules

1. Reproduce the issue before changing code where possible.
1. Provide the smallest useful error/context to the AI.
1. Ask for hypotheses, not an assumed root cause.
1. Test each proposed fix.
1. Prefer root-cause fixes over symptom suppression.
1. Add a regression test for confirmed bugs.
1. Document unresolved uncertainty.
## 22. Refactoring Rules

- Refactoring must preserve externally observable behavior unless explicitly stated otherwise.
- Run regression tests before and after significant refactors.
- Do not combine large refactors with unrelated feature work.
- Measure performance if the refactor touches real-time or data-intensive code.
- Keep public interfaces stable unless contract changes are approved.
## 23. Dependency Rules

- AI may suggest dependencies but must not silently add them.
- Every new dependency requires justification.
- Check license/security/maintenance considerations.
- Use compatible versions.
- Update lock files intentionally.
- Remove unused dependencies introduced during experimentation.
## 24. Security Rules

- Treat AI-generated security code as untrusted until reviewed.
- Use approved authentication/authorization mechanisms.
- Validate all external input.
- Use parameterized database access.
- Use safe serialization/deserialization.
- Apply secure defaults.
- Do not suppress security warnings without documented review.
- Run security checks for material security-sensitive changes.
## 25. Privacy and Sensitive Data Rules

| Data | AI Tool Rule |
| --- | --- |
| Raw camera/video | Do not upload unless explicitly authorized. |
| Landmark sequences | Treat as potentially sensitive; minimize and authorize. |
| User identifiers | Minimize; anonymize where practical. |
| Credentials/tokens | Never provide. |
| Private source code | Use only approved enterprise/project tooling where permitted. |
| Production logs | Sanitize before sharing. |
| Dataset samples | Use approved subsets or synthetic examples when possible. |

## 26. Secret Management

- Secrets belong in approved environment/secret-management systems.
- Never put secrets in prompts, source files, commits, issue comments, screenshots, or logs.
- Use placeholders such as [SECRET] when discussing configuration with AI.
- Rotate a secret immediately if accidental exposure occurs.
- Use secret-scanning tools in CI where available.
## 27. API Coding Rules

- Generate from the approved API Contract.
- Preserve request/response schemas.
- Validate payloads.
- Use documented HTTP status codes.
- Keep controller logic thin.
- Update API tests and frontend clients when contracts change.
- Never invent undocumented fields or endpoints and treat them as approved.
## 28. Database Coding Rules

- Use existing repositories/ORM patterns.
- Never concatenate untrusted SQL.
- Create migrations for schema changes.
- Check indexes and query performance.
- Do not introduce raw camera storage without approval.
- Preserve retention and deletion policies.
- Test migration upgrade paths.
## 29. Frontend Coding Rules

- Use existing component/design patterns.
- Keep camera lifecycle management explicit.
- Represent Ready/Tracking/Recognized/Uncertain/No Sign/Tracking Lost/Error states.
- Do not store secrets in frontend bundles.
- Keep API calls in dedicated clients/services.
- Ensure accessible labels and keyboard behavior.
- Prevent unnecessary re-renders in real-time views.
## 30. Computer Vision Coding Rules

- Keep frame processing bounded and efficient.
- Validate frame dimensions and formats.
- Release camera resources correctly.
- Do not introduce unnecessary frame copies.
- Keep MediaPipe processing behind stable interfaces.
- Define behavior for missing/low-confidence landmarks.
- Do not persist frames by default.
## 31. AI/ML Coding Rules

| Area | Rule |
| --- | --- |
| Model | Use approved architecture/configuration unless an experiment authorizes change. |
| Features | Version feature definitions. |
| Dataset | Use approved dataset version/split. |
| Training | Record experiment configuration. |
| Evaluation | Compare against agreed metrics/baseline. |
| Inference | Verify model-feature compatibility. |
| Artifacts | Version/checksum important artifacts. |
| Promotion | Require documented validation before deployment. |

## 32. Dataset and Training Rules

- Never train on validation/test data.
- Preserve signer-aware split rules.
- Record dataset version and preprocessing version.
- Do not silently relabel classes.
- Document class mapping changes.
- Keep augmentation configuration explicit.
- Record random seeds where reproducibility is required.
- Keep failed experiments in the experiment log when they inform decisions.
## 33. Model Inference Rules

- Load models through the approved model registry/runtime path.
- Record model version in predictions where applicable.
- Validate tensor shape, dtype, and feature version.
- Use confidence/uncertainty rules defined by the model specification.
- Do not silently substitute an incompatible model.
- Keep inference hot paths efficient.
- Handle model loading and runtime failures safely.
## 34. Performance Rules

- Measure before optimization.
- Use the Performance Benchmark specification.
- Do not optimize by reducing required accuracy without review.
- Profile frame processing, landmark extraction, feature generation, inference, API, and UI separately where possible.
- Track p50/p95/p99 latency for APIs.
- Check real-time FPS and end-to-end latency after relevant changes.
- Record benchmark environment.
## 35. Error Handling Rules

- Do not swallow exceptions silently.
- Use controlled error types.
- Return user-safe messages.
- Log diagnostic context without sensitive data.
- Distinguish validation, tracking, model, network, database, and internal failures.
- Define recovery behavior for camera and stream failures.
- Do not use broad exception handling to hide defects.
## 36. Documentation Rules

- AI-generated documentation must be reviewed for factual correctness.
- Update affected contracts after code changes.
- Document new configuration values.
- Document model/data version dependencies.
- Use project terminology consistently.
- Do not claim capabilities that are not implemented.
## 37. Git and Commit Rules

- Do not commit AI conversation transcripts containing sensitive information.
- Use focused commits.
- Use the project's commit convention.
- Reference requirement/task/experiment IDs where appropriate.
- Review the complete diff before commit.
- Check for accidental generated files, secrets, or debug artifacts.
## 38. Pull Request Rules

| PR Requirement | Rule |
| --- | --- |
| Summary | State behavior and reason. |
| Scope | List files/modules affected. |
| Tests | List tests actually run. |
| Benchmarks | Include measured results only when actually run. |
| Risks | Identify security/privacy/performance risks. |
| Contracts | Call out API/DB/model changes. |
| AI assistance | Disclose material AI-generated changes where project policy requires. |
| Review | Obtain required human approval. |

## 39. AI Code Review Checklist

☐ I understand the generated code.

☐ The code matches the approved requirement.

☐ Architecture boundaries are preserved.

☐ No secrets or sensitive data are present.

☐ Inputs are validated.

☐ Errors are handled.

☐ Tests cover changed behavior.

☐ API/database/model contracts remain consistent.

☐ Security/privacy impact is acceptable.

☐ Performance impact is understood.

☐ Dependencies are intentional.

☐ Documentation/traceability is updated.

☐ The diff contains no unrelated changes.

## 40. Hallucination Prevention

- Ask AI to state assumptions explicitly.
- Do not accept invented library APIs or configuration fields without verification.
- Verify framework/library behavior against approved documentation when uncertain.
- Compile/type-check generated code.
- Run tests rather than relying on AI's predicted outcome.
- Treat citations, benchmark claims, and version claims from AI as unverified until checked.
## 41. Verification Before Claiming Success

| Claim | Minimum Evidence |
| --- | --- |
| Build succeeds | Actual build execution and successful output |
| Tests pass | Actual test run |
| Performance improved | Actual benchmark comparison |
| Bug fixed | Reproduction + regression test |
| API works | Actual endpoint/contract test |
| Migration works | Actual migration test |
| Model improved | Controlled evaluation with recorded metrics |
| Deployment succeeded | Actual deployment/health verification |

If execution did not occur, describe the action as proposed or unverified rather than successful.

## 42. Change Size and Scope Control

- Prefer one logical change per AI task.
- Break large work into independently testable increments.
- Do not request an AI tool to rewrite the entire repository for ordinary feature work.
- Large architecture changes require an approved design before implementation.
- Keep generated diffs reviewable.
## 43. Tool and Command Execution Rules

1. Use approved development environments and tools.
1. Review commands before execution when they can modify/delete data.
1. Do not run destructive commands without explicit authorization.
1. Use isolated environments for experiments.
1. Do not expose credentials through command-line history.
1. Capture relevant command results for reproducibility.
1. Never claim a command was run if it was not.
## 44. CI/CD and Release Rules

- AI-generated code must pass the same CI gates as all other code.
- Protected branches require required reviews.
- Release artifacts must identify source/model versions where relevant.
- Production deployment remains a human-approved operation.
- Rollback procedures must remain available.
- Do not allow AI-generated code to bypass quality gates.
## 45. Incident and Rollback Rules

- If AI-generated code causes a defect, follow the normal incident process.
- Stop or roll back unsafe releases when required.
- Preserve diagnostic evidence without exposing sensitive data.
- Add a regression test after root cause is identified.
- Review whether the AI prompt/context/process contributed to the defect.
- Update coding rules if a recurring failure mode is discovered.
## 46. AI Coding Quality Metrics

| Metric | Initial Target / Measure |
| --- | --- |
| AI-generated code acceptance | Track accepted vs rejected changes |
| Defect escape rate | Track defects attributable to generated changes |
| Review rework | Track substantial changes after review |
| Test coverage | ≥80% target for core automated code |
| Security findings | No unresolved critical findings |
| Traceability | Material changes linked to requirement/task |
| Regression rate | Track regressions after AI-assisted changes |
| Cycle time | Track as a productivity metric, not a quality substitute |

## 47. Editable AI Coding Parameters

| Parameter | Value |
| --- | --- |
| Approved AI Coding Tool | [Enter] |
| Approved AI Model | [Enter] |
| Enterprise/Private Mode | [Enabled / Disabled / N/A] |
| Human Review Required | [Yes] |
| Required PR Approvals | [Enter] |
| Core Test Coverage Target | [>=80%] |
| Security Scan | [Enter] |
| Dependency Scan | [Enter] |
| Secret Scan | [Enter] |
| Maximum Preferred AI Change Size | [Enter] |
| AI Change Traceability Required | [Yes / No] |
| Model Experiment ID Required | [Yes for model changes] |
| Production AI Deployment Authority | [Enter role] |
| Sensitive Data Sharing Policy | [Enter] |

## 48. AI Coding Workflow

1. Select approved requirement/task.
1. Identify affected modules and contracts.
1. Prepare sanitized context.
1. Construct a constrained prompt.
1. Generate or modify code.
1. Inspect the complete diff.
1. Run formatting/lint/type checks.
1. Run relevant tests.
1. Run security/privacy checks.
1. Run performance/model evaluation where applicable.
1. Update documentation and traceability.
1. Submit for human review.
1. Merge only after approval.
1. Record experiment/model information for AI/ML changes.
## 49. Definition of Done

☐ Requirement is implemented.

☐ AI-generated code is understood by the responsible developer.

☐ Coding standards pass.

☐ Tests pass.

☐ Security/privacy review is complete where applicable.

☐ API/database/model contracts are synchronized.

☐ Performance impact is checked where relevant.

☐ Documentation and traceability are updated.

☐ Human review is complete.

☐ No secrets or unauthorized sensitive data are included.

☐ Release/merge gates are satisfied.

## 50. AI Coding Checklist

☐ Approved task identified

☐ Source-of-truth documents checked

☐ Context sanitized

☐ Prompt includes constraints and acceptance criteria

☐ AI output inspected

☐ No invented APIs/dependencies accepted without verification

☐ Code formatted/linted

☐ Types checked

☐ Tests added/updated

☐ Security checks completed

☐ Privacy implications reviewed

☐ Performance/model impact evaluated where required

☐ Traceability recorded

☐ Human review completed

☐ Final diff is focused and clean

## 51. Assumptions and Open Questions

- Exact approved AI coding tools are configurable.
- Organization-specific policies may impose stricter rules.
- Enterprise/private AI tooling may be required for confidential source code.
- AI-assisted development does not change project accountability.
- Open question: Which AI coding tools are approved for production source code?
- Open question: Is disclosure of AI assistance mandatory in pull requests?
- Open question: What data classification policy governs source-code sharing with external AI tools?
- Open question: What automated CI gates are mandatory before merge?
## 52. Related Documents

| Document | Relationship |
| --- | --- |
| 10 Technology Stack | Technology baseline |
| 11 Testing & Evaluation | Testing and acceptance |
| 13 Security, Privacy & Ethics | Security/privacy constraints |
| 14 Vibe Coding Master Specification | AI-assisted development governance |
| 26 Coding Standards | General coding standards |
| 03 System Architecture | Architecture boundaries |
| 07 API Contract | API implementation contract |
| 08 Database Schema | Database implementation contract |
| 23 Model Training Specification | Training implementation |
| 24 Model Versioning & Experiment Log | Experiment/model traceability |
| 25 Performance Benchmark | Performance validation |
| 20 Requirements Traceability Matrix | Requirement traceability |

## 53. Version History and Approval

| Version | Date | Author | Change Summary | Status |
| --- | --- | --- | --- | --- |
| 0.1 | [Enter date] | [Enter name] | Initial AI coding rules | Draft |
| 1.0 | [Enter date] | [Enter name] | Baseline approved AI coding rules | [Draft / Review / Approved] |

| Approval Role | Name | Signature | Date |
| --- | --- | --- | --- |
| Prepared By | [Enter name] | [Signature] | [Date] |
| Reviewed By | [Enter name] | [Signature] | [Date] |
| Approved By | [Enter name] | [Signature] | [Date] |
