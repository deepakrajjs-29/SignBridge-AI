---
license: mit
pretty_name: Indian Sign Language Dictionary (H265 Re-encoded)
task_categories:
- video-classification
annotations_creators:
- expert-generated
source_datasets:
- government
language:
- en
multilinguality: monolingual
size_categories:
- 10K<n<100K
modality:
- video
tags:
- isl
- sign
- sign language
- video
- dataset
---
# Indian_Sign_Language_Data.gov_Rencoded

## Dataset Overview

**Dataset name:** Indian_Sign_Language_Data.gov_Rencoded  
**Hugging Face repository:** silentone0725/Indian_Sign_Language_Data.gov_Rencoded  
**Modality:** Video (H.265 / HEVC)  
**Total size:** ~75 GB  
**Original size:** ~200 GB  
**Language:** Indian Sign Language (ISL)  
**License:** MIT  

This dataset is a re-encoded and curated version of the *Indian Sign Language Dictionary* originally published on the Government of India Open Data Portal (data.gov.in). The primary goal of this release is to significantly reduce storage requirements while preserving visual quality, and to improve structural consistency for machine learning and research use.

---

## Source Dataset

**Original source:**  
Indian Sign Language Dictionary (till January 2024)  
Published by the Indian Sign Language Research and Training Centre (ISLRTC), Government of India  
Hosted on: https://www.data.gov.in/resource/indian-sign-language-dictionary-till-january-2024

The original dataset consists of thousands of short video clips demonstrating isolated Indian Sign Language signs for words, alphabets, and numbers.

---

## Processing and Modifications

The following processing steps were applied to create this dataset:

1. **Video re-encoding**
   - All videos were re-encoded to **H.265 (HEVC)**.
   - Encoding was performed with minimal perceptual quality loss.
   - Dataset size was reduced from approximately **200 GB to 75 GB**.

2. **Conflict resolution for similar words**
   - Duplicate or semantically overlapping word entries were reviewed.
   - Similar-word disputes were resolved to avoid redundant or ambiguous samples.

3. **Structural reorganization**
   - Videos were grouped primarily by:
     - Alphabets (A–Z)
     - Numbers (0–9)
   - This grouping is intended to simplify dataset navigation and isolated-sign training workflows.

4. **Format standardization**
   - File naming and directory structure were normalized where possible.
   - Metadata is provided in Hugging Face-compatible formats.

---

## Dataset Structure

The dataset is organized as follows:

- Alphabet-based directories containing sign videos for individual letters
- Number-based directories containing sign videos for digits
- Additional vocabulary entries derived from the original dictionary
- Hugging Face dataset metadata (Parquet format)

This structure is suitable for isolated sign classification and preprocessing pipelines.

---

## Intended Use

This dataset is intended for:

- Indian Sign Language (ISL) research
- Video-based sign language recognition
- Computer vision and deep learning experiments
- Accessibility and assistive technology development
- Educational and academic purposes

---

## Limitations

- This dataset focuses on **isolated signs**, not continuous sign language sentences.
- Compression artifacts may exist due to H.265 encoding; users should evaluate suitability for fine-grained motion analysis tasks.
- Metadata completeness depends on the original source and available annotations.

---

## Ethical Considerations

- The dataset contains videos of human signers; users should ensure respectful and ethical usage.
- The data should not be used for surveillance, profiling, or harmful applications.
- Users are responsible for complying with the original data source’s usage policies.

---

## Citation

If you use this dataset in academic or research work, please cite both:

1. The original Indian Sign Language Dictionary dataset from data.gov.in
2. This re-encoded Hugging Face dataset repository

---

## Acknowledgements

- Indian Sign Language Research and Training Centre (ISLRTC)
- Government of India Open Data Initiative
- Hugging Face Datasets community

---

## Contact

For issues, improvements, or questions, please use the Hugging Face repository discussion or issues section.