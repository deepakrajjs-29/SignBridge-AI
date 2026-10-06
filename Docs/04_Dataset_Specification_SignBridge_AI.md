<!-- Source: 04_Dataset_Specification_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# DATASET SPECIFICATION

## SignBridge AI – Indian Sign Language (ISL) Recognition System

| Field | Details |
| --- | --- |
| Document ID | 04_Dataset_Specification |
| Project | SignBridge AI |
| Document Type | Dataset Specification |
| Version | 1.0 |
| Status | Draft / Editable |
| Prepared For | SignBridge AI Development Team |
| Primary Domain | Computer Vision, AI/ML, Indian Sign Language |

## 1. Purpose

This document defines the requirements, structure, collection strategy, annotation standards, preprocessing requirements, storage format, quality controls, and dataset splits for the SignBridge AI Indian Sign Language recognition system. It is intended to provide a consistent specification for building a reliable dataset for model training, validation, testing, and future expansion.

## 2. Dataset Objectives

- Build a representative dataset for real-time Indian Sign Language recognition from camera/video input.
- Capture both spatial hand information and temporal motion information for dynamic signs.
- Support signer-independent training and evaluation to reduce overfitting to individual users.
- Provide standardized labels and metadata for reproducible AI/ML experiments.
- Allow future expansion to additional ISL signs, words, phrases, and continuous sign sequences.
## 3. Dataset Scope

| Component | Specification |
| --- | --- |
| Primary input | RGB video / webcam frames |
| Recognition type | Static and dynamic ISL sign recognition |
| Language | Indian Sign Language (ISL) |
| Primary modality | Vision-based hand/body movement |
| Optional derived modality | Hand landmarks, pose landmarks, face landmarks, frame-level features |
| Target environment | Real-time webcam/mobile/website application |
| Model usage | Training, validation, testing and benchmarking |
| Future scope | Continuous sign recognition and sentence-level recognition |

## 4. Dataset Composition

The dataset should contain samples representing the target ISL vocabulary. Each sample should preserve the temporal order of frames when the sign contains motion.

| Dataset Element | Recommended Specification | Editable Project Value |
| --- | --- | --- |
| Number of classes | Define target vocabulary | [Enter value] |
| Samples per class | Prefer balanced distribution | [Enter value] |
| Total samples/videos | Based on class count and collection capacity | [Enter value] |
| Number of signers | Multiple signers; target at least 15–30 where feasible | [Enter value] |
| Age groups | Diverse adult participants; document actual range | [Enter range] |
| Gender diversity | Include available participant diversity | [Enter details] |
| Backgrounds | Plain + natural backgrounds | [Enter details] |
| Lighting conditions | Indoor varied lighting; controlled and natural | [Enter details] |
| Camera viewpoints | Primarily frontal; optional mild variation | [Enter details] |
| Resolution | Prefer 720p or higher source capture | [Enter resolution] |
| Frame rate | Prefer 24–30 FPS | [Enter FPS] |

## 5. Class / Label Specification

Every sample must have one authoritative class label for isolated-sign recognition. Labels should be stable, unique, human-readable, and mapped to an internal class ID.

| Field | Description | Example |
| --- | --- | --- |
| class_id | Unique numeric/string identifier | ISL_001 |
| label | Canonical sign name | Hello |
| gloss | Standardized gloss if used | HELLO |
| sign_type | Static or dynamic | Dynamic |
| meaning | English meaning/description | Greeting |
| handedness | Left / right / both / variable | Both |
| notes | Special collection instructions | Requires upper-body motion |

## 6. Sample-Level Metadata

| Metadata Field | Required | Description |
| --- | --- | --- |
| sample_id | Yes | Unique identifier for each sample |
| class_id | Yes | Target class identifier |
| label | Yes | Canonical sign label |
| signer_id | Yes | Anonymized participant identifier |
| session_id | Yes | Collection session identifier |
| sequence_id | Yes | Video/sequence identifier |
| capture_date | Recommended | Date of data collection |
| camera_id | Recommended | Anonymized device/camera identifier |
| resolution | Recommended | Source video/image resolution |
| fps | Recommended | Source frame rate |
| environment | Yes | Indoor/outdoor/background category |
| lighting | Yes | Lighting category |
| handedness | Recommended | Dominant/visible hand configuration |
| quality_flag | Yes | Accepted / review / rejected |
| annotation_status | Yes | Pending / verified |

