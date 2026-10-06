<!-- Source: 14_Vibe_Coding_Master_Specification_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# SIGNBRIDGE AI

## 14 — VIBE CODING MASTER SPECIFICATION

AI-Assisted Software Development Standard

| Field | Value |
| --- | --- |
| Document ID | SB-14-VCM |
| Version | 1.0 |
| Status | Draft / Review |
| Project | SignBridge AI |
| Document Type | Vibe Coding / AI-Assisted Development Specification |
| Prepared By | [Enter name / team] |
| Reviewed By | [Enter reviewer] |
| Approved By | [Enter approver] |
| Date | [Enter date] |

Purpose: Establish the standard method for using AI coding assistants and agentic development workflows to build SignBridge AI while preserving architectural consistency, code quality, security, testability, traceability, and human review.

## 1. Document Purpose

This specification defines how AI-assisted coding may be used across the SignBridge AI lifecycle. AI-generated code is proposed implementation and must satisfy the same engineering standards as human-written code.

## 2. Definition of Vibe Coding

For this project, vibe coding means using natural-language instructions, AI coding assistants, code agents, generated scaffolding, refactoring suggestions, test generation, debugging assistance, and documentation generation as part of the software-development workflow.

- AI may accelerate implementation, exploration, refactoring, testing, and documentation.
- AI output is not automatically correct, secure, or production-ready.
- Human developers remain responsible for architecture, requirements, review, testing, and release decisions.
- Every AI-generated change must be traceable to a requirement, issue, task, or documented engineering decision.
## 3. Objectives

- Reduce repetitive coding and boilerplate effort.
- Maintain architectural consistency across frontend, backend, AI/CV, database, and deployment layers.
- Generate tests alongside implementation.
- Accelerate debugging and documentation while retaining human verification.
- Prevent uncontrolled AI-generated code from introducing security, privacy, performance, or maintainability problems.
## 4. Governing Principles

| Principle | Rule |
| --- | --- |
| Requirements first | AI receives the approved requirement before implementation. |
| Small changes | Prefer focused, reviewable changes over broad rewrites. |
| Human ownership | A developer reviews and owns every merged AI-generated change. |
| Tests with code | New behavior must include or update appropriate tests. |
| No silent architecture changes | AI must not change approved architecture without explicit approval. |
| Secure by default | Generated code follows project security and privacy requirements. |
| Evidence over assumption | Claims about APIs, libraries, or behavior must be verified. |
| Traceability | Changes link to a requirement, issue, task, or decision. |

## 5. AI-Assisted Development Scope

| Area | Allowed AI Assistance | Human Responsibility |
| --- | --- | --- |
| Frontend | Components, styling, state logic, tests, refactoring. | UX, accessibility, final review. |
| Backend | Routes, schemas, services, validation, tests. | API design, security, business rules. |
| AI/CV | Feature code, preprocessing utilities, evaluation scripts. | Model architecture and scientific validity. |
| Database | Schema drafts, queries, migrations, tests. | Data model approval and migration safety. |
| Deployment | Dockerfiles, CI/CD templates, manifests. | Secrets, infrastructure, production approval. |
| Documentation | Draft specifications, comments, READMEs. | Accuracy and final approval. |

## 6. Non-Autonomous Decisions

- AI must not independently change project scope or production architecture.
- AI must not introduce authentication, analytics, data collection, or external services without approval.
- AI must not deploy production changes without release authorization.
- AI must not remove tests to make a build pass.
- AI must not disable security controls as a debugging shortcut.
- AI must not fabricate test results, model metrics, citations, API behavior, or deployment status.
## 7. Approved Project Context

| Artifact | Authoritative Source |
| --- | --- |
| Requirements | 01_Project_PRD / 02_SRS |
| Architecture | 03_System_Architecture |
| Dataset | 04_Dataset_Specification |
| AI model | 05_AI_Model_Specification |
| Preprocessing | 06_Preprocessing_Feature_Engineering |
| API | 07_API_Contract |
| Database | 08_Database_Schema |
| UI/UX | 09_UI_UX_Specification |
| Technology | 10_Technology_Stack |
| Testing | 11_Testing_Evaluation |
| Deployment | 12_Deployment |
| Security/Privacy/Ethics | 13_Security_Privacy_Ethics |

## 8. Source-of-Truth Hierarchy

