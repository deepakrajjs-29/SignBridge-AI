<!-- Source: 36_Experimental_Design_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# SIGNBRIDGE AI

## EXPERIMENTAL DESIGN

*Controlled experimental framework for dataset, preprocessing, model, robustness, and real-time evaluation*

| Field | Value |
| --- | --- |
| Document ID | SBAI-EXP-001 |
| Document Number | 36 |
| Version | 1.0 |
| Status | Draft / Editable |
| Project | SignBridge AI |
| Research Area | Indian Sign Language Recognition / Computer Vision / AI |
| Related Research Gap | 35 Research Gap Analysis |
| Prepared By | [Enter Name / Team] |
| Reviewed By | [Enter Reviewer] |
| Approved By | [Enter Approver] |
| Effective Date | [Enter Date] |
| Last Updated | [Enter Date] |

## Table of Contents

1. 1. Purpose
1. 2. Scope
1. 3. Experimental Principles
1. 4. Experimental Objectives
1. 5. Research Questions and Hypotheses
1. 6. Experimental Variables
1. 7. Experimental Factors and Levels
1. 8. Dataset and Sampling Design
1. 9. Train/Validation/Test Protocol
1. 10. Baseline Design
1. 11. Preprocessing Experiments
1. 12. Feature Engineering Experiments
1. 13. Model Architecture Experiments
1. 14. Hyperparameter Experiments
1. 15. Ablation Studies
1. 16. Robustness Experiments
1. 17. Generalization Experiments
1. 18. Real-Time Performance Experiments
1. 19. End-to-End System Experiments
1. 20. Usability and Accessibility Experiments
1. 21. Statistical Analysis Plan
1. 22. Reproducibility Controls
1. 23. Experiment Execution Workflow
1. 24. Experiment Record Template
1. 25. Acceptance and Decision Criteria
1. 26. Expected Experimental Outputs
1. 27. Traceability
1. 28. Version History
1. 29. Review and Approval
## 1. Purpose

This document defines the controlled experimental framework for SignBridge AI. It specifies how research questions will be converted into measurable experiments, how baselines and variables will be controlled, how model and system configurations will be compared, and how results will be recorded for reproducibility and decision-making.

The experimental design is intended to prevent uncontrolled changes from being interpreted as evidence of improvement. Every material experiment should have a unique identifier, a defined objective, a baseline, a documented configuration, an evaluation protocol, and a recorded conclusion.

## 2. Scope

- Dataset composition, quality, splitting, and sampling experiments.
- Landmark extraction, normalization, sequence construction, and feature-engineering experiments.
- Temporal model architecture and hyperparameter experiments.
- Ablation and component-contribution studies.
- Signer-independent, environmental, occlusion, and tracking robustness experiments.
- Latency, FPS, memory, throughput, and resource experiments.
- End-to-end application and integration experiments.
- Usability and accessibility evaluation where applicable.
- Reproducibility, statistical analysis, and experiment decision records.
## 3. Experimental Principles

- Control: change only the intended experimental factor whenever possible.
- Fair comparison: use the same evaluation split and metric definitions for competing configurations.
- Traceability: link every result to code, dataset, preprocessing, model, and environment versions.
- Reproducibility: record configuration, seed, hardware, runtime, and dependency information where relevant.
- Isolation: keep final test data isolated from model selection and tuning.
- Evidence-first decisions: adopt changes based on recorded evidence rather than assumptions.
- Negative-result preservation: retain unsuccessful and inconclusive experiments for research traceability.
- Responsible reporting: do not claim broader generalization than the tested population and conditions support.
## 4. Experimental Objectives

| Objective ID | Objective | Primary Evidence |
| --- | --- | --- |
| EO-01 | Establish a reliable baseline for supported ISL recognition. | Baseline metrics and error analysis. |
| EO-02 | Determine the effect of preprocessing and feature representation. | Controlled comparison and ablation results. |
| EO-03 | Evaluate suitable temporal model architectures. | Validation/test metrics and resource profile. |
| EO-04 | Measure signer-independent generalization. | Unseen-signer evaluation. |
| EO-05 | Measure environmental and tracking robustness. | Condition-wise degradation analysis. |
| EO-06 | Determine an acceptable accuracy-latency trade-off. | Benchmark results. |
| EO-07 | Validate integrated application behavior. | End-to-end evaluation. |
| EO-08 | Assess accessibility and uncertainty handling. | Task and interaction observations. |
| EO-09 | Produce reproducible research evidence. | Versioned experiment records and artifacts. |

## 5. Research Questions and Hypotheses