## 7. Data Collection Protocol

1. Define the approved ISL vocabulary and class IDs before collection.

2. Recruit multiple signers and assign anonymized signer IDs.

3. Record each sign multiple times using consistent instructions.

4. Capture natural variation in speed, position, distance, and execution while avoiding extreme unusable samples.

5. Record samples under multiple reasonable lighting and background conditions.

6. Ensure hands and relevant upper-body regions remain visible.

7. Store raw recordings separately from processed/derived data.

8. Review recordings and remove corrupted, duplicated, severely occluded, or incorrectly performed samples.

## 8. Data Format and Directory Structure

Recommended project structure:

dataset/
├── raw/
│   ├── videos/
│   └── images/
├── processed/
│   ├── frames/
│   ├── landmarks/
│   └── features/
├── annotations/
│   ├── labels.csv
│   ├── metadata.csv
│   └── splits.csv
├── train/
├── validation/
├── test/
└── documentation/

## 9. Frame and Sequence Configuration

| Parameter | Recommended Value | Project Value |
| --- | --- | --- |
| Input sequence length | Fixed length such as 30–60 frames | [Enter value] |
| Frame sampling | Uniform sampling / temporal normalization | [Enter method] |
| Image size | Model-dependent, e.g. 224×224 or 256×256 | [Enter value] |
| Color format | RGB | [Enter value] |
| Padding strategy | Temporal padding/repetition if required | [Enter method] |
| Maximum sequence duration | Define based on target signs | [Enter value] |
| Minimum valid frames | Enough frames to represent sign | [Enter value] |

## 10. Landmark and Feature Extraction

Where MediaPipe or a comparable landmark detector is used, derived features should be stored separately from raw video. The dataset may contain hand, pose, and facial landmarks depending on the model design.

| Feature Group | Typical Data | Purpose |
| --- | --- | --- |
| Left hand | 21 landmarks × (x, y, z) | Hand shape and movement |
| Right hand | 21 landmarks × (x, y, z) | Hand shape and movement |
| Pose | Selected body landmarks | Upper-body movement/context |
| Face | Selected facial landmarks | Optional non-manual features |
| Temporal features | Velocity/displacement/angles | Motion representation |
| Normalized features | Relative coordinates | Reduce camera/person variation |

## 11. Annotation Guidelines

- Use one canonical label for each target sign.
- Verify that the performed sign matches the intended class.
- Mark ambiguous or incorrectly performed samples for review rather than forcing a label.
- Preserve sequence order for dynamic signs.
- Record signer and session metadata without exposing personally identifiable information.
- Use at least one independent verification pass for the final evaluation set.
## 12. Data Preprocessing Requirements

| Stage | Operation | Requirement |
| --- | --- | --- |
| Quality check | Corrupt/invalid sample removal | Mandatory |
| Frame extraction | Convert video to frame sequence | As required |
| Resize | Standardize input dimensions | Mandatory for image models |
| Normalization | Coordinate/pixel normalization | Model dependent |
| Landmark extraction | MediaPipe/other detector | Recommended |
| Temporal normalization | Standardize sequence length | Recommended |
| Augmentation | Controlled spatial/temporal variation | Training only |
| Deduplication | Remove near-duplicate samples | Mandatory |

## 13. Data Augmentation

Augmentation should improve robustness without changing the semantic identity of the sign.

- Small spatial translation and scaling.
- Moderate brightness/contrast variation.
- Limited rotation where it does not alter sign meaning.
- Temporal speed variation for dynamic signs.
- Frame dropping or interpolation within controlled limits.
- Background variation where appropriate.
Avoid aggressive transformations that could distort hand orientation or change the intended ISL sign.

## 14. Train / Validation / Test Split

The split must be performed at signer level wherever possible. The same signer should not appear in both training and final testing data, because this can produce overly optimistic results.