1. Approved project requirements and signed-off specifications.
1. Approved architecture and API/database contracts.
1. Approved issue/task or change request.
1. Existing production behavior when explicitly documented as authoritative.
1. Team coding conventions and repository standards.
1. AI-generated suggestions, which are proposals rather than authoritative requirements.
## 9. Recommended Repository Structure

| Path | Purpose |
| --- | --- |
| frontend/ | React/Next.js client application |
| backend/ | FastAPI/API application |
| ai/ | Model, inference, evaluation, ML utilities |
| preprocessing/ | Landmark and feature engineering |
| database/ | Schema, migrations, seed/reference data |
| tests/ | Unit, integration, API, E2E and evaluation tests |
| docs/ | Project specifications and developer documentation |
| scripts/ | Development, evaluation, migration and deployment utilities |
| deploy/ | Docker, CI/CD and infrastructure manifests |
| configs/ | Non-secret configuration templates |

## 10. AI Coding Workflow

1. Read the relevant specification and identify the exact requirement.
1. Create/update the development task with acceptance criteria.
1. Provide the AI assistant with repository context and explicit constraints.
1. Ask for an implementation plan before broad changes.
1. Implement the smallest useful change.
1. Generate/update tests.
1. Run formatting, linting, type checks, and tests.
1. Review the complete diff for correctness, security, and unintended changes.
1. Update documentation/contracts when behavior changes.
1. Commit the reviewed change with traceable metadata.
## 11. Standard Prompt Structure

| Prompt Element | Required Content |
| --- | --- |
| Role | Role such as senior Python/FastAPI engineer. |
| Goal | One concrete outcome. |
| Context | Relevant SignBridge AI module/specification. |
| Constraints | Architecture, libraries, performance, security, compatibility. |
| Inputs | Existing files, interfaces, schemas, sample data. |
| Expected Output | Files/code/tests/documentation expected. |
| Acceptance Criteria | Measurable conditions. |
| Validation | Tests, edge cases, assumptions. |
| Change Limits | What must not be modified. |

## 12. Master Coding Prompt Template

You are working on SignBridge AI, an Indian Sign Language recognition system.

Task:
[Describe one specific implementation task.]

Authoritative specification:
[Document and section]

Existing context:
[Relevant files, interfaces, data structures, APIs]

Constraints:
[Approved technologies, architecture, security and performance rules]

Requirements:
1. [Requirement]
2. [Requirement]
3. [Requirement]

Do not:
- Change unrelated files.
- Change approved architecture without asking.
- Add unapproved dependencies.
- Remove or weaken security controls.
- Claim tests passed unless they were actually run.

Acceptance criteria:
[Measurable criteria]

Before finalizing:
- Review the diff for unintended changes.
- Add/update tests.
- Report exactly which tests were run and their results.
- Identify assumptions and remaining risks.

## 13. Context Packaging for AI Agents

- Provide only the files/specifications needed for the task where practical.
- Include interfaces, schemas, types, tests, and existing error-handling conventions.
- Avoid sending secrets, credentials, private keys, production tokens, or unnecessary personal data to coding assistants.
- When repository context is large, provide a concise architecture summary and targeted file references.
## 14. Coding Standards

- Follow approved language/framework conventions.
- Prefer readable, maintainable code over compressed or clever code.
- Use descriptive names and small functions.
- Validate external input at system boundaries.
- Handle errors explicitly and consistently.
- Avoid duplicated business logic.
- Keep configuration separate from implementation.
- Use type hints where supported.
- Comment decisions and non-obvious constraints rather than obvious syntax.
## 15. Frontend AI Coding Rules

- Follow the UI/UX specification and design tokens.
- Keep reusable components modular.
- Implement loading, error, empty, uncertain, no-sign, and tracking-lost states.
- Never embed backend secrets in client source.
- Validate API responses.
- Preserve keyboard accessibility and responsive behavior.
- Add tests for critical recognition flows.
## 16. Backend AI Coding Rules

- Follow the API Contract unless a versioned change is approved.
- Validate all API inputs.
- Keep route handlers thin and business logic in services.
- Use structured errors and approved status codes.
- Never expose stack traces or sensitive internal details.
- Apply authentication, authorization, rate limits and request limits where required.
- Add tests for valid, invalid, boundary and failure scenarios.
## 17. AI/ML Coding Rules

- Do not change model architecture/training objectives without documenting the change.
- Keep train/validation/test data separated.
- Prevent data leakage in preprocessing and scaling.
- Version model artifacts and evaluation configurations.
- Never report generated/synthetic metrics as actual experiment results.
- Keep training preprocessing and inference preprocessing consistent.
- Provide reproducible evaluation scripts for important results.
## 18. Computer Vision Coding Rules