| ID | Research Question | Illustrative Hypothesis | Primary Experiment |
| --- | --- | --- | --- |
| RQ1 | Can normalized temporal landmarks effectively represent supported ISL signs? | H1: The selected landmark representation meets the predefined baseline performance target. | EXP-REP |
| RQ2 | Does temporal modeling improve dynamic-sign recognition? | H2: A temporal model improves dynamic-sign performance over a frame-level baseline. | EXP-TEMP |
| RQ3 | How well does the selected approach generalize to unseen signers? | H3: Signer-independent performance remains within the predefined acceptable range. | EXP-SIGNER |
| RQ4 | Which preprocessing/feature configuration provides the best trade-off? | H4: One controlled configuration provides measurable benefit without unacceptable computational cost. | EXP-FEAT |
| RQ5 | Can the system operate within the real-time target? | H5: The selected configuration meets the defined latency/FPS target on supported hardware. | EXP-RT |
| RQ6 | Which environmental conditions most affect recognition? | H6: Specific conditions produce measurable and repeatable degradation. | EXP-ROB |
| RQ7 | Does uncertainty handling reduce forced incorrect predictions? | H7: A validated threshold/unknown state reduces accepted low-confidence errors. | EXP-CONF |

## 6. Experimental Variables

| Variable Type | Examples | Control / Measurement |
| --- | --- | --- |
| Independent | Model family, sequence length, normalization, feature set, augmentation, threshold, input resolution. | Set explicitly per experiment. |
| Dependent | Accuracy, precision, recall, macro F1, class-wise F1, confusion, latency, FPS, memory. | Measured using fixed protocols. |
| Controlled | Dataset split, class set, metric definitions, hardware, runtime, random seed where applicable. | Hold constant within comparisons. |
| Blocking / Stratification | Signer, sign class, environment, device. | Report or balance where appropriate. |
| Confounding | Different preprocessing, data leakage, hardware changes, dependency changes. | Detect and document. |

## 7. Experimental Factors and Levels

| Factor | Example Levels | Notes |
| --- | --- | --- |
| Sequence Length | [16, 32, 48, 64] frames | Use only lengths supported by the data and model. |
| Feature Set | Coordinates / normalized coordinates / motion features / combined | Evaluate under identical split and training policy. |
| Model Family | Baseline / LSTM-GRU / TCN / Attention or Transformer | Select technically appropriate candidates. |
| Input Resolution | [Enter supported levels] | Higher resolution may affect tracking and latency. |
| Confidence Threshold | [Enter threshold range] | Evaluate coverage vs error trade-off. |
| Augmentation | None / spatial / temporal / combined | Apply only to training data. |
| Inference Mode | Local / server / hybrid where applicable | Measure separately because latency differs. |
| Hardware | Reference CPU / GPU / target device | Record exact configuration. |

## 8. Dataset and Sampling Design

- Define the target sign vocabulary before final experiments.
- Ensure samples have stable labels and documented quality status.
- Use signer-aware splitting when measuring generalization to unseen signers.
- Prevent the same signer or near-duplicate sequence from appearing across train and final test sets when that would create leakage.
- Report class distribution for each split.
- Use stratification where feasible while preserving signer independence.
- Document inclusion/exclusion criteria and any data removed after preprocessing.
- Freeze the evaluation set before final model selection.
## 9. Train/Validation/Test Protocol

| Split | Purpose | Permitted Use |
| --- | --- | --- |
| Training | Fit model parameters. | Training, approved augmentation, optimization. |
| Validation | Select model/configuration and tune parameters. | Model selection, threshold tuning, early stopping. |
| Test | Estimate final generalization. | Final evaluation only after selection. |
| Signer-Independent Test | Measure unseen-signer generalization. | Research evaluation and final reporting. |
| Robustness Set | Measure controlled condition changes. | Robustness analysis; not used for tuning unless explicitly defined. |

Recommended default split ratios may be configured by the Dataset Specification. The critical requirement is strict separation and signer-aware policy where generalization is a research objective.

## 10. Baseline Design

A baseline establishes a reference point against which subsequent methods are compared. The baseline should be simple enough to interpret and implemented using the same core dataset split and evaluation metrics.

| Baseline | Input | Purpose |
| --- | --- | --- |
| B1 Frame-Level Classifier | Single-frame landmark/features | Measure performance without temporal context. |
| B2 Simple Temporal Model | Short landmark sequence | Establish a temporal reference. |
| B3 Proposed Model | Approved full feature/sequence representation | Evaluate final candidate. |
| B4 Optional Raw-Image Baseline | Image/video input if feasible | Contextual comparison with landmark approach. |

