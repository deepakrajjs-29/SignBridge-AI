<!-- Source: 37_Results_Analysis_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# SIGNBRIDGE AI

## RESULTS & ANALYSIS

*Structured framework for recording, analyzing, interpreting, and reporting SignBridge AI experimental findings*

| Field | Value |
| --- | --- |
| Document ID | SBAI-RA-001 |
| Document Number | 37 |
| Version | 1.0 |
| Status | Draft / Editable |
| Project | SignBridge AI |
| Related Document | 36 Experimental Design |
| Prepared By | [Enter Name / Team] |
| Reviewed By | [Enter Reviewer] |
| Approved By | [Enter Approver] |
| Analysis Period | [Enter Period] |
| Last Updated | [Enter Date] |

## Table of Contents

1. 1. Purpose
1. 2. Scope
1. 3. Result Reporting Principles
1. 4. Evaluation Configuration
1. 5. Dataset Results
1. 6. Baseline Results
1. 7. Preprocessing Results
1. 8. Feature Engineering Results
1. 9. Model Comparison Results
1. 10. Hyperparameter Results
1. 11. Ablation Results
1. 12. Classification Performance
1. 13. Confusion and Error Analysis
1. 14. Signer-Independent Results
1. 15. Robustness Results
1. 16. Real-Time Performance Results
1. 17. End-to-End System Results
1. 18. Usability and Accessibility Results
1. 19. Statistical Analysis
1. 20. Hypothesis Evaluation
1. 21. Research Question Findings
1. 22. Gap Closure Analysis
1. 23. Discussion
1. 24. Limitations of the Results
1. 25. Key Findings
1. 26. Recommendations
1. 27. Reproducibility Record
1. 28. Traceability
1. 29. Version History
1. 30. Review and Approval
## 1. Purpose

This document provides the controlled structure for recording and interpreting the results generated from SignBridge AI experiments. It is intended to separate measured evidence from interpretation and to ensure that reported conclusions remain traceable to the experimental design, dataset, model, preprocessing pipeline, and evaluation configuration.

No performance value should be treated as an achieved result until it has been measured and recorded from the approved experiment. Placeholder fields in this document are intentionally editable.

## 2. Scope

- Dataset composition and quality results.
- Baseline and candidate model results.
- Preprocessing and feature-engineering comparisons.
- Hyperparameter and ablation results.
- Accuracy, precision, recall, macro F1, and class-wise performance.
- Confusion-matrix and error analysis.
- Signer-independent generalization.
- Environmental and robustness evaluation.
- Real-time latency, FPS, memory, and resource measurements.
- End-to-end application behavior.
- Usability and accessibility observations.
- Statistical analysis, hypothesis decisions, research-gap closure, and recommendations.
## 3. Result Reporting Principles

- Report the exact dataset, model, preprocessing, and experiment versions used.
- Separate measured results from interpretation and proposed explanations.
- Report aggregate and class-wise performance where appropriate.
- Do not compare values produced under materially different evaluation protocols without clearly identifying the difference.
- Report failed, inconclusive, and negative experiments where they inform the research conclusions.
- State hardware and runtime configuration for performance results.
- Do not generalize beyond the tested signer population, sign vocabulary, environments, devices, and evaluation protocol.
- Retain raw experiment evidence and link it to the corresponding experiment ID.
## 4. Evaluation Configuration

| Parameter | Recorded Value |
| --- | --- |
| Dataset Version | [Enter] |
| Dataset Size | [Enter] |
| Number of Classes | [Enter] |
| Number of Signers | [Enter] |
| Train Split | [Enter] |
| Validation Split | [Enter] |
| Test Split | [Enter] |
| Signer-Independent Split | [Enter] |
| Sequence Length | [Enter] |
| Feature Version | [Enter] |
| Preprocessing Version | [Enter] |
| Model Version | [Enter] |
| Framework/Runtime | [Enter] |
| Hardware | [Enter] |
| Operating System | [Enter] |
| Evaluation Date | [Enter] |
| Random Seed | [Enter / N/A] |
| Evaluation Script Version | [Enter] |

## 5. Dataset Results

### 5.1 Dataset Composition

