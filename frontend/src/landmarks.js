/**
 * Webcam landmark providers (Option A).
 *
 * MediaPipeProvider is the production path: on-device HandLandmarker
 * (tasks-vision) over the browser webcam -> raw (T,2,21,3) landmark frames
 * -> hands.ts FV-1.0 pipeline -> 45x189 rows for POST /predict (unchanged).
 * Frames never leave the browser; only the .task model + wasm download once.
 *
 * DemoProvider remains for unit tests only (never used by Live view).
 */
import { FilesetResolver, HandLandmarker } from "@mediapipe/tasks-vision";
import { buildSequence } from "./hands";
const WASM_BASE = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.0.1/wasm";
const MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task";
let shared = null;
function landmarker() {
    if (!shared) {
        shared = (async () => {
            const fileset = await FilesetResolver.forVisionTasks(WASM_BASE);
            return HandLandmarker.createFromOptions(fileset, {
                baseOptions: { modelAssetPath: MODEL_URL, delegate: "GPU" },
                runningMode: "VIDEO",
                numHands: 2,
            });
        })();
        shared.catch(() => {
            shared = null; // allow retry after failure
        });
    }
    return shared;
}
function blank() {
    return [Array.from({ length: 21 }, () => [0, 0, 0]), Array.from({ length: 21 }, () => [0, 0, 0])];
}
const nextFrame = () => new Promise((r) => requestAnimationFrame(() => r()));
export class MediaPipeProvider {
    constructor() {
        this.name = "mediapipe-handlandmarker (on-device)";
        this.status = "idle";
        this.error = "";
        this.progress = "";
    }
    async capture(video, frames = 45) {
        this.error = "";
        this.progress = "";
        if (video.readyState < 2 || video.videoWidth === 0) {
            this.status = "error";
            this.error = "Camera frame not ready — re-enable camera and retry.";
            throw new Error(this.error);
        }
        this.status = "loading-model";
        let lm;
        try {
            lm = await landmarker();
        }
        catch {
            this.status = "error";
            this.error = "Hand-tracking model failed to download (network needed once). Retry online.";
            throw new Error(this.error);
        }
        this.status = "capturing";
        const raw = [];
        try {
            for (let t = 0; t < frames; t++) {
                let pts = blank();
                try {
                    const res = lm.detectForVideo(video, performance.now());
                    const hands = res.landmarks ?? [];
                    for (let h = 0; h < Math.min(2, hands.length); h++)
                        pts[h] = hands[h].slice(0, 21).map((p) => [p.x, p.y, p.z]);
                }
                catch {
                    // single-frame detection failure -> blank frame (never aborts capture)
                }
                raw.push(pts);
                this.progress = `Capturing ${t + 1}/${frames} — hold the sign steady`;
                await nextFrame();
            }
        }
        finally {
            this.progress = "";
        }
        if (raw.every((f) => f.flat(2).every((v) => v === 0))) {
            this.status = "error";
            this.error = "No hands detected in 45 frames — move closer, improve light, reframe.";
            throw new Error(this.error);
        }
        this.status = "ready";
        return buildSequence(raw);
    }
}
/** Unit-test-only synthetic source (Live view no longer uses this). */
export class DemoProvider {
    constructor() {
        this.name = "demo (tests only)";
        this.status = "ready";
        this.error = "";
        this.progress = "";
    }
    async capture(_video, frames = 45) {
        const out = [];
        for (let t = 0; t < frames; t++)
            out.push(new Array(189).fill(((t * 37) % 11) * 0.01));
        return out;
    }
}
export function isFiniteFrame(frames) {
    return (frames.length > 0 &&
        frames.every((r) => r.length === 189 && r.every((v) => Number.isFinite(v))));
}