## 11. Preprocessing Experiments

- Compare coordinate normalization strategies.
- Measure the effect of missing-landmark handling.
- Compare fixed-length sampling approaches where multiple approaches are feasible.
- Evaluate smoothing only if it does not introduce unacceptable temporal delay.
- Measure whether preprocessing improves generalization as well as aggregate validation accuracy.
- Keep preprocessing versions independent and traceable.

| Experiment ID | Question | Baseline | Variable | Metric | Decision |
| --- | --- | --- | --- | --- | --- |
| EXP-PRE-001 | Does coordinate normalization improve recognition? | Raw/standard preprocessing | Normalization method | Macro F1, latency | [Enter] |
| EXP-PRE-002 | Does missing-point handling improve robustness? | Default handling | Interpolation/fallback | Macro F1, failure rate | [Enter] |
| EXP-PRE-003 | Which sequence sampling method is preferable? | Default sampling | Sampling strategy | F1, latency | [Enter] |

## 12. Feature Engineering Experiments

| Experiment | Feature Comparison | Primary Metrics | Secondary Metrics |
| --- | --- | --- | --- |
| EXP-FEAT-001 | Coordinates vs normalized coordinates | Macro F1 | Latency, memory |
| EXP-FEAT-002 | Coordinates vs motion deltas | Dynamic-class F1 | Confusion patterns |
| EXP-FEAT-003 | Single feature family vs combined features | Macro F1 | Model size, latency |
| EXP-FEAT-004 | Different reference/scale normalization | Signer-independent F1 | Robustness metrics |

## 13. Model Architecture Experiments

Candidate architectures should be selected based on the research question and available resources. The following structure is a template rather than a requirement to implement every model family.

| Experiment | Candidate | Comparison Basis |
| --- | --- | --- |
| EXP-MOD-001 | Frame-level baseline | Establish non-temporal reference. |
| EXP-MOD-002 | LSTM/GRU or equivalent recurrent model | Temporal baseline. |
| EXP-MOD-003 | Temporal convolutional model | Temporal efficiency comparison. |
| EXP-MOD-004 | Attention/Transformer-style model | Long-range temporal comparison. |
| EXP-MOD-005 | Selected optimized model | Accuracy-latency deployment candidate. |

- Keep feature representation and data split constant when comparing architectures.
- Record parameter count, model size, training time, inference latency, and performance.
- Do not select a model using test-set performance during development.
## 14. Hyperparameter Experiments

| Parameter | Example Search Space | Selection Rule |
| --- | --- | --- |
| Learning Rate | [1e-4, 3e-4, 1e-3, ...] | Best validation result subject to stability. |
| Batch Size | [16, 32, 64] | Performance and resource feasibility. |
| Sequence Length | [16, 32, 48, 64] | Best validation/latency trade-off. |
| Hidden Dimension | [64, 128, 256] | Validation performance and complexity. |
| Dropout | [0.0, 0.2, 0.4, 0.5] | Generalization and training stability. |
| Optimizer | [Enter options] | Validation performance and convergence. |
| Confidence Threshold | [Enter range] | Error/coverage trade-off. |

Search spaces should be finalized before large-scale tuning when practical. Hyperparameter search must use validation data and must not repeatedly optimize against the final test set.

## 15. Ablation Studies

Ablation experiments determine the contribution of individual pipeline components.

| Ablation ID | Full Configuration | Removed/Changed Component | Expected Insight |
| --- | --- | --- | --- |
| ABL-001 | Full model | Remove motion features | Contribution of temporal motion information. |
| ABL-002 | Full model | Remove normalization | Importance of spatial normalization. |
| ABL-003 | Full model | Shorter sequence | Importance of temporal context. |
| ABL-004 | Full model | No augmentation | Contribution of training augmentation. |
| ABL-005 | Full model | Reduced feature set | Efficiency versus accuracy trade-off. |
| ABL-006 | Full pipeline | Alternative landmark subset | Contribution of hand/body components. |

## 16. Robustness Experiments

| Experiment | Condition | Measurement |
| --- | --- | --- |
| EXP-ROB-001 | Low lighting | Macro F1 degradation, landmark failure rate |
| EXP-ROB-002 | Backlighting | Recognition degradation, tracking failures |
| EXP-ROB-003 | Background clutter | Class performance and tracking stability |
| EXP-ROB-004 | Partial occlusion | Recognition and unknown-state rate |
| EXP-ROB-005 | Fast signing | Dynamic-class F1 and temporal failure rate |
| EXP-ROB-006 | Camera distance variation | Performance versus capture distance |
| EXP-ROB-007 | Camera angle variation | Performance versus viewpoint |
| EXP-ROB-008 | Frame drops | Sequence stability and latency |

