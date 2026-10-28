"""
Detailed technical content for the SignBridge AI Final Project Report.
Contains academic text, table specifications, equation descriptions, and references.
"""

FRONT_MATTER = {
    "title": "SIGNBRIDGE AI",
    "subtitle": "AI-POWERED REAL-TIME SIGN LANGUAGE TRANSLATION FOR SEAMLESS TWO-WAY COMMUNICATION",
    "course": "23ECP401 PROJECT IV",
    "degree": "BACHELOR OF ENGINEERING",
    "department": "ELECTRONICS AND COMMUNICATION ENGINEERING",
    "institution": "SNS COLLEGE OF TECHNOLOGY",
    "institution_sub": "(An Autonomous Institution)",
    "location": "Kurumbapalayam (PO), Coimbatore – 641107",
    "date": "OCTOBER 2026",
    "students": [
        ("AKILAN S", "713323EC003"),
        ("ARUTHRA SM", "713323EC005"),
        ("DEEPAK RAJ JS", "713323EC008"),
        ("GOWTHAMAN KL", "713323EC017")
    ],
    "guide_title": "PROJECT GUIDE",
    "guide_dept": "Department of Electronics and Communication Engineering,\nSNS College of Technology, Coimbatore – 641107.",
    "hod_title": "HEAD OF THE DEPARTMENT",
    "hod_dept": "Department of Electronics and Communication Engineering,\nSNS College of Technology, Coimbatore – 641107."
}

ABSTRACT_TEXT = (
    "Indian Sign Language (ISL) serves as the primary and most vital communication medium for an estimated 18 million "
    "deaf and hard-of-hearing individuals across India. However, because over 98% of the hearing population possesses no "
    "formal training in sign language, severe communication divides persist in essential daily activities—spanning education, "
    "workplace collaboration, administrative services, emergency response, and clinical healthcare consultations. Professional "
    "human interpreters are severely scarce, geographically concentrated in major urban centers, and financially cost-prohibitive "
    "for spontaneous everyday interactions. Concurrently, prior automated recognition systems have predominantly relied on "
    "invasive sensory hardware such as electronic data gloves, acoustic sleeves, or specialized infrared depth cameras, which "
    "impose substantial economic burdens, physical encumbrance, and logistical friction on signers.\n\n"
    "To resolve these foundational barriers, this project presents SignBridge AI, a non-invasive, camera-based, end-to-end "
    "Indian Sign Language recognition and bidirectional communication platform. Operating entirely with commodity consumer "
    "RGB webcams and laptop cameras, the system deploys an edge-assisted architecture utilizing Google MediaPipe Holistic and "
    "Tasks-Vision frameworks executing on-device via WebAssembly (Wasm) and WebGL acceleration at 30+ frames per second. "
    "Rather than streaming high-bandwidth raw pixel video to cloud infrastructure—which incurs severe privacy vulnerabilities "
    "and latency spikes—the client extracts 21 three-dimensional skeletal anatomical keypoints per hand. The raw coordinates "
    "undergo deterministic wrist-relative spatial translation, bounding-box scale normalization, and least-active-hand-first "
    "canonicalization, conferring rigorous mathematical invariance to camera distance, signer body proportions, and hand dominance.\n\n"
    "These spatial coordinates are combined with instantaneous joint velocity magnitudes and structural handshape bounding metrics, "
    "generating a rich 189-dimensional temporal feature vector per frame. Sequences are sampled across a uniform 45-frame sliding window "
    "and classified by a deployed 3-way deep learning ensemble (`SBAI-MDL-ISL-4.0.0`) comprising a 2-layer stacked Long Short-Term "
    "Memory (LSTM-128/64) network, a 2-layer stacked Gated Recurrent Unit (GRU-128/64) network, and a mirrored test-time augmentation "
    "(mirror-TTA) branch over a comprehensive 109-class ISL vocabulary (`ISL_001`–`ISL_109`). Evaluated on a frozen, strictly "
    "signer-independent benchmark dataset of 14,826 sequences (SPLIT-4.0), the system achieves an overall test accuracy of 81.29%, "
    "macro precision of 81.90%, macro recall of 81.22%, and macro F1-score of 80.79% across 3,629 unseen test sequences performed by "
    "disjoint signers, operating with a median CPU inference latency of 374.85 ms. The recognized signs are automatically composed into "
    "coherent English sentences through Google Gemini 2.0 Flash AI and vocalized via the HTML5 Web Speech API, with an integrated "
    "reverse Text-to-Sign dictionary channel establishing complete, two-way conversational parity."
)

KEYWORDS = "Indian Sign Language, Sign Language Recognition, Computer Vision, MediaPipe Holistic, Gated Recurrent Unit (GRU), Long Short-Term Memory (LSTM), Deep Neural Ensembles, Human–Computer Interaction, WebAssembly, Assistive Technology."
