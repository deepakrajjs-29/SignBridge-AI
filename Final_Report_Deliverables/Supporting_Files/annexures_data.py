"""
Annexures content for SignBridge AI Final Project Report.
Contains production source code excerpts, complete 109-class vocabulary table,
and deployment configuration runbook.
"""

ANNEXURE_A_INTRO = (
    "This annexure provides core production source code modules demonstrating the end-to-end "
    "implementation of SignBridge AI. The excerpts showcase client-side landmark extraction, "
    "server-side mathematical normalization, 189-dimensional temporal feature engineering, "
    "recurrent neural network architectures, and asynchronous streaming microservices."
)

CODE_MODULE_1 = {
    "title": "Module A.1: Landmark Normalization and Canonicalization (ai/preprocessing/landmarks.py)",
    "code": '''import numpy as np

def normalize_hand_landmarks(landmarks: np.ndarray) -> np.ndarray:
    """
    Performs wrist translation centering, bounding-box scale normalization,
    and least-active-hand-first canonicalization on 3D hand keypoints.
    
    Args:
        landmarks: Array of shape (2, 21, 3) representing 2 hands x 21 joints x (x, y, z).
    Returns:
        Canonicalized and normalized landmark array of shape (2, 21, 3).
    """
    normalized = np.copy(landmarks)
    
    # Stage 1: Wrist-Relative Translation Centering
    for h in range(2):
        wrist = normalized[h, 0, :].copy()
        if not np.all(wrist == 0.0):
            normalized[h] = normalized[h] - wrist

    # Stage 2: Bounding-Box Scale Normalization (Euclidean Hypersphere)
    for h in range(2):
        dists = np.linalg.norm(normalized[h], axis=-1)
        max_dist = np.max(dists)
        if max_dist > 1e-6:
            normalized[h] = normalized[h] / max_dist

    # Stage 3: Canonical Hand Slot Assignment
    # Compute active joint variance to ensure dominant hand occupies Slot 0
    h0_energy = np.var(normalized[0])
    h1_energy = np.var(normalized[1])
    if h1_energy > h0_energy and h0_energy < 1e-5:
        normalized[[0, 1]] = normalized[[1, 0]]

    return normalized
'''
}

CODE_MODULE_2 = {
    "title": "Module A.2: 189-Dimensional Feature Vector Construction (ai/features/build.py)",
    "code": '''import numpy as np

def build_frame_feature_vector(current_landmarks: np.ndarray, 
                               prev_landmarks: np.ndarray) -> np.ndarray:
    """
    Constructs the deterministic 189-dimensional feature vector per frame:
    - 126 coordinates: 2 hands x 21 joints x 3 dimensions (x, y, z)
    - 42 velocity magnitudes: 2 hands x 21 joints x 1 Euclidean scalar
    - 12 bounding box dimensions: min/max bounds for both hands
    - 9 palm geometry metrics: centroids and palm span distances
    """
    # 1. Normalized spatial coordinates (126 dims)
    coords = current_landmarks.flatten()

    # 2. Instantaneous velocity magnitudes (42 dims)
    velocities = np.linalg.norm(current_landmarks - prev_landmarks, axis=-1).flatten()

    # 3. Spatial bounding box bounds (12 dims: 2 hands x [xmin, ymin, zmin, xmax, ymax, zmax])
    bboxes = []
    for h in range(2):
        h_pts = current_landmarks[h]
        min_pt = np.min(h_pts, axis=0)
        max_pt = np.max(h_pts, axis=0)
        bboxes.extend([min_pt[0], min_pt[1], min_pt[2], max_pt[0], max_pt[1], max_pt[2]])
    bboxes = np.array(bboxes, dtype=np.float32)

    # 4. Hand centroids and palm opening spans (9 dims)
    geom = []
    for h in range(2):
        centroid = np.mean(current_landmarks[h], axis=0)
        thumb_tip = current_landmarks[h, 4]
        pinky_tip = current_landmarks[h, 20]
        span = np.linalg.norm(thumb_tip - pinky_tip)
        geom.extend([centroid[0], centroid[1], centroid[2], span])
    geom.append(np.linalg.norm(np.mean(current_landmarks[0], axis=0) - 
                               np.mean(current_landmarks[1], axis=0)))
    geom = np.array(geom, dtype=np.float32)

    feature_189 = np.concatenate([coords, velocities, bboxes, geom])
    assert feature_189.shape[0] == 189, f"Expected 189 dims, got {feature_189.shape[0]}"
    return feature_189
'''
}

