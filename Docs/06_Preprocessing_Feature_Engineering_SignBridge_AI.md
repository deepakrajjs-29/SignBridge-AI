<!-- Source: 06_Preprocessing_Feature_Engineering_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# PREPROCESSING & FEATURE ENGINEERING

## SignBridge AI – Indian Sign Language (ISL) Recognition System

| Field | Details |
| --- | --- |
| Document ID | 06_Preprocessing_Feature_Engineering |
| Project | SignBridge AI |
| Document Type | Preprocessing & Feature Engineering Specification |
| Version | 1.0 |
| Status | Draft / Editable |
| Primary Input | Raw image/video frames |
| Primary Output | Normalized temporal feature sequences |
| Primary Tools | OpenCV + MediaPipe + Python – [Confirm] |

## 1. Purpose

This document defines the preprocessing and feature-engineering pipeline used to convert raw camera/video data into consistent, normalized, model-ready representations for SignBridge AI. The pipeline is designed to reduce irrelevant variation while preserving the spatial and temporal information required for Indian Sign Language recognition.

## 2. Objectives

- Convert raw video into standardized frame sequences.
- Detect and extract relevant hand and body landmarks.
- Normalize landmark coordinates to reduce variation caused by position, scale, and camera distance.
- Generate temporal features that represent sign movement.
- Handle missing, noisy, or low-quality landmark detections.
- Create reproducible model-ready features for training and real-time inference.
- Ensure the same preprocessing logic is used during training and deployment.
## 3. End-to-End Processing Pipeline

Recommended processing flow:

Raw Video / Camera
        ↓
Frame Capture
        ↓
Frame Quality Check
        ↓
Resize / Color Conversion
        ↓
Hand + Pose Landmark Detection
        ↓
Landmark Validation
        ↓
Coordinate Normalization
        ↓
Spatial Feature Extraction
        ↓
Temporal Feature Extraction
        ↓
Sequence Construction
        ↓
Padding / Sampling / Alignment
        ↓
Feature Scaling
        ↓
Model-Ready Tensor
        ↓
AI Model

## 4. Input Data Specification

| Parameter | Recommended Specification | Project Value |
| --- | --- | --- |
| Input type | RGB video / webcam frames | [Enter] |
| Source resolution | 720p or higher preferred | [Enter] |
| Frame rate | 24–30 FPS preferred | [Enter] |
| Color space | RGB | [Enter] |
| Sequence length | 30–60 frames | [Enter] |
| Camera view | Primarily frontal | [Enter] |
| Subject visibility | Hands and required upper body visible | [Enter] |

## 5. Frame Extraction

- Read video frames sequentially while preserving temporal order.
- Record source FPS and frame count as metadata.
- Discard corrupted or unreadable frames.
- Use uniform frame sampling when the source sequence is longer than the configured model window.
- Use temporal padding or controlled repetition when a valid sequence is shorter than the required length.
## 6. Image Preprocessing

| Operation | Specification | Purpose |
| --- | --- | --- |
| Resize | Model-dependent dimensions | Standardize processing |
| Color conversion | BGR → RGB where required | Correct model input |
| Normalization | Pixel/feature normalization as required | Stable computation |
| Cropping | Optional region-of-interest crop | Reduce irrelevant background |
| Quality filtering | Remove unusable frames | Improve input quality |

## 7. Landmark Detection

MediaPipe Hands or MediaPipe Holistic may be used to extract hand and body landmarks. The exact detector configuration must be versioned because changes in detector configuration can affect downstream model features.

| Landmark Group | Typical Representation | Purpose |
| --- | --- | --- |
| Left hand | 21 × (x, y, z) | Left-hand shape and movement |
| Right hand | 21 × (x, y, z) | Right-hand shape and movement |
| Pose | Selected body landmarks | Upper-body context |
| Face | Optional selected landmarks | Non-manual facial cues |

## 8. Landmark Validation

- Check whether each expected landmark group is detected.
- Record detector confidence where available.
- Flag frames with severe tracking loss.
- Avoid treating an absent hand as a valid zero-coordinate hand without an explicit mask.
- Maintain a missing-data mask when landmark availability is relevant to the model.
## 9. Coordinate Normalization

Raw landmark coordinates are affected by signer position, camera distance, body size, and hand location. Normalization should preserve relative sign geometry while reducing these variations.

| Method | Description | Recommended Use |
| --- | --- | --- |
| Translation normalization | Subtract reference landmark/hand center | Reduce absolute position |
| Scale normalization | Divide by hand/body reference distance | Reduce size variation |
| Range normalization | Map coordinates to fixed range | Standardized model input |
| Z normalization | Normalize depth relative to reference | Reduce depth variation |

## 10. Recommended Hand Normalization

For each detected hand, a reference point such as the wrist may be used. Each landmark can be represented relative to the wrist and then scaled by a stable hand-size measure.

**normalized_point = (landmark - reference_point) / reference_scale**

The exact reference point and scale must be fixed for the dataset and deployment pipeline.