## 17. Generalization Experiments

Generalization should be evaluated using data not represented by the training participants or, where appropriate, the training capture conditions.

| Generalization Dimension | Training Condition | Evaluation Condition | Primary Metric |
| --- | --- | --- | --- |
| Signer | Set A | Unseen signers | Macro F1 |
| Environment | Controlled | Different background/lighting | Macro F1 |
| Camera | Reference setup | Different supported devices | Macro F1 + latency |
| Signing speed | Normal | Slow/fast | Dynamic-class F1 |
| Capture distance | Reference | Near/far supported range | F1 + tracking quality |

## 18. Real-Time Performance Experiments

Real-time experiments must measure the full processing pipeline and identify where time is spent.

| Measurement | Definition | Target / Acceptance |
| --- | --- | --- |
| Capture-to-Prediction Latency | Time from usable input capture to prediction availability. | Preferred < 200 ms; editable. |
| FPS | Sustained processing rate. | Preferred ≥ 15 FPS; editable. |
| Model Inference Time | Model-only processing duration. | [Enter target] |
| Landmark Processing Time | Detection/tracking duration. | [Enter target] |
| Memory Usage | Peak or sustained memory consumption. | [Enter target] |
| CPU/GPU Utilization | Resource consumption during representative load. | [Enter target] |
| Startup Time | Time to initialize application/model. | [Enter target] |

The targets above are project defaults and must be reported as targets unless measured and achieved under a documented test configuration.

## 19. End-to-End System Experiments

- Camera permission granted → capture → landmarks → preprocessing → inference → postprocessing → UI result.
- Camera permission denied → clear user guidance and recoverable state.
- Backend unavailable → timeout/error state without exposing internal details.
- Low-confidence prediction → uncertainty state rather than forced semantic output.
- Model-version mismatch → compatibility error or controlled fallback.
- Session reset → correct release of camera/resources and clean restart.
- External text-to-speech or related service unavailable → graceful fallback where supported.
## 20. Usability and Accessibility Experiments

| Experiment | Task | Observation / Metric |
| --- | --- | --- |
| EXP-UX-001 | Start camera and position signer | Task completion, errors, time |
| EXP-UX-002 | Perform supported sign | Recognition feedback comprehension |
| EXP-UX-003 | Recover from low confidence | Recovery success |
| EXP-UX-004 | Handle camera permission issue | Task completion |
| EXP-UX-005 | Interpret prediction/uncertainty | User understanding |
| EXP-UX-006 | Use supported accessibility controls | Accessibility task completion |

Where human participants are involved, use the approved participant, consent, privacy, and study procedures. Report sample size and sampling limitations.

## 21. Statistical Analysis Plan

- Report aggregate and class-wise metrics.
- Use macro F1 when class imbalance could hide weak classes.
- For repeated runs, report mean and standard deviation or another appropriate uncertainty summary.
- Use confidence intervals or significance tests only when their assumptions and sample sizes support them.
- Report effect size for meaningful comparisons where appropriate.
- Do not interpret statistically significant but practically negligible changes as meaningful improvements.
- Document failed runs, excluded samples, and protocol deviations.
## 22. Reproducibility Controls

| Artifact | Required Version Information |
| --- | --- |
| Dataset | Dataset ID/version, split definition, checksum where applicable |
| Code | Repository/version/commit identifier |
| Preprocessing | Pipeline version and parameters |
| Model | Architecture/version/configuration |
| Training | Seed, optimizer, learning rate, batch size, epochs |
| Runtime | OS, Python/framework/runtime versions |
| Hardware | CPU/GPU, RAM, device model |
| Experiment | Experiment ID and configuration file |
| Results | Raw metrics, summary, logs, and conclusion |

## 23. Experiment Execution Workflow

1. Create experiment ID and record research question.
1. Define baseline, independent variable, controlled variables, and success criteria.
1. Freeze the dataset split and configuration required for the experiment.
1. Run the baseline under the same evaluation conditions.
1. Run the candidate configuration.
1. Repeat runs when variability needs to be estimated.
1. Collect metrics, logs, errors, resource measurements, and observations.
1. Analyze results without changing the predefined protocol unless a deviation is explicitly recorded.
1. Conclude whether the hypothesis is supported, partially supported, rejected, or inconclusive.
1. Update the experiment log, model version, benchmark, risk, defect, or limitation records as applicable.
## 24. Experiment Record Template