CODE_MODULE_3 = {
    "title": "Module A.3: Stacked Deep Recurrent Neural Architecture (ai/models/lstm.py)",
    "code": '''import tensorflow as tf
from tensorflow.keras import layers, models

def create_recurrent_classifier(seq_len: int = 45, feat_dim: int = 189, 
                                num_classes: int = 109, rnn_type: str = "gru") -> models.Model:
    """
    Builds the production recurrent neural network architecture for ISL classification.
    Supports either stacked Gated Recurrent Units (GRU) or Long Short-Term Memory (LSTM).
    """
    inputs = layers.Input(shape=(seq_len, feat_dim), name="feature_sequence_input")
    x = layers.Masking(mask_value=0.0)(inputs)

    if rnn_type.lower() == "gru":
        x = layers.GRU(128, return_sequences=True, recurrent_dropout=0.1, name="gru_layer_1")(x)
        x = layers.BatchNormalization(name="bn_1")(x)
        x = layers.GRU(64, return_sequences=False, recurrent_dropout=0.1, name="gru_layer_2")(x)
    else:
        x = layers.LSTM(128, return_sequences=True, recurrent_dropout=0.1, name="lstm_layer_1")(x)
        x = layers.BatchNormalization(name="bn_1")(x)
        x = layers.LSTM(64, return_sequences=False, recurrent_dropout=0.1, name="lstm_layer_2")(x)

    x = layers.BatchNormalization(name="bn_2")(x)
    x = layers.Dense(64, activation="relu", name="projection_dense")(x)
    x = layers.Dropout(0.35, name="regularization_dropout")(x)
    outputs = layers.Dense(num_classes, activation="softmax", dtype="float32", name="predictions")(x)

    model = models.Model(inputs=inputs, outputs=outputs, name=f"SBAI_{rnn_type.upper()}_Model")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model
'''
}

CODE_MODULE_4 = {
    "title": "Module A.4: Asynchronous WebSocket Streaming Router (backend/app/routers/stream.py)",
    "code": '''from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import numpy as np
import json
import logging

router = APIRouter(tags=["stream"])
logger = logging.getLogger("signbridge.stream")

@router.websocket("/ws/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = websocket.headers.get("sec-websocket-key", "anonymous")
    logger.info("WebSocket connected: %s", session_id)
    
    sequence_buffer = []
    
    try:
        while True:
            raw_text = await websocket.receive_text()
            data = json.loads(raw_text)
            landmarks = np.array(data.get("landmarks", []), dtype=np.float32)
            
            # Feature extraction and rolling window accumulation
            if landmarks.shape == (2, 21, 3):
                norm_feat = process_frame(landmarks)
                sequence_buffer.append(norm_feat)
                
                if len(sequence_buffer) > 45:
                    sequence_buffer.pop(0)
                    
                if len(sequence_buffer) == 45:
                    pred = run_ensemble_inference(np.array([sequence_buffer]))
                    if pred["confidence"] >= 0.60 and pred["margin"] >= 0.15:
                        await websocket.send_text(json.dumps({
                            "status": "ACCEPTED",
                            "sign": pred["gloss"],
                            "confidence": round(float(pred["confidence"]), 4)
                        }))
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s", session_id)
'''
}

CODE_MODULE_5 = {
    "title": "Module A.5: Client-Side Landmark Preprocessing & Normalization (frontend/src/landmarks.ts)",
    "code": '''export interface Landmark3D {
  x: number;
  y: number;
  z: number;
}

export function normalizeLandmarksClient(
  hands: [Landmark3D[], Landmark3D[]]
): Float32Array {
  const output = new Float32Array(126); // 2 hands x 21 joints x 3 coords
  
  hands.forEach((hand, hIdx) => {
    if (!hand || hand.length < 21) return;
    
    // Translation centering relative to wrist (index 0)
    const wrist = hand[0];
    const centered = hand.map(pt => ({
      x: pt.x - wrist.x,
      y: pt.y - wrist.y,
      z: pt.z - wrist.z
    }));
    
    // Scale normalization by maximum Euclidean distance
    let maxDist = 0;
    centered.forEach(pt => {
      const d = Math.sqrt(pt.x * pt.x + pt.y * pt.y + pt.z * pt.z);
      if (d > maxDist) maxDist = d;
    });
    
    const scale = maxDist > 1e-6 ? maxDist : 1.0;
    centered.forEach((pt, k) => {
      const baseIdx = hIdx * 63 + k * 3;
      output[baseIdx] = pt.x / scale;
      output[baseIdx + 1] = pt.y / scale;
      output[baseIdx + 2] = pt.z / scale;
    });
  });
  
  return output;
}
'''
}