- Validate frame input before processing.
- Handle missing landmarks and tracking loss gracefully.
- Keep preprocessing deterministic where reproducibility is required.
- Avoid hard-coded image dimensions when configuration exists.
- Prevent unbounded memory growth in real-time loops.
- Measure latency when modifying the inference path.
## 19. Database Coding Rules

- Use migrations for schema changes.
- Never silently alter production schema at application startup.
- Use parameterized queries/ORM patterns.
- Preserve foreign-key and uniqueness constraints.
- Justify new indexes by query patterns.
- Test migration upgrades and recovery procedures.
## 20. API Contract Change Rules

| Change | Required Action |
| --- | --- |
| Add optional field | Update schema, tests and docs; verify compatibility. |
| Add required field | Assess compatibility and change process. |
| Rename/remove field | Use approved breaking-change procedure. |
| Add endpoint | Document request/response/errors and tests. |
| Change response meaning | Update contract and affected clients. |
| Change authentication | Security review required. |
| Change WebSocket message | Update client/server contract and compatibility tests. |

## 21. Test-First AI Development

- For bugs, reproduce with a test when practical before fixing.
- For new behavior, define acceptance criteria and tests alongside implementation.
- Ask AI to identify edge cases before generating implementation code.
- Run targeted tests first, then the regression suite.
- Never delete failing tests to conceal regressions.
- Record test commands and meaningful results.
## 22. Required Validation Gates

| Gate | Check | Pass Condition |
| --- | --- | --- |
| Syntax/Build | Compile/import/build | No blocking errors |
| Formatting | Formatter | Rules satisfied |
| Lint | Static analysis | No critical findings |
| Types | Type checking | No blocking errors |
| Unit | Affected tests | Pass |
| Integration | Service integration tests | Pass |
| Security | Relevant security checks | No unresolved critical issue |
| Regression | Critical suite | Pass |
| Review | Human diff review | Approved |

## 23. AI Code Review Prompt

Review this SignBridge AI change as a senior software engineer.

Check:
1. Correctness against the referenced requirement.
2. API/database compatibility.
3. Error handling and edge cases.
4. Security and privacy implications.
5. Performance and real-time behavior.
6. Test coverage and missing cases.
7. Maintainability and duplication.
8. Unintended changes outside scope.

Return:
- Blocking issues
- Important issues
- Minor issues
- Missing tests
- Documentation updates
- Evidence-based review recommendation.

## 24. Prompt Patterns by Task

| Task | Recommended Pattern |
| --- | --- |
| New feature | Plan → implement → test → review; modify only required files. |
| Bug fix | Reproduce → root cause → minimal fix → regression test. |
| Refactor | Preserve behavior; show risk; run regression tests. |
| API endpoint | Follow contract; add validation, tests and docs. |
| ML experiment | Define hypothesis, split, metrics, config and reproducibility. |
| Performance | Profile first; optimize measured bottleneck; compare before/after. |
| Security fix | Explain threat, mitigation and regression test. |
| Documentation | Use authoritative specs; label assumptions explicitly. |

## 25. Change Size Policy

| Size | Typical Scope | Review |
| --- | --- | --- |
| Small | One module, small bug, isolated UI change. | Developer + automated tests. |
| Medium | Multiple modules or API behavior. | Developer + reviewer + integration tests. |
| Large | Architecture, model, database, deployment, security. | Design review + testing + explicit approval. |
| Critical | Authentication, privacy, production model, data migration, infrastructure. | Specialist review + release approval. |

## 26. Dependency Management

- Do not add a library merely for convenience if approved libraries can solve the task.
- New dependencies require reason and compatibility/security review.
- Pin/constrain versions according to the technology policy.
- Review license, maintenance, vulnerability status and provenance where appropriate.
- Remove unused dependencies introduced during experiments.
## 27. Security Rules for AI Coding Tools

- Never provide passwords, private keys, production tokens, database credentials, or secrets to an AI coding assistant.
- Do not paste unnecessary personal/sensitive user data into prompts.
- Review generated code for injection, auth, file-handling and data-exposure risks.
- Treat generated shell commands and scripts as untrusted until reviewed.
- Do not execute destructive commands generated by AI without explicit verification.
- Use project-approved AI tools and organizational privacy settings.
## 28. Safe Command Execution