| Measure | Expected / Target | Actual Result | Notes |
| --- | --- | --- | --- |
| Total Samples | [Target] | [Enter] | [Enter] |
| Total Videos/Sequences | [Target] | [Enter] | [Enter] |
| Number of Classes | [Target] | [Enter] | [Enter] |
| Number of Signers | [Target] | [Enter] | [Enter] |
| Average Samples/Class | [Target] | [Enter] | [Enter] |
| Minimum Samples/Class | [Target] | [Enter] | [Enter] |
| Maximum Samples/Class | [Target] | [Enter] | [Enter] |
| Average Sequence Length | [Target] | [Enter] | [Enter] |

### 5.2 Split Distribution

| Split | Samples | Signers | Classes | Percentage |
| --- | --- | --- | --- | --- |
| Training | [Enter] | [Enter] | [Enter] | [Enter] |
| Validation | [Enter] | [Enter] | [Enter] | [Enter] |
| Test | [Enter] | [Enter] | [Enter] | [Enter] |
| Signer-Independent Test | [Enter] | [Enter] | [Enter] | [Enter] |

### 5.3 Dataset Quality Findings

- [Enter observed data-quality finding]
- [Enter class-balance finding]
- [Enter annotation/label-quality finding]
- [Enter duplicate/leakage check finding]
- [Enter signer/environment diversity finding]
## 6. Baseline Results

| Model | Input Representation | Accuracy | Macro F1 | Precision | Recall | Latency | FPS |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 Frame-Level Baseline | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| B2 Simple Temporal Baseline | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| B3 Proposed Model | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |

Analysis: [Explain how the baseline establishes the reference point and what changed with the proposed approach.]

## 7. Preprocessing Results

| Experiment ID | Configuration | Accuracy | Macro F1 | Latency | Robustness | Conclusion |
| --- | --- | --- | --- | --- | --- | --- |
| EXP-PRE-001 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| EXP-PRE-002 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| EXP-PRE-003 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |

Analysis: [Describe the measurable effect of preprocessing choices and identify the selected configuration.]

## 8. Feature Engineering Results

| Experiment | Feature Set | Macro F1 | Dynamic-Class F1 | Latency | Model Size | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| EXP-FEAT-001 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| EXP-FEAT-002 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| EXP-FEAT-003 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |

Analysis: [Identify which features contributed to recognition and whether their cost was justified.]

## 9. Model Comparison Results

| Model | Parameters | Accuracy | Macro F1 | Precision | Recall | Latency (ms) | FPS | Memory | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Model A] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| [Model B] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| [Model C] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| [Selected Model] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |

Analysis: [Compare models under the same evaluation protocol. Explain trade-offs without using unsupported claims.]

## 10. Hyperparameter Results

| Parameter | Configuration | Validation Metric | Test Metric* | Latency | Decision |
| --- | --- | --- | --- | --- | --- |
| Sequence Length | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Learning Rate | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Batch Size | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Hidden Dimension | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Dropout | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |

*Use final test metrics only after configuration selection. Avoid repeatedly tuning against the test set.

## 11. Ablation Results

| Ablation ID | Full Configuration | Removed Component | Metric Change | Latency Change | Interpretation |
| --- | --- | --- | --- | --- | --- |
| ABL-001 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| ABL-002 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| ABL-003 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| ABL-004 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| ABL-005 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |

## 12. Classification Performance

| Metric | Training | Validation | Test | Signer-Independent Test | Target | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Accuracy | [Enter] | [Enter] | [Enter] | [Enter] | ≥ 90%* | [Enter] |
| Macro F1 | [Enter] | [Enter] | [Enter] | [Enter] | ≥ 0.90* | [Enter] |
| Macro Precision | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Macro Recall | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Weighted F1 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |

*Project default target; editable and not an assertion that the target has been achieved.

## 13. Confusion and Error Analysis

The confusion matrix should be inserted or attached here for the final evaluated model.

| Error Pattern | Actual Class | Predicted Class | Frequency | Possible Cause | Evidence | Action |
| --- | --- | --- | --- | --- | --- | --- |
| E-001 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| E-002 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| E-003 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| E-004 | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |

- Analyze visually similar signs separately.
- Check whether errors originate from data quality, landmark tracking, temporal ambiguity, or model capacity.
- Compare errors across signers and environmental conditions.
- Do not infer causal explanations without supporting evidence; label them as hypotheses when unverified.
## 14. Signer-Independent Results

| Measure | Standard Test | Unseen-Signer Test | Difference | Interpretation |
| --- | --- | --- | --- | --- |
| Accuracy | [Enter] | [Enter] | [Enter] | [Enter] |
| Macro F1 | [Enter] | [Enter] | [Enter] | [Enter] |
| Precision | [Enter] | [Enter] | [Enter] | [Enter] |
| Recall | [Enter] | [Enter] | [Enter] | [Enter] |
| Unknown/Low-Confidence Rate | [Enter] | [Enter] | [Enter] | [Enter] |

Analysis: [Describe generalization behavior and any meaningful performance degradation.]

## 15. Robustness Results

| Condition | Baseline Metric | Final Metric | Change | Landmark Failure Rate | Notes |
| --- | --- | --- | --- | --- | --- |
| Low Light | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Backlighting | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Background Clutter | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Partial Occlusion | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Fast Signing | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Camera Distance | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Camera Angle | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |

## 16. Real-Time Performance Results

| Metric | Target | Measured | Test Hardware | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| End-to-End Latency | < 200 ms* | [Enter] | [Enter] | [Enter] | [Enter] |
| Sustained FPS | ≥ 15 FPS* | [Enter] | [Enter] | [Enter] | [Enter] |
| Model Inference Time | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Landmark Processing Time | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Peak Memory | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| CPU/GPU Utilization | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |

*Preferred project targets; editable and subject to the approved Performance Benchmark.

## 17. End-to-End System Results

| Workflow | Expected Behavior | Observed Result | Status | Evidence / Issue ID |
| --- | --- | --- | --- | --- |
| Camera Permission | Permission and recovery guidance | [Enter] | [Pass/Fail] | [Enter] |
| Camera Capture | Stable frame acquisition | [Enter] | [Pass/Fail] | [Enter] |
| Landmark Extraction | Valid landmark sequence | [Enter] | [Pass/Fail] | [Enter] |
| Preprocessing | Correct feature/sequence generation | [Enter] | [Pass/Fail] | [Enter] |
| Inference | Prediction within configured threshold | [Enter] | [Pass/Fail] | [Enter] |
| Low Confidence | Unknown/uncertain state | [Enter] | [Pass/Fail] | [Enter] |
| Backend Failure | Graceful failure state | [Enter] | [Pass/Fail] | [Enter] |
| Model Compatibility | Correct model/pipeline pairing | [Enter] | [Pass/Fail] | [Enter] |
| UI Feedback | Clear prediction/status | [Enter] | [Pass/Fail] | [Enter] |

### 17.1 Preliminary Manual Webcam Observations (15-Sign Session)

**Classification:** Preliminary manual webcam observations — **not** a controlled benchmark and **not** a held-out accuracy measurement.

**Cross-reference:** `Docs/eval/webcam_15_sign_checklist.md` (protocol) and `Docs/eval/webcam_truth.csv` (structured truth sheet — this session recorded as rows `C01`–`C15`, plus extra trial `X01` = Police). This addendum records a single informal live-camera session. Several automatic primary predictions were not captured on screen; some notes describe alternatives/suggestions rather than the primary. Because of missing primaries, ambiguous outcomes, and at least one session with no displayed result, **no aggregate accuracy percentage is computed or claimed for this session**, and it stays strictly separate from the offline benchmark of 81.29%.

Model context: `SBAI-MDL-ISL-4.0.0`, 109 classes; frozen offline TEST argmax accuracy remains **81.29%** (n=3629, `Docs/eval/08_final_test.json`) — unaffected by this informal session.

#### Observation table (original checklist IDs)