VOCAB_CATEGORIES = [
    ("ISL_001", "HELLO", "Greetings & Courtesies", "Single Hand Wave / Open Palm", "High (Initial Salutation)"),
    ("ISL_002", "THANK YOU", "Greetings & Courtesies", "Chin to Forward Open Palm", "High (Social Politeness)"),
    ("ISL_003", "PLEASE", "Greetings & Courtesies", "Circular Chest Rub", "High (Requests & Civility)"),
    ("ISL_004", "WELCOME", "Greetings & Courtesies", "Inward Sweeping Open Hand", "Moderate (Hospitality)"),
    ("ISL_005", "GOODBYE", "Greetings & Courtesies", "Hand Wave Lateral Motion", "High (Departure)"),
    ("ISL_006", "SORRY", "Greetings & Courtesies", "Fist Rotation on Chest", "High (Apology / Remediation)"),
    ("ISL_007", "GOOD MORNING", "Greetings & Courtesies", "Rising Sun Gesture + Good", "Moderate (Daily Greeting)"),
    ("ISL_008", "GOOD NIGHT", "Greetings & Courtesies", "Descending Hand Arc + Good", "Moderate (Evening Parting)"),
    ("ISL_009", "YES", "Greetings & Courtesies", "Fist Nodding Vertical Action", "Critical (Binary Affirmation)"),
    ("ISL_010", "NO", "Greetings & Courtesies", "Index and Middle Snap on Thumb", "Critical (Binary Negation)"),
    ("ISL_011", "HOW ARE YOU", "Greetings & Courtesies", "Chest Palms Up Turn Forward", "High (Inquiry)"),
    ("ISL_012", "I AM FINE", "Greetings & Courtesies", "Five Hand Tap on Chest", "High (Health Status)"),
    ("ISL_013", "NICE TO MEET YOU", "Greetings & Courtesies", "Slide Palms + Point Together", "Moderate (Introduction)"),
    ("ISL_014", "SEE YOU LATER", "Greetings & Courtesies", "V-Fingers to Eye + Forward", "Moderate (Parting)"),
    ("ISL_015", "HELP", "Emergency & Medical", "Fist on Flat Palm Lift Up", "CRITICAL (Immediate Distress)"),
    ("ISL_016", "EMERGENCY", "Emergency & Medical", "E-Hand Shake Lateral Alert", "CRITICAL (Life-Safety Alert)"),
    ("ISL_017", "HOSPITAL", "Emergency & Medical", "Cross Touch on Shoulder", "CRITICAL (Medical Transport)"),
    ("ISL_018", "DOCTOR", "Emergency & Medical", "Fingers Tap Radial Pulse", "CRITICAL (Clinical Triage)"),
    ("ISL_019", "NURSE", "Emergency & Medical", "Thumb Cross Trace on Wrist", "High (Inpatient Care)"),
    ("ISL_020", "MEDICINE", "Emergency & Medical", "Middle Finger Swirl on Palm", "High (Prescription Fulfillment)"),
    ("ISL_021", "PAIN", "Emergency & Medical", "Index Points Twist Toward Site", "CRITICAL (Symptom Assessment)"),
    ("ISL_022", "FEVER", "Emergency & Medical", "Back of Hand on Forehead", "High (Diagnostic Triage)"),
    ("ISL_023", "ACCIDENT", "Emergency & Medical", "Fists Crash Together Inward", "CRITICAL (First-Responder Call)"),
    ("ISL_024", "AMBULANCE", "Emergency & Medical", "Rotating Overhead Flashing Hand", "CRITICAL (Emergency Dispatch)"),
    ("ISL_025", "POLICE", "Emergency & Medical", "C-Hand Tap on Chest/Cap", "CRITICAL (Security / Legal)"),
    ("ISL_026", "FIRE", "Emergency & Medical", "Wiggling Fingers Rising Up", "CRITICAL (Evacuation Alert)"),
    ("ISL_027", "DANGER", "Emergency & Medical", "Hands Thrust Back Warning", "CRITICAL (Hazard Warning)"),
    ("ISL_028", "BLOOD", "Emergency & Medical", "Red Sign + Flowing Downward", "CRITICAL (Trauma Assessment)"),
    ("ISL_029", "BREATHE", "Emergency & Medical", "Dual Palms Expand/Contract", "CRITICAL (Respiratory Distress)"),
    ("ISL_030", "HEART", "Emergency & Medical", "Middle Finger Tap Left Chest", "CRITICAL (Cardiac Emergency)"),
    ("ISL_031", "WATER", "Daily Life & Family", "W-Hand Tap on Chin", "High (Hydration / Sustenance)"),
    ("ISL_032", "FOOD", "Daily Life & Family", "Fingers Flattened to Mouth", "High (Nutrition)"),
    ("ISL_033", "HUNGRY", "Daily Life & Family", "C-Hand Slide Down Sternum", "Moderate (Daily Needs)"),
    ("ISL_034", "THIRSTY", "Daily Life & Family", "Index Finger Down Throat", "Moderate (Daily Needs)"),
    ("ISL_035", "SLEEP", "Daily Life & Family", "Hand Draw Down Over Face", "Moderate (Rest / Wellness)"),
    ("ISL_036", "FAMILY", "Daily Life & Family", "F-Hands Circle to Join", "High (Social Support)"),
    ("ISL_037", "MOTHER", "Daily Life & Family", "Thumb Tap on Chin", "High (Kinship Relations)"),
    ("ISL_038", "FATHER", "Daily Life & Family", "Thumb Tap on Forehead", "High (Kinship Relations)"),
    ("ISL_039", "BROTHER", "Daily Life & Family", "L-Hands Meet Forearms", "High (Kinship Relations)"),
    ("ISL_040", "SISTER", "Daily Life & Family", "L-Hand From Jaw to Meet", "High (Kinship Relations)"),
    ("ISL_041", "FRIEND", "Daily Life & Family", "Interlocking Index Hooks", "High (Interpersonal Bond)"),
    ("ISL_042", "HOME", "Daily Life & Family", "Flat Hands Form Peaked Roof", "High (Shelter / Residence)"),
    ("ISL_043", "TIME", "Daily Life & Family", "Index Finger Tap on Wrist", "High (Scheduling / Travel)"),
    ("ISL_044", "TODAY", "Daily Life & Family", "Y-Hands Drop Downward Twice", "High (Temporal Reference)"),
    ("ISL_045", "TOMORROW", "Daily Life & Family", "A-Hand Thumb Push Forward", "High (Temporal Reference)"),
    ("ISL_046", "YESTERDAY", "Daily Life & Family", "A-Hand Thumb Arc Backward", "High (Temporal Reference)"),
    ("ISL_047", "MONEY", "Daily Life & Family", "Thumb Rub on Fingertips", "High (Commerce / Banking)"),
    ("ISL_048", "BATHROOM", "Daily Life & Family", "T-Hand Lateral Shake", "High (Sanitation / Personal)"),
    ("ISL_049", "WHERE", "Daily Life & Family", "Index Waggle Side to Side", "High (Wayfinding Question)"),
    ("ISL_050", "WHAT", "Daily Life & Family", "Open Palms Shrug Shake", "High (Inquiry / Clarification)"),
    ("ISL_051", "WHEN", "Daily Life & Family", "Index Circles and Touches Tip", "High (Scheduling Inquiry)"),
    ("ISL_052", "WHY", "Daily Life & Family", "Hand From Forehead to Y-Hand", "High (Reasoning Question)"),
    ("ISL_053", "HOW MUCH", "Daily Life & Family", "Fingers Flick Upward", "High (Commercial Pricing)"),
    ("ISL_054", "TIRED", "Daily Life & Family", "Bent Hands Droop on Chest", "Moderate (Physical State)"),
    ("ISL_055", "HAPPY", "Daily Life & Family", "Open Hand Flutters Up Chest", "Moderate (Affective State)"),
    ("ISL_056", "SAD", "Daily Life & Family", "Five Hands Droop Over Face", "Moderate (Affective State)"),
    ("ISL_057", "CLOTHES", "Daily Life & Family", "Hands Brush Down Shirt Front", "Moderate (Personal Belongings)"),
    ("ISL_058", "TELEPHONE", "Daily Life & Family", "Y-Hand to Ear and Mouth", "High (Communication Method)"),
    ("ISL_059", "SCHOOL", "Education & Workplace", "Clap Flat Hands Horizontally", "High (Academic Access)"),
    ("ISL_060", "COLLEGE", "Education & Workplace", "Slide Palm and Arc Upward", "High (Higher Education)"),
    ("ISL_061", "TEACHER", "Education & Workplace", "O-Hands at Temples + Agent", "High (Instructional Role)"),
    ("ISL_062", "STUDENT", "Education & Workplace", "Learn Gesture + Agent Suffix", "High (Academic Role)"),
    ("ISL_063", "BOOK", "Education & Workplace", "Palms Open Like Book Leaves", "High (Learning Material)"),
    ("ISL_064", "WRITE", "Education & Workplace", "Pencil Grip Scribble on Palm", "High (Literacy / Exam)"),
    ("ISL_065", "READ", "Education & Workplace", "V-Fingers Scan Down Palm", "High (Literacy / Exam)"),
    ("ISL_066", "QUESTION", "Education & Workplace", "Index Traces Question Mark", "High (Inquiry / Exam)"),
    ("ISL_067", "ANSWER", "Education & Workplace", "Index Fingers Point Forward", "High (Response / Exam)"),
    ("ISL_068", "COMPUTER", "Education & Workplace", "C-Hand Arc Up Non-Dominant", "High (Digital Literacy)"),
    ("ISL_069", "INTERNET", "Education & Workplace", "Middle Fingers Touch and Pivot", "High (Connectivity)"),
    ("ISL_070", "OFFICE", "Education & Workplace", "O-Hands Form Room Perimeter", "High (Workplace Environment)"),
    ("ISL_071", "JOB", "Education & Workplace", "Fists Tap Wrists Together", "High (Employment)"),
    ("ISL_072", "SALARY", "Education & Workplace", "Hand Slide Palm Inward", "High (Compensation)"),
    ("ISL_073", "MEETING", "Education & Workplace", "All Fingers Meet Across Hands", "High (Collaboration)"),
    ("ISL_074", "PROJECT", "Education & Workplace", "P-Hand to J-Hand on Palm", "High (Academic / Work Task)"),
    ("ISL_075", "ENGINEERING", "Education & Workplace", "Y-Hands Interlock Gears Twist", "High (Discipline of Study)"),
    ("ISL_076", "EXAM", "Education & Workplace", "Dual Hands Flip Down Papers", "High (Evaluation / Academic)"),
    ("ISL_077", "PASS", "Education & Workplace", "Thumbs Up Thrust Forward", "High (Academic Outcome)"),
    ("ISL_078", "FAIL", "Education & Workplace", "V-Hand Slides Off Palm Edge", "High (Academic Outcome)"),
    ("ISL_079", "BUS", "Education & Workplace", "Hands Grip Large Steering Wheel", "High (Public Commute)"),
    ("ISL_080", "TRAIN", "Education & Workplace", "H-Fingers Slide Over H-Fingers", "High (Intercity Travel)"),
    ("ISL_081", "TICKET", "Education & Workplace", "Bent V Clamps Non-Dominant Palm", "High (Transit Authorization)"),
    ("ISL_082", "STATION", "Education & Workplace", "Two Fingers Stand on Flat Palm", "High (Transit Terminal)"),
    ("ISL_083", "GOVERNMENT", "Education & Workplace", "Index Twist Touch Forehead", "High (Civic Administration)"),
    ("ISL_084", "A (ALPHABET)", "ISL Alphabets & Digits", "Closed Fist with Thumb Upright", "Fundamental (Fingerspelling)"),
    ("ISL_085", "B (ALPHABET)", "ISL Alphabets & Digits", "Flat Four Fingers, Thumb Tucked", "Fundamental (Fingerspelling)"),
    ("ISL_086", "C (ALPHABET)", "ISL Alphabets & Digits", "Curved C-Shape Hand Formation", "Fundamental (Fingerspelling)"),
    ("ISL_087", "D (ALPHABET)", "ISL Alphabets & Digits", "Index Up, Thumb Meets Others", "Fundamental (Fingerspelling)"),
    ("ISL_088", "E (ALPHABET)", "ISL Alphabets & Digits", "Curled Fingers Rest on Thumb", "Fundamental (Fingerspelling)"),
    ("ISL_089", "F (ALPHABET)", "ISL Alphabets & Digits", "Index and Thumb Ring, 3 Extended", "Fundamental (Fingerspelling)"),
    ("ISL_090", "G (ALPHABET)", "ISL Alphabets & Digits", "Index and Thumb Parallel Side", "Fundamental (Fingerspelling)"),
    ("ISL_091", "H (ALPHABET)", "ISL Alphabets & Digits", "Index and Middle Parallel Side", "Fundamental (Fingerspelling)"),
    ("ISL_092", "I (ALPHABET)", "ISL Alphabets & Digits", "Pinky Extended Upright Only", "Fundamental (Fingerspelling)"),
    ("ISL_093", "J (ALPHABET)", "ISL Alphabets & Digits", "Pinky Traces J-Shape in Air", "Fundamental (Fingerspelling)"),
    ("ISL_094", "K (ALPHABET)", "ISL Alphabets & Digits", "Index Up, Middle Out, Thumb Joint", "Fundamental (Fingerspelling)"),
    ("ISL_095", "L (ALPHABET)", "ISL Alphabets & Digits", "Index and Thumb Right Angle", "Fundamental (Fingerspelling)"),
    ("ISL_096", "M (ALPHABET)", "ISL Alphabets & Digits", "Thumb Under Three Fingers", "Fundamental (Fingerspelling)"),
    ("ISL_097", "N (ALPHABET)", "ISL Alphabets & Digits", "Thumb Under Two Fingers", "Fundamental (Fingerspelling)"),
    ("ISL_098", "O (ALPHABET)", "ISL Alphabets & Digits", "All Fingers Form O-Shape", "Fundamental (Fingerspelling)"),
    ("ISL_099", "P (ALPHABET)", "ISL Alphabets & Digits", "K-Hand Inverted Downward", "Fundamental (Fingerspelling)"),
    ("ISL_100", "1 (DIGIT)", "ISL Alphabets & Digits", "Index Finger Upright Extended", "Fundamental (Numerical Quantity)"),
    ("ISL_101", "2 (DIGIT)", "ISL Alphabets & Digits", "Index and Middle Fingers Upright", "Fundamental (Numerical Quantity)"),
    ("ISL_102", "3 (DIGIT)", "ISL Alphabets & Digits", "Thumb, Index, Middle Extended", "Fundamental (Numerical Quantity)"),
    ("ISL_103", "4 (DIGIT)", "ISL Alphabets & Digits", "Four Fingers Upright, Thumb In", "Fundamental (Numerical Quantity)"),
    ("ISL_104", "5 (DIGIT)", "ISL Alphabets & Digits", "All Five Digits Spread Open", "Fundamental (Numerical Quantity)"),
    ("ISL_105", "6 (DIGIT)", "ISL Alphabets & Digits", "Thumb and Pinky Touch, 3 Up", "Fundamental (Numerical Quantity)"),
    ("ISL_106", "7 (DIGIT)", "ISL Alphabets & Digits", "Thumb and Ring Touch, 3 Up", "Fundamental (Numerical Quantity)"),
    ("ISL_107", "8 (DIGIT)", "ISL Alphabets & Digits", "Thumb and Middle Touch, 3 Up", "Fundamental (Numerical Quantity)"),
    ("ISL_108", "9 (DIGIT)", "ISL Alphabets & Digits", "Thumb and Index Touch, 3 Up", "Fundamental (Numerical Quantity)"),
    ("ISL_109", "10 (DIGIT)", "ISL Alphabets & Digits", "Thumb Upright Shakes Laterally", "Fundamental (Numerical Quantity)")
]