| Command | Policy |
| --- | --- |
| Read-only inspection | AI may suggest; normal review. |
| Build/test/format | Allowed after reviewing scope. |
| Dependency install | Human review required. |
| Database migration | Human approval; production requires explicit authorization. |
| Deployment/rollback | Explicit release authorization. |
| Destructive delete/reset/drop | Never autonomous; explicit confirmation. |

## 29. Git & Branching Strategy

- Use feature branches for isolated work.
- Keep commits focused and traceable.
- Reference issue/task/requirement in commit or PR metadata.
- Do not mix unrelated AI-generated changes.
- Review the complete diff before merge.
- Protect main/release branches.
## 30. Commit Message Standard

<type>(<scope>): <short description>

- feat — feature
- fix — bug fix
- refactor — behavior-preserving restructuring
- test — tests only
- docs — documentation
- perf — performance improvement
- security — security change
- chore — tooling/dependency/maintenance
## 31. Pull Request / Review Template

Title: [Short change description]
Requirement / Task: [Reference]
What changed: [Summary]
AI assistance used: [Tool / purpose]
Files changed: [List]
Tests run: [Commands + results]
Security/privacy impact: [None / describe]
API/database/model impact: [None / describe]
Performance impact: [None / measurements]
Known limitations: [List]
Reviewer notes: [Reviewer completes]

## 32. AI-Generated Documentation Rules

- Verify factual statements against implementation or authoritative specifications.
- Never fabricate references, benchmarks, deployment results, certifications or user studies.
- Keep code comments synchronized with behavior.
- Update API, database, architecture and deployment documentation when needed.
- Clearly label assumptions and placeholders.
## 33. AI-Assisted Debugging Workflow

1. Capture exact error, environment, input and reproduction steps.
1. Ask AI for multiple plausible causes.
1. Inspect logs, stack traces, tests and source.
1. Select the smallest evidence-supported fix.
1. Add a regression test where practical.
1. Run targeted and broader tests.
1. Document root cause and resolution for significant issues.
## 34. AI-Assisted Model Development Workflow

1. Define experiment hypothesis.
1. Freeze and identify dataset version.
1. Define train/validation/test split.
1. Specify preprocessing/features.
1. Define architecture/hyperparameters.
1. Generate training/evaluation code.
1. Run experiment and store actual results.
1. Compare against baseline.
1. Review class-level and signer-independent performance.
1. Approve model before deployment.
## 35. Performance Optimization Workflow

- Measure before optimizing.
- Identify the actual bottleneck using profiling/metrics.
- Ask AI for candidate optimizations and tradeoffs.
- Implement one focused optimization at a time.
- Compare latency, FPS, memory, accuracy and resources before/after.
- Reject speedups that violate accuracy, privacy or maintainability.
## 36. Documentation & Traceability Matrix

| Artifact | Must Reference |
| --- | --- |
| Source code change | Requirement/task/issue |
| AI prompt | Task/development context where retained |
| Test case | Requirement/behavior |
| Model experiment | Dataset + configuration + hypothesis |
| Model artifact | Training/evaluation version |
| API change | API contract version/change |
| Database migration | Schema version/change |
| Deployment | Release + model version |
| Security change | Threat/risk + mitigation |

## 37. Vibe Coding Quality Metrics

| Metric | Target / Guideline | Actual |
| --- | --- | --- |
| Critical test pass rate | 100% before release | [Enter] |
| Core test coverage | ≥80% target; confirm final | [Enter] |
| Unreviewed AI-generated production changes | 0 | [Enter] |
| Critical security findings | 0 unresolved at release | [Enter] |
| Traceable production changes | 100% target | [Enter] |
| Documentation drift | No known critical drift | [Enter] |

## 38. AI Coding Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Hallucinated API/library behavior | Implementation failure | Verify docs/source and run tests. |
| Broad code changes | Regression | Small tasks, scoped prompts, diff review. |
| Security vulnerability | System/data compromise | Security review and scanning. |
| Data leakage | Privacy impact | Minimize prompt data; prohibit secrets. |
| Architecture drift | Maintenance cost | Source-of-truth hierarchy and approval gates. |
| Test manipulation | False confidence | Meaningful tests + human review. |
| Dependency sprawl | Maintenance/security burden | Dependency approval. |
| Over-automation | Uncontrolled changes | Human approval for sensitive actions. |

## 39. Definition of Done for AI-Assisted Coding