## 11. Spatial Feature Engineering

| Feature | Description | Use |
| --- | --- | --- |
| Normalized coordinates | Relative x/y/z positions | Primary spatial representation |
| Pairwise distances | Distance between selected joints | Hand geometry |
| Joint angles | Angles formed by connected landmarks | Finger articulation |
| Bounding-box features | Hand extent/size | Scale/context |
| Hand orientation | Optional orientation features | Pose configuration |

## 12. Temporal Feature Engineering

Dynamic signs require information across multiple frames. Temporal features are computed from the ordered landmark sequence.

| Feature | Concept | Purpose |
| --- | --- | --- |
| Velocity | Δposition / Δtime | Movement direction and speed |
| Acceleration | Δvelocity / Δtime | Movement changes |
| Displacement | Position difference over interval | Overall movement |
| Trajectory | Ordered landmark path | Sign motion pattern |
| Temporal statistics | Mean/std/max over sequence | Sequence summary |

## 13. Velocity and Acceleration

v_t = (x_t - x_(t-1)) / Δt
a_t = (v_t - v_(t-1)) / Δt

Velocity and acceleration should be calculated only after coordinate normalization and with a consistent frame interval where possible.

## 14. Sequence Construction

- Collect a temporal window containing the required number of frames.
- Preserve frame order.
- Ensure each frame has the same feature layout.
- Attach the correct class label to the complete training sequence.
- Apply padding or sampling only according to the configured sequence policy.
## 15. Sequence Length Management

| Case | Processing Strategy |
| --- | --- |
| Sequence exactly target length | Use directly |
| Longer sequence | Uniform sampling / sliding window |
| Shorter sequence | Temporal padding/repetition with mask if required |
| Variable-duration sign | Temporal normalization or controlled sampling |
| Continuous input | Use rolling window for real-time inference |

## 16. Missing Data Handling

- Use short-gap interpolation only when the movement remains reliable.
- Use a missing-data mask when landmark absence carries information.
- Do not interpolate across long periods of tracking failure.
- Reject samples with severe or persistent landmark loss during dataset cleaning.
- Use the same missing-data policy during training and inference.
## 17. Noise Reduction

Landmark detectors may produce frame-to-frame jitter. A light smoothing method may be applied, provided that it does not remove meaningful fast sign movements.

| Method | Purpose | Caution |
| --- | --- | --- |
| Moving average | Reduce high-frequency noise | May blur rapid motion |
| Exponential smoothing | Stable real-time output | Tune smoothing factor |
| Median filtering | Remove isolated spikes | Can alter sharp movement |
| No smoothing | Preserve raw motion | More detector noise |

## 18. Data Augmentation

Augmentation must be applied only to training data unless a specific robustness experiment requires otherwise.

- Small coordinate translation.
- Controlled scale variation.
- Small rotation where semantically safe.
- Temporal speed variation.
- Limited frame dropping.
- Controlled coordinate noise.
Avoid transformations that can change handedness or the semantic meaning of an ISL sign.

## 19. Feature Scaling

| Approach | Description | Requirement |
| --- | --- | --- |
| Min-max scaling | Map values to a fixed interval | Fit parameters on training data |
| Standardization | Zero mean / unit variance | Fit statistics on training data |
| Coordinate normalization | Geometric normalization | Apply consistently |
| No additional scaling | Use already normalized features | Only if validated |

## 20. Preventing Data Leakage

- Calculate feature-scaling parameters using training data only.
- Do not use test-set statistics for normalization.
- Keep signer identities separated between train, validation, and test.
- Do not generate augmented versions of test samples for training.
- Freeze preprocessing configuration before final test evaluation.
## 21. Feature Vector Specification

The final feature vector should have a fixed and documented ordering. Example representation:

| Feature Block | Example Size | Project Value |
| --- | --- | --- |
| Left-hand coordinates | 21 × 3 = 63 | [Enter] |
| Right-hand coordinates | 21 × 3 = 63 | [Enter] |
| Pose features | Selected landmarks × 3 | [Enter] |
| Distances | Selected joint pairs | [Enter] |
| Angles | Selected joints | [Enter] |
| Velocity | Same spatial dimensions | [Enter] |
| Acceleration | Same spatial dimensions | [Enter] |
| Missing-data mask | Optional | [Enter] |
| Total features/frame | Calculated | [Enter] |

## 22. Model-Ready Tensor Format

For a temporal model such as LSTM/GRU, the recommended input shape is:

**(batch_size, sequence_length, feature_dimension)**

Example: (32, 45, F), where 32 is the batch size, 45 is the sequence length, and F is the final feature dimension.

## 23. Training vs. Inference Consistency

- Use the same landmark detector family and compatible configuration.
- Use identical coordinate normalization logic.
- Use identical feature ordering.
- Use identical scaling parameters.
- Use identical sequence-length handling.
- Use the same smoothing and missing-data rules where applicable.
## 24. Real-Time Preprocessing Pipeline

1. Capture current camera frame.