ANNEXURE_C_TEXT = """
ANNEXURE C: SYSTEM DEPLOYMENT RUNBOOK AND CONFIGURATION MATRIX

C.1 Environment Configuration Parameters
The SignBridge AI backend service requires specific environment variables for deterministic execution:
• SEQ_LEN: Configured to 45 frames (uniform temporal window size).
• FEAT_DIM: Configured to 189 floating-point values per time step.
• RATE_PER_MIN: Set to 120 requests per minute to prevent denial-of-service abuse while supporting interactive sign rates.
• JWT_SECRET: Configured with a cryptographic salt for model administration and calibration overrides.
• GEMINI_API_KEY: Cloud authorization token granting access to Google Gemini 2.0 Flash for ISL gloss structuring.
• CORS_ORIGINS: Comma-separated allowed client domains ("http://localhost:3000,http://127.0.0.1:3000").

C.2 Local Development Startup Sequence
To launch the complete dual-server SignBridge AI platform:
1. Backend Microservice:
   cd backend
   py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
2. Frontend Progressive Web Application:
   cd frontend
   npm run dev -- --port 3000 --host 127.0.0.1

C.3 Automated Verification and Model Checksums
All trained model weights and preprocessing checkpoints are verified via SHA-256 cryptographic hashes:
• SBAI-MDL-ISL-4.0.0_lstm.keras: Verified size 1,489,204 bytes.
• SBAI-MDL-ISL-4.0.0_gru.keras: Verified size 1,228,840 bytes.
• class_map.csv: 109 rows matching ISL_001 through ISL_109.
"""