- ☐ Requirement/task identified.
- ☐ Relevant specifications consulted.
- ☐ AI implementation scoped to task.
- ☐ Coding conventions followed.
- ☐ Tests added/updated.
- ☐ Formatting/lint/type checks passed where applicable.
- ☐ Security/privacy reviewed.
- ☐ API/database/model docs updated if needed.
- ☐ Complete diff reviewed by a human.
- ☐ Actual test results recorded.
- ☐ Traceable commit created.
- ☐ Deployment uses approved release process.
## 40. Editable Vibe Coding Parameters

| Parameter | Current Proposal | Final Value |
| --- | --- | --- |
| Primary AI coding tool | [Define] | [Confirm] |
| AI review tool | [Define] | [Confirm] |
| Repository platform | GitHub / GitLab / [Other] | [Confirm] |
| Branching strategy | Feature branch + protected main | [Confirm] |
| Required code review | Human review required | [Confirm] |
| Core test coverage target | ≥80% | [Confirm] |
| Critical security findings | 0 unresolved | [Confirm] |
| AI prompt retention | [Define policy] | [Confirm] |
| Secret handling | Never provide secrets to AI | [Confirm] |
| Production deployment authority | Authorized project owner | [Confirm] |
| AI autonomy | Assist/propose; human approval for sensitive actions | [Confirm] |

## 41. Master AI Agent Operating Prompt

You are an AI software-engineering assistant working on SignBridge AI, an Indian Sign Language recognition system.

Rules:
1. Treat project specifications as the source of truth.
2. Implement only the requested task.
3. Do not invent requirements or external facts.
4. Do not change architecture without explicit approval.
5. Do not add dependencies without justification.
6. Never expose or hard-code secrets.
7. Do not use unnecessary personal/sensitive data.
8. Make small, reviewable changes.
9. Include/update tests.
10. Preserve compatibility unless a breaking change is explicitly requested.
11. Never claim a test, build, deployment, benchmark or experiment succeeded unless actually executed.
12. Identify assumptions and unresolved questions.
13. Before completion, summarize files changed, tests run, risks and remaining work.

Response structure:
- Understanding
- Plan
- Changes
- Tests
- Risks / assumptions
- Files changed
- Follow-up items

## 42. Dependencies

- 01_Project_PRD — product goals and scope.
- 02_SRS — functional/non-functional requirements.
- 03_System_Architecture — approved architecture.
- 04_Dataset_Specification — dataset rules.
- 05_AI_Model_Specification — model behavior/evaluation.
- 06_Preprocessing_Feature_Engineering — preprocessing.
- 07_API_Contract — interfaces.
- 08_Database_Schema — persistence.
- 09_UI_UX_Specification — UI behavior.
- 10_Technology_Stack — approved technologies.
- 11_Testing_Evaluation — testing and acceptance.
- 12_Deployment — operations.
- 13_Security_Privacy_Ethics — responsible development.
## 43. Final Approval Checklist

- ☐ AI-assisted workflow approved.
- ☐ Source-of-truth hierarchy established.
- ☐ Repository structure approved.
- ☐ Prompt template approved.
- ☐ Coding standards documented.
- ☐ AI-tool security rules reviewed.
- ☐ Test/review gates defined.
- ☐ Git/review process defined.
- ☐ Model-development workflow defined.
- ☐ Deployment authority defined.
- ☐ AI autonomy boundaries defined.
- ☐ Editable parameters finalized.
- ☐ Team trained on workflow.
## 44. Version History

| Version | Date | Author | Change Description | Status |
| --- | --- | --- | --- | --- |
| 1.0 | [Enter date] | [Enter name] | Initial Vibe Coding Master Specification. | Draft |
| 1.1 | [Enter date] | [Enter name] | [Enter changes] | [Review/Approved] |
| 2.0 | [Enter date] | [Enter name] | [Major revision if required] | [Review/Approved] |

## 45. Approval

| Role | Name | Signature | Date |
| --- | --- | --- | --- |
| Project Lead | [Enter] | [Signature] | [Date] |
| Software Lead | [Enter] | [Signature] | [Date] |
| AI/ML Lead | [Enter] | [Signature] | [Date] |
| Security Lead | [Enter] | [Signature] | [Date] |
| QA/Test Lead | [Enter] | [Signature] | [Date] |
| Project Reviewer | [Enter] | [Signature] | [Date] |

> Document control note: AI-assisted coding does not transfer engineering accountability to the AI system. All production changes remain subject to human review, testing, security/privacy controls, and the approved release process.