| Split | Recommended Ratio | Purpose |
| --- | --- | --- |
| Training | 70% | Model learning |
| Validation | 15% | Hyperparameter tuning and model selection |
| Testing | 15% | Final unbiased evaluation |

Alternative ratios may be used when dataset size requires it, but the selected split must be documented and fixed before final evaluation.

## 15. Data Leakage Prevention

- Keep signer identities separated across train, validation, and test sets.
- Do not place consecutive duplicate recordings from the same session into different splits.
- Fit normalization/statistical parameters only on training data when applicable.
- Do not tune the final model repeatedly against the test set.
- Maintain a fixed, versioned test set for final reporting.
## 16. Dataset Quality Criteria

| Quality Check | Acceptance Criterion |
| --- | --- |
| Label correctness | Sample clearly matches assigned sign |
| Visibility | Hands and required body regions are sufficiently visible |
| Video integrity | No corruption or severe frame loss |
| Class balance | No uncontrolled extreme class imbalance |
| Metadata completeness | Required fields are populated |
| Duplicate control | No accidental duplicate samples across splits |
| Annotation verification | Critical labels reviewed |
| Privacy | No unnecessary personally identifiable information stored |

## 17. Dataset Versioning

| Version | Change Description | Date | Owner |
| --- | --- | --- | --- |
| v1.0 | Initial dataset specification | 2026-09-27 | [Enter name] |
| v1.1 | [Future changes] | [Enter date] | [Enter name] |
| v2.0 | [Major dataset revision] | [Enter date] | [Enter name] |

## 18. Dataset Naming Convention

Recommended sample naming pattern:

**CLASSID_SIGNERID_SESSIONID_SEQUENCEID.ext**

Example: ISL_001_S003_SE02_Q015.mp4

## 19. Storage and Backup Requirements

- Maintain a read-only copy of raw recordings after verification.
- Store processed data separately from raw data.
- Use version control or dataset version manifests for labels and splits.
- Maintain at least one backup of important raw and annotated data.
- Restrict access to participant-related metadata.
## 20. Dataset Deliverables

- Raw video/image collection.
- Cleaned and validated dataset.
- Class label mapping.
- Sample metadata file.
- Train/validation/test split file.
- Processed frame sequences.
- Landmark/feature files, if used.
- Dataset README and collection/annotation guidelines.
- Dataset version manifest and change log.
## 21. Dataset Acceptance Checklist

☐ Target classes are finalized.

☐ All samples have unique IDs.

☐ Labels have been verified.

☐ Signer IDs are anonymized.

☐ Required metadata is complete.

☐ Invalid/corrupt samples have been removed.

☐ Duplicates have been checked.

☐ Train/validation/test splits are documented.

☐ No signer leakage exists across evaluation boundaries.

☐ Preprocessing pipeline is reproducible.

☐ Dataset version is recorded.

☐ Backup is available.

## 22. Editable Project Parameters

| Parameter | Current Value |
| --- | --- |
| Dataset name | [Enter dataset name] |
| Number of ISL classes | [Enter value] |
| Total samples/videos | [Enter value] |
| Number of signers | [Enter value] |
| Frames per sequence | [Enter value] |
| Input resolution | [Enter value] |
| Frame rate | [Enter value] |
| Train split | 70% |
| Validation split | 15% |
| Test split | 15% |
| Landmark framework | MediaPipe / [Confirm] |
| Storage format | MP4 / JPG/PNG / CSV/JSON / [Confirm] |
| Dataset version | v1.0 |
| Dataset owner | [Enter name/team] |

## 23. References / Supporting Documents

- 01_Project_PRD – SignBridge AI
- 02_SRS – SignBridge AI
- 03_System_Architecture – SignBridge AI
- 05_AI_Model_Specification – SignBridge AI
- 06_Preprocessing_Feature_Engineering – SignBridge AI
## 24. Approval

| Role | Name | Signature | Date |
| --- | --- | --- | --- |
| Project Lead | [Enter name] | ________________ | ____________ |
| Dataset Lead | [Enter name] | ________________ | ____________ |
| Technical Reviewer | [Enter name] | ________________ | ____________ |
| Project Guide | [Enter name] | ________________ | ____________ |