| # | Class ID | Expected sign | Automatic primary prediction | Confidence (as displayed) | Alternatives / other notes | Observed outcome | Category |
|--:| --- | --- | --- | --- | --- | --- | --- |
| 1 | ISL_001 | Hello | *not_observed* (not captured) | 8.2% (attached to Hello suggestion) | Suggestions: Go, Child, T, Hello | Primary not captured | Unverified |
| 2 | ISL_002 | Thank You | *not_observed* (not captured) | 11.4% (attached to suggestion) | Thank You appeared as a suggestion | Primary not captured | Unverified |
| 3 | ISL_003 | Please | *unverified* | *unverified* | — | No reliable observation recorded | Unverified |
| 4 | ISL_004 | Market | What | 100% (expected-sign Market: 34%) | — | Automatic primary incorrect | Incorrect prediction |
| 5 | ISL_011 | Help | YOU (automatically selected) | expected-sign Help: 12.4% | — | Automatic primary incorrect | Incorrect prediction |
| 6 | ISL_012 | Water | *not_observed* (not captured) | 9.6% (box reading) | — | Primary not captured | Unverified |
| 7 | ISL_028 | School | *not_observed* (not captured) | 26.7% (box reading) | — | Primary not captured | Unverified |
| 8 | ISL_035 | Go | Walk | 4.7% | — | Automatic primary incorrect (motion-related pair) | Incorrect prediction |
| 9 | ISL_039 | Student | *none reported* | *not_observed* | — | Sign not recognized; no prediction reported | Recognition failure / no output |
| 10 | ISL_045 | Teacher | Baby / Hero (primary not disambiguated) | *not_observed* (Teacher conf not reported) | Baby and Hero displayed | Both displayed predictions differ from expected | Incorrect prediction (primary not disambiguated) |
| 11 | ISL_046 | Sit | Teacher | *not_observed* (Sit conf not reported) | — | Automatic primary incorrect | Incorrect prediction |
| 12 | ISL_049 | Book | *not_observed* (not captured) | 13.5% (box reading) | — | Primary not captured | Unverified |
| 13 | ISL_055 | Stay | *none displayed* | *not_observed* | Tester reports Stay not available in the sign list | Nothing appeared | Recognition failure / no output + sign-list availability |
| 14 | ISL_060 | Walk | *not_observed* (not captured) | 14.7% (box reading) | — | Primary not captured | Unverified |
| 15 | ISL_097 | Big | Family | 23.7% | — | Automatic primary incorrect | Incorrect prediction |
| E1* | ISL_107 | Police* | What | expected-sign Police: 0.2% | — | Automatic primary incorrect at near-zero confidence | Incorrect prediction (extra trial) |

\* Police was an extra trial outside the original 15-sign checklist — preserved as such, never substituted for a checklist row (CSV row `X01`).

#### Result classification (live session only — kept separate from the offline 81.29% TEST score)

