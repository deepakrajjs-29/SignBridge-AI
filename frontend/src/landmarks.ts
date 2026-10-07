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

export type LandmarkerDelegate = "GPU" | "CPU";

/** Creation attempt order: GPU first, CPU fallback (first success wins). */
const DELEGATE_ORDER: LandmarkerDelegate[] = ["GPU", "CPU"];

export const DOWNLOAD_ERROR_MESSAGE =
  "Hand-tracking model failed to download (network needed once). Retry online.";
export const DELEGATE_ERROR_MESSAGE =
  "Hand-tracking failed to start (GPU delegate unsupported and CPU fallback failed). Try a different browser or device.";

export interface LandmarkerDeps {
  resolveFileset?: typeof FilesetResolver.forVisionTasks;
  create?: typeof HandLandmarker.createFromOptions;
}

function codedError(message: string, code: "DOWNLOAD" | "DELEGATE"): Error {
  return Object.assign(new Error(message), { code });
}

/**
 * Internal creation seam (exported for tests): resolves the wasm fileset
 * once, then tries each delegate in order and returns the first success.
 * Fileset (network) failures throw a DOWNLOAD-coded error; exhausting all
 * delegates throws a DELEGATE-coded error so callers stay truthful.
 */
export async function createLandmarker(
  delegates: LandmarkerDelegate[] = DELEGATE_ORDER,
  deps: LandmarkerDeps = {}
): Promise<HandLandmarker> {
  const resolveFileset = deps.resolveFileset ?? FilesetResolver.forVisionTasks;
  const create = deps.create ?? HandLandmarker.createFromOptions;
  let fileset: Awaited<ReturnType<typeof FilesetResolver.forVisionTasks>>;
  try {
    fileset = await resolveFileset(WASM_BASE);
  } catch {
    throw codedError(DOWNLOAD_ERROR_MESSAGE, "DOWNLOAD");
  }
  for (const delegate of delegates) {
    try {
      return await create(fileset, {
        baseOptions: { modelAssetPath: MODEL_URL, delegate },
        runningMode: "VIDEO",
        numHands: 2,
      });
    } catch {
      // Try the next delegate (GPU failure falls through to CPU).
    }
  }
  throw codedError(DELEGATE_ERROR_MESSAGE, "DELEGATE");
}

let shared: Promise<HandLandmarker> | null = null;
/** Shared singleton (exported for tests); happy-path creation is unchanged. */
export function landmarker(): Promise<HandLandmarker> {
  if (!shared) {
    shared = createLandmarker(DELEGATE_ORDER);
    shared.catch(() => {
      shared = null; // allow retry after failure
    });
  }
  return shared;
}

/**
 * Clears the shared landmarker, closing the underlying instance.
 * Safe no-op when nothing was ever created.
 */
export function dispose(): void {
  const pending = shared;
  shared = null;
  if (pending) {
    pending.then(
      (lm) => {
        try {
          lm.close();
        } catch {
          /* already closed */
        }
      },
      () => {
        /* creation failed — nothing to close */
      }
    );
  }
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

  /** Releases the shared on-device model. Safe no-op if never created. */
  dispose(): void {
    // Bare `dispose()` resolves to the module-level function (methods are
    // properties, not lexical bindings), so this is not recursive.
    dispose();
  }

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
    } catch (e) {
      this.status = "error";
      // Truthful errors: delegate exhaustion (unsupported device/browser)
      // must not masquerade as a network download failure.
      const code = (e as { code?: string } | null)?.code;
      this.error = code === "DELEGATE" ? DELEGATE_ERROR_MESSAGE : DOWNLOAD_ERROR_MESSAGE;
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
