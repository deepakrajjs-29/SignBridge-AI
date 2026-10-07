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
import { buildSequence, type Frames } from "./hands";

const WASM_BASE = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.0.1/wasm";
const MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task";

export type ProviderStatus = "idle" | "loading-model" | "ready" | "capturing" | "error";

export interface LandmarkProvider {
  readonly name: string;
  status: ProviderStatus;
  error: string;
  progress: string;
  capture(video: HTMLVideoElement, frames?: number, deadlineMs?: number): Promise<number[][]>;
}

let shared: Promise<HandLandmarker> | null = null;
function landmarker(): Promise<HandLandmarker> {
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

function blank(): number[][][] {
  return [Array.from({ length: 21 }, () => [0, 0, 0]), Array.from({ length: 21 }, () => [0, 0, 0])];
}

const nextFrame = () => new Promise<void>((r) => requestAnimationFrame(() => r()));

export const CAPTURE_DEADLINE_MS = 60000;

export class MediaPipeProvider implements LandmarkProvider {
  readonly name = "mediapipe-handlandmarker (on-device)";
  status: ProviderStatus = "idle";
  error = "";
  progress = "";

  async capture(
    video: HTMLVideoElement,
    frames = 45,
    deadlineMs = CAPTURE_DEADLINE_MS
  ): Promise<number[][]> {
    this.error = "";
    this.progress = "";
    if (video.readyState < 2 || video.videoWidth === 0) {
      this.status = "error";
      this.error = "Camera frame not ready — re-enable camera and retry.";
      throw new Error(this.error);
    }
    const fail = (message: string): never => {
      this.status = "error";
      this.error = message;
      throw new Error(this.error);
    };
    const deadlineMessage = () =>
      `Capture timed out after ${Math.round(deadlineMs / 1000)} s — reframe hands and retry.`;
    const start = Date.now();
    const abortIfPastDeadline = () => {
      if (Date.now() - start > deadlineMs) fail(deadlineMessage());
    };
    this.status = "loading-model";
    let lm: HandLandmarker;
    try {
      lm = await landmarker();
    } catch {
      this.status = "error";
      this.error = "Hand-tracking model failed to download (network needed once). Retry online.";
      throw new Error(this.error);
    }
    abortIfPastDeadline();
    this.status = "capturing";
    const raw: Frames = [];
    try {
      for (let t = 0; t < frames; t++) {
        abortIfPastDeadline();
        let pts = blank();
        try {
          const res = lm.detectForVideo(video, performance.now());
          const hands = res.landmarks ?? [];
          for (let h = 0; h < Math.min(2, hands.length); h++)
            pts[h] = hands[h].slice(0, 21).map((p) => [p.x, p.y, p.z]);
        } catch {
          // single-frame detection failure -> blank frame (never aborts capture)
        }
        raw.push(pts);
        this.progress = `Capturing ${t + 1}/${frames} — hold the sign steady`;
        const remaining = deadlineMs - (Date.now() - start);
        if (remaining <= 0) fail(deadlineMessage());
        let timer: ReturnType<typeof setTimeout> | undefined;
        try {
          await Promise.race([
            nextFrame(),
            new Promise<never>((_, reject) => {
              timer = setTimeout(() => reject(new Error(deadlineMessage())), remaining);
            }),
          ]);
        } catch {
          fail(deadlineMessage());
        } finally {
          if (timer !== undefined) clearTimeout(timer);
        }
      }
    } finally {
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
  readonly name = "demo (tests only)";
  status: ProviderStatus = "ready";
  error = "";
  progress = "";
  async capture(
    _video?: HTMLVideoElement,
    frames = 45,
    _deadlineMs = CAPTURE_DEADLINE_MS
  ): Promise<number[][]> {
    const out: number[][] = [];
    for (let t = 0; t < frames; t++) out.push(new Array(189).fill(((t * 37) % 11) * 0.01));
    return out;
  }
}

export function isFiniteFrame(frames: number[][]): boolean {
  return (
    frames.length > 0 &&
    frames.every((r) => r.length === 189 && r.every((v) => Number.isFinite(v)))
  );
}