1. **Observed results (automatic primary captured on screen):** 6 of 15 checklist rows (#4, #5, #8, #10, #11, #15) + the extra Police trial — **every one mismatched the expected sign**; no exact-match automatic pass was observed.
2. **Low-confidence predictions:** 11 of the 12 observed confidence readings (0.2%, 4.7%, 8.2%, 9.6%, 11.4%, 12.4%, 13.5%, 14.7%, 23.7%, 26.7%, 34%) fall **below the server accept threshold 0.57** — under the current policy these are Provisional/Uncertain and are never auto-committed. The single high-confidence reading (What at 100% on Market) was **wrong**.
3. **Incorrect automatic predictions:** Market→What, Help→YOU, Go→Walk, Teacher→Baby/Hero, Sit→Teacher, Big→Family (6 checklist rows) + Police→What (extra trial).
4. **Missing / unverified information:** 7 checklist rows lack a recorded automatic primary (#1 Hello, #2 Thank You, #3 Please, #6 Water, #7 School, #12 Book, #14 Walk); confidence additionally missing for #10, #11; nothing at all recorded for #3. These are marked `unverified` / `not_observed` and are **excluded from every correctness count** — never counted as correct, never inferred.
5. **Sign-list availability issue:** #13 Stay — tester reported Stay was not available in the sign list and nothing appeared. The dataset `class_map.csv` **does** define `ISL_055,Stay` (so this is a UI/observation-side availability issue, not an absent model class); not independently re-verified live. Student (#9) is a plain recognition failure (no prediction reported).

#### Outcome taxonomy (no aggregate rate)

| Category | Count | Meaning |
| --- | ---: | --- |
| Incorrect automatic prediction (checklist) | 6 | Primary shown (or displayed candidates) ≠ expected: #4 Market, #5 Help, #8 Go, #10 Teacher, #11 Sit, #15 Big |
| Incorrect automatic prediction (extra trial) | 1 | Police (ISL_107) — outside the 15, counted separately |
| Recognition failure / no output | 2 | #9 Student produced no prediction; #13 Stay produced no displayed result |
| Unverified / incomplete observation | 7 | Automatic primary not captured: #1, #2, #3, #6, #7, #12, #14 — **excluded from correctness** (not counted as correct) |
| **Session accuracy** | **Not reported** | Deliberately omitted — denominators and primaries are incomplete; a percentage would be misleading. This live session is **never** merged with the offline 81.29% TEST score |

#### Interpretation notes

1. **Very low displayed confidence** — 11 of the 12 observed readings (0.2%–34%) sit **below** policy `accept_threshold = 0.57`: these would be **Provisional/Uncertain** and are **not** committed as automatic successes under the current release gate. The one above-threshold reading (What at 100% on Market) was wrong. Low confidence with wrong primaries still indicates a reliability problem worth investigating.
2. **Confusion between semantically or kinematically related signs** (Go↔Walk, Market/What/Big, Sit↔Teacher) warrants further controlled analysis; it aligns with offline per-class weaknesses (e.g. Sit F1 ≈ 0.17 on frozen TEST) but this session alone does not prove a mechanism.
3. **Missing confidence values and unrecorded primaries** are observation gaps (tester did not capture the UI state), not model outputs of “no score.”
4. **Static-versus-dynamic hypothesis (UNVERIFIED for this document):** the working hypothesis that the pipeline may under-weight natural movement (holding a sign still vs performing it dynamically) **has not been confirmed as root cause by this informal session.** It requires dedicated code inspection and controlled testing (see audit deliverable awaiting approval). It must not be reported as a proven defect until those checks are completed and recorded here with evidence. **Live static-held vs naturally-moving comparison: PENDING** — no such split result exists in project artifacts (the offline staticify/time_shuffle probes are synthetic input transforms, not live static/moving trials), so no such result is recorded here.
5. **Follow-up (2026-10-20):** the audit and its approved P0–P3 fix plan have since been executed — status, probe results (staticify 0.0091 / time_shuffle 0.4274 vs full 0.8129 on frozen TEST), and the failed retraining gates are recorded in `Docs/eval/static_dynamic_audit.md` (§ Implementation Status) and `Docs/eval/trajectory_ablation_result.md`; the shipped model `SBAI-MDL-ISL-4.0.0` was kept active.

#### Reporting status

| Item | Status |
| --- | --- |
| 15-sign checklist protocol | Created (`webcam_15_sign_checklist.md`) |
| This observation table | Recorded (preliminary, manual) — original checklist IDs + `unverified` / `not_observed` markers |
| Full checklist row completion / truth CSV | **PARTIAL** — checklist rows `C01`–`C15` + extra `X01` appended to `webcam_truth.csv`; 7 of 15 primaries unverified; M13 deck rows (A/H/R/S) still unfilled |
| Aggregate live accuracy claim | **NOT CALCULATED** (intentionally) — kept separate from offline TEST 81.29% |
| Static vs dynamic root-cause confirmation | **NOT CONFIRMED** — hypothesis only |
| Live static-held vs naturally-moving comparison | **PENDING** — no such data exists in project artifacts |
| Gemini real-API A/B test | **PENDING** — not performed (no `VITE_GEMINI_API_KEY`); no result claimed |

## 18. Usability and Accessibility Results

| Task | Participants / Runs | Success Rate | Average Time | Observed Issues | Interpretation |
| --- | --- | --- | --- | --- | --- |
| Start camera | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Position signer | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Perform sign | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Understand uncertainty | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| Recover from failure | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |

Participant information, consent procedures, and study limitations should be documented separately where required.

## 19. Statistical Analysis

- State the number of independent runs and summarize variability where repeated experiments were performed.
- Report mean ± standard deviation or an appropriate alternative when justified.
- Use confidence intervals where sample size and experimental design support them.
- Use statistical significance tests only when their assumptions are appropriate.
- Report effect sizes for important comparisons where possible.
- Distinguish statistical significance from practical significance.
- Document missing values, failed runs, exclusions, and deviations.

| Comparison | Metric | Difference | Statistical Test / CI | Effect Size | Conclusion |
| --- | --- | --- | --- | --- | --- |
| [Model A] vs [Model B] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| [Baseline] vs [Proposed] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |
| [Standard] vs [Robustness] | [Enter] | [Enter] | [Enter] | [Enter] | [Enter] |

## 20. Hypothesis Evaluation

| Hypothesis | Evidence | Result | Decision | Reason |
| --- | --- | --- | --- | --- |
| H1: Landmark representation meets predefined target | [Enter] | [Supported / Partial / Rejected / Inconclusive] | [Enter] | [Enter] |
| H2: Temporal model improves dynamic recognition | [Enter] | [Enter] | [Enter] | [Enter] |
| H3: Signer-independent performance remains acceptable | [Enter] | [Enter] | [Enter] | [Enter] |
| H4: Selected configuration meets real-time target | [Enter] | [Enter] | [Enter] | [Enter] |
| H5: Robustness degradation is measurable | [Enter] | [Enter] | [Enter] | [Enter] |
| H6: Uncertainty policy reduces forced errors | [Enter] | [Enter] | [Enter] | [Enter] |

## 21. Research Question Findings

| RQ | Finding | Evidence | Confidence / Limitation |
| --- | --- | --- | --- |
| RQ1 | [Enter finding] | [Experiment IDs / metrics] | [Enter] |
| RQ2 | [Enter finding] | [Experiment IDs / metrics] | [Enter] |
| RQ3 | [Enter finding] | [Experiment IDs / metrics] | [Enter] |
| RQ4 | [Enter finding] | [Experiment IDs / metrics] | [Enter] |
| RQ5 | [Enter finding] | [Experiment IDs / metrics] | [Enter] |
| RQ6 | [Enter finding] | [Experiment IDs / metrics] | [Enter] |

## 22. Gap Closure Analysis

| Gap ID | Research Gap | Evidence | Status | Remaining Work |
| --- | --- | --- | --- | --- |
| RG-01 | Dataset diversity | [Enter] | [Addressed / Partial / Open] | [Enter] |
| RG-02 | Signer-independent validation | [Enter] | [Enter] | [Enter] |
| RG-03 | Dynamic temporal representation | [Enter] | [Enter] | [Enter] |
| RG-04 | Landmark robustness | [Enter] | [Enter] | [Enter] |
| RG-05 | Class imbalance/confusion | [Enter] | [Enter] | [Enter] |
| RG-06 | Real-time trade-off | [Enter] | [Enter] | [Enter] |
| RG-07 | Environmental generalization | [Enter] | [Enter] | [Enter] |
| RG-08 | Uncertainty handling | [Enter] | [Enter] | [Enter] |
| RG-09 | End-to-end integration | [Enter] | [Enter] | [Enter] |
| RG-10 | Accessibility evaluation | [Enter] | [Enter] | [Enter] |
| RG-11 | Privacy-aware processing | [Enter] | [Enter] | [Enter] |
| RG-12 | Reproducibility | [Enter] | [Enter] | [Enter] |

## 23. Discussion

### 23.1 Interpretation Framework

- Identify the strongest empirical findings.
- Explain which experimental factors produced measurable changes.
- Discuss accuracy-versus-latency and accuracy-versus-robustness trade-offs.
- Identify classes, signers, or conditions that remain difficult.
- Compare findings with the expectations established by the literature survey.
- Distinguish findings supported by direct evidence from plausible explanations that require further study.
### 23.2 Comparison with Literature

| Literature Finding | SignBridge AI Result | Agreement / Difference | Interpretation |
| --- | --- | --- | --- |
| [Enter cited finding] | [Enter result] | [Agreement / Difference] | [Enter] |
| [Enter cited finding] | [Enter result] | [Enter] | [Enter] |
| [Enter cited finding] | [Enter result] | [Enter] | [Enter] |

### 23.3 Practical Implications

- [Enter implication for model design]
- [Enter implication for dataset design]
- [Enter implication for real-time deployment]
- [Enter implication for accessibility]
- [Enter implication for future research]
## 24. Limitations of the Results

- Results are limited by the size, diversity, and composition of the evaluated dataset.
- Performance metrics may not generalize beyond the supported sign vocabulary.
- Hardware-specific latency results should not be treated as universal.
- User-study findings, if based on a small sample, should not be generalized to the entire target population.
- Controlled robustness tests may not represent every real-world environment.
- Any unresolved dataset, annotation, model, or tracking limitations should be reported with the final results.
## 25. Key Findings

| Finding ID | Finding | Evidence | Impact | Status |
| --- | --- | --- | --- | --- |
| KF-01 | [Enter key finding] | [Metric / experiment] | [Enter] | [Confirmed / Preliminary] |
| KF-02 | [Enter key finding] | [Metric / experiment] | [Enter] | [Enter] |
| KF-03 | [Enter key finding] | [Metric / experiment] | [Enter] | [Enter] |
| KF-04 | [Enter key finding] | [Metric / experiment] | [Enter] | [Enter] |
| KF-05 | [Enter key finding] | [Metric / experiment] | [Enter] | [Enter] |

## 26. Recommendations

- [Enter evidence-based model recommendation]
- [Enter evidence-based dataset recommendation]
- [Enter evidence-based preprocessing recommendation]
- [Enter performance optimization recommendation]
- [Enter robustness improvement recommendation]
- [Enter accessibility/usability recommendation]
- [Enter future research recommendation]
Recommendations should be directly supported by recorded evidence. Avoid converting unresolved hypotheses into confirmed recommendations.

## 27. Reproducibility Record

| Artifact | Identifier / Location | Verified By | Date |
| --- | --- | --- | --- |
| Dataset | [Enter version/path] | [Enter] | [Date] |
| Source Code | [Enter repository/commit] | [Enter] | [Date] |
| Preprocessing | [Enter version] | [Enter] | [Date] |
| Model | [Enter model version/hash] | [Enter] | [Date] |
| Experiment Config | [Enter ID/path] | [Enter] | [Date] |
| Evaluation Script | [Enter version/path] | [Enter] | [Date] |
| Raw Results | [Enter location] | [Enter] | [Date] |
| Benchmark Logs | [Enter location] | [Enter] | [Date] |

## 28. Traceability

| Related Document | Relationship |
| --- | --- |
| 04 Dataset Specification | Provides the dataset definitions and constraints for interpreting results. |
| 05 AI Model Specification | Defines model scope and expected evaluation measures. |
| 06 Preprocessing & Feature Engineering | Defines preprocessing versions evaluated. |
| 11 Testing & Evaluation | Provides test strategy and quality criteria. |
| 23 Model Training Specification | Defines training and validation methodology. |
| 24 Model Versioning & Experiment Log | Provides experiment and artifact identifiers. |
| 25 Performance Benchmark | Provides detailed performance measurements. |
| 31 Risk Register | Links results to technical and operational risks. |
| 32 Known Issues & Limitations | Captures limitations confirmed by experimental evidence. |
| 33 Research Methodology | Defines the research process. |
| 34 Literature Survey | Provides literature context for interpretation. |
| 35 Research Gap Analysis | Defines gaps that results are expected to investigate. |
| 36 Experimental Design | Defines the experiments and protocols whose results are recorded here. |

## 29. Version History

| Version | Date | Author | Change Description |
| --- | --- | --- | --- |
| 1.0 | [Enter Date] | [Enter Name] | Initial Results & Analysis document. |
| 1.1 | [Enter Date] | [Enter Name] | [Enter changes] |
| 1.2 | [Enter Date] | [Enter Name] | [Enter changes] |

## 30. Review and Approval

| Role | Name | Signature / Approval | Date |
| --- | --- | --- | --- |
| Prepared By | [Enter Name] | [Enter] | [Date] |
| Research Lead | [Enter Name] | [Enter] | [Date] |
| ML / AI Lead | [Enter Name] | [Enter] | [Date] |
| Technical Lead | [Enter Name] | [Enter] | [Date] |
| Project Owner | [Enter Name] | [Enter] | [Date] |
| Approved By | [Enter Name] | [Enter] | [Date] |

*Document Control Note: Populate this document only with measured or formally reviewed evidence. Replace placeholders with results from the approved experiments and retain links to the underlying experiment records.*