| Field | Entry |
| --- | --- |
| Experiment ID | EXP-YYYY-NNN |
| Title | [Enter experiment name] |
| Date | [Enter date] |
| Research Question | [Enter RQ] |
| Hypothesis | [Enter hypothesis] |
| Objective | [Enter objective] |
| Dataset Version | [Enter] |
| Split | [Enter] |
| Preprocessing Version | [Enter] |
| Feature Set | [Enter] |
| Model Version | [Enter] |
| Independent Variable | [Enter] |
| Controlled Variables | [Enter] |
| Hardware / Runtime | [Enter] |
| Training Configuration | [Enter] |
| Evaluation Protocol | [Enter] |
| Metrics | [Enter] |
| Baseline Result | [Enter] |
| Candidate Result | [Enter] |
| Statistical Summary | [Enter] |
| Observations | [Enter] |
| Failures / Deviations | [Enter] |
| Conclusion | [Supported / Partially Supported / Rejected / Inconclusive] |
| Decision | [Adopt / Modify / Repeat / Archive] |
| Artifact Location | [Enter] |
| Reviewer | [Enter] |

## 25. Acceptance and Decision Criteria

| Decision | Criteria |
| --- | --- |
| Adopt | Meets predefined performance requirements, does not introduce unacceptable regressions, and has reproducible evidence. |
| Modify | Shows promise but fails one or more defined criteria that can reasonably be addressed. |
| Repeat | Results are inconclusive, unstable, or affected by a protocol deviation. |
| Archive | Does not provide sufficient benefit or violates constraints; retain record for traceability. |
| Escalate | Creates critical security, privacy, integrity, or severe reliability concerns. |

Default release-oriented targets may include accuracy ≥ 90%, macro F1 ≥ 0.90, preferred latency < 200 ms, sustained processing ≥ 15 FPS, adequate core test coverage, and no unresolved critical security/privacy findings. These targets remain editable and must be evaluated against the approved release criteria.

## 26. Expected Experimental Outputs

- Baseline model and baseline metrics.
- Preprocessing and feature comparison results.
- Model architecture comparison.
- Hyperparameter study results.
- Ablation findings.
- Signer-independent generalization results.
- Robustness and environmental stress-test results.
- Real-time latency/FPS/resource benchmark.
- End-to-end integration results.
- Usability/accessibility observations where applicable.
- Final experiment conclusions and evidence supporting model/system selection.
## 27. Traceability

| Related Document | Relationship |
| --- | --- |
| 04 Dataset Specification | Defines dataset scope, quality, labels, participants, and split constraints. |
| 05 AI Model Specification | Defines model candidates, inputs, outputs, and evaluation requirements. |
| 06 Preprocessing & Feature Engineering | Defines preprocessing and feature configurations tested here. |
| 11 Testing & Evaluation | Defines validation and quality-assurance processes. |
| 23 Model Training Specification | Defines training controls and reproducibility requirements. |
| 24 Model Versioning & Experiment Log | Stores experiment identifiers, configurations, and results. |
| 25 Performance Benchmark | Stores detailed latency, FPS, and resource measurements. |
| 31 Risk Register | Tracks risks identified or revealed by experiments. |
| 32 Known Issues & Limitations | Records limitations confirmed through experimental evidence. |
| 33 Research Methodology | Defines the broader research methodology. |
| 34 Literature Survey | Provides research context and evidence motivating experiments. |
| 35 Research Gap Analysis | Maps unresolved gaps to experimental objectives. |

## 28. Version History

| Version | Date | Author | Change Description |
| --- | --- | --- | --- |
| 1.0 | [Enter Date] | [Enter Name] | Initial Experimental Design document. |
| 1.1 | [Enter Date] | [Enter Name] | [Enter changes] |
| 1.2 | [Enter Date] | [Enter Name] | [Enter changes] |

## 29. Review and Approval

| Role | Name | Signature / Approval | Date |
| --- | --- | --- | --- |
| Prepared By | [Enter Name] | [Enter] | [Date] |
| Research Lead | [Enter Name] | [Enter] | [Date] |
| ML / AI Lead | [Enter Name] | [Enter] | [Date] |
| Technical Lead | [Enter Name] | [Enter] | [Date] |
| Project Owner | [Enter Name] | [Enter] | [Date] |
| Approved By | [Enter Name] | [Enter] | [Date] |

*Document Control Note: This document is a controlled experimental framework. Update it whenever research questions, model candidates, evaluation criteria, dataset protocols, hardware targets, or project acceptance criteria materially change.*