2. Convert frame to the required color format.

3. Run landmark detection.

4. Validate hand/pose tracking.

5. Normalize landmarks.

6. Calculate required spatial/temporal features.

7. Append features to rolling sequence buffer.

8. When the buffer is ready, run model inference.

9. Apply confidence threshold and temporal smoothing.

10. Return recognized sign to the application.

## 25. Computational Requirements

| Component | Requirement |
| --- | --- |
| Frame processing | Should operate continuously at application target FPS |
| Landmark detection | Real-time capable configuration |
| Feature extraction | Low computational overhead |
| Memory | Rolling buffer only where possible |
| Parallelism | Optional asynchronous capture/inference |
| Hardware | CPU baseline; GPU optional |

## 26. Quality Control and Validation

| Check | Acceptance Criterion |
| --- | --- |
| Frame order | Temporal order preserved |
| Landmark count | Expected landmarks present or correctly masked |
| Coordinate range | Within configured normalized range |
| Feature dimension | Fixed across all samples |
| NaN/Inf values | None in model input |
| Sequence length | Matches model requirement |
| Label alignment | Correct label assigned to sequence |
| Reproducibility | Same input produces equivalent features |

## 27. Preprocessing Configuration

| Parameter | Current Value |
| --- | --- |
| Landmark framework | MediaPipe – [Confirm version] |
| Input FPS | [Enter] |
| Target sequence length | [Enter] |
| Image resolution | [Enter] |
| Reference landmark | Wrist / [Confirm] |
| Scale normalization | [Enter method] |
| Smoothing | [Enter method] |
| Missing-data strategy | [Enter] |
| Feature scaling | [Enter] |
| Augmentation | [Enter] |
| Total features/frame | [Enter] |
| Preprocessing version | v1.0 |

## 28. Feature Dictionary

| Feature ID | Feature Name | Type | Description |
| --- | --- | --- | --- |
| F001 | left_hand_x/y/z | Continuous | Normalized left-hand landmark coordinates |
| F002 | right_hand_x/y/z | Continuous | Normalized right-hand landmark coordinates |
| F003 | pose_x/y/z | Continuous | Selected normalized pose landmarks |
| F004 | joint_distance | Continuous | Selected landmark distances |
| F005 | joint_angle | Continuous | Selected joint angles |
| F006 | velocity | Continuous | Frame-to-frame movement |
| F007 | acceleration | Continuous | Change in movement |
| F008 | visibility_mask | Binary | Landmark availability indicator |

## 29. Failure Handling

- If no hand is detected, return a tracking/no-sign state rather than an arbitrary class.
- If tracking is temporarily lost, retain a short buffer only when the configured policy permits.
- If the input sequence is invalid, do not send it to the model.
- Log preprocessing failures for debugging and dataset improvement.
- Avoid crashing the real-time application because of a single bad frame.
## 30. Versioning and Reproducibility

| Version | Change | Date | Owner |
| --- | --- | --- | --- |
| v1.0 | Initial preprocessing specification | [Enter] | [Enter] |
| v1.1 | [Future change] | [Enter] | [Enter] |
| v2.0 | [Major pipeline revision] | [Enter] | [Enter] |

## 31. Acceptance Checklist

☐ Raw frames/videos can be processed successfully.

☐ Landmarks are extracted consistently.

☐ Normalization is documented and reproducible.

☐ Feature dimensions are fixed.

☐ Temporal features are correctly ordered.

☐ Missing-data handling is defined.

☐ Training and inference use the same preprocessing logic.

☐ No test-data leakage occurs.

☐ Model-ready tensors contain no invalid numeric values.

☐ Real-time preprocessing meets application latency requirements.

## 32. Editable Project Parameters

| Parameter | Value |
| --- | --- |
| Dataset version | [Enter] |
| MediaPipe version | [Enter] |
| OpenCV version | [Enter] |
| Input resolution | [Enter] |
| Input FPS | [Enter] |
| Sequence length | [Enter] |
| Landmarks used | [Enter] |
| Normalization method | [Enter] |
| Temporal features | [Enter] |
| Smoothing method | [Enter] |
| Missing-data strategy | [Enter] |
| Feature dimension | [Enter] |
| Preprocessing version | v1.0 |

## 33. Dependencies on Other Documents

- 01_Project_PRD – project objectives and feature scope.
- 02_SRS – functional and non-functional requirements.
- 03_System_Architecture – overall data and model pipeline.
- 04_Dataset_Specification – source data, labels, splits, and metadata.
- 05_AI_Model_Specification – model input/output and architecture requirements.
- 07_API_Contract – interface between preprocessing/model services and application.
## 34. Approval

| Role | Name | Signature | Date |
| --- | --- | --- | --- |
| AI/ML Lead | [Enter name] | ________________ | ____________ |
| Data/Preprocessing Lead | [Enter name] | ________________ | ____________ |
| Project Lead | [Enter name] | ________________ | ____________ |
| Project Guide | [Enter name] | ________________ | ____________ |
