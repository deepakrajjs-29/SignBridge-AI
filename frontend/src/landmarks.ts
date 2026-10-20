/**
 * Webcam landmark providers (Option A).
 *
 * MediaPipeProvider is the production path: on-device HandLandmarker
 * (tasks-vision) over the browser webcam -> raw (T,2,21,3) landmark frames
 * -> hands.ts FV-1.0 pipeline -> full-T rows (T,189) sent to POST /predict
 * or the WS `window` message; the single 45-row resample happens server-side.
 * Frames never leave the browser; only the .task model + wasm download once.
 *
 * DemoProvider remains for unit tests only (never used by Live view).
 */
import { FilesetResolver, HandLandmarker } from "@mediapipe/tasks-vision";
import { buildFeatureRows, type Frames } from "./hands";

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
/**
 * Time-boxed capture window. The old 45-rAF loop (~0.75 s at 60 Hz) clipped
 * dynamic signs mid-performance: offline replay measured 0.475 accuracy for
 * contiguous 45-frame windows vs 0.822 for full-sign windows. 3.5 s covers
 * ~1 s reaction delay + a whole performance + idle tail: the realistic
 * (1 s delay + tail) window measured 0.769 on n=1500 test clips.
 */
export const CAPTURE_WINDOW_MS = 3500;
/** Minimum unique camera frames before a sequence can be trusted (toSequence
 * pads beyond 45 rows for slow cameras; below this the window caught no sign). */
export const MIN_CAPTURE_FRAMES = 30;

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
    _frames = 45,
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
    let lastVideoTime = Number.NaN;
    const windowStart = Date.now();
    try {
      while (Date.now() - windowStart < CAPTURE_WINDOW_MS) {
        abortIfPastDeadline();
        // Dedupe: rAF can outrun the camera (60 Hz vs 30 fps); reprocessing the
        // same video frame injects zero-speed rows into the FV-1.0 speed features.
        if (video.currentTime !== lastVideoTime) {
          lastVideoTime = video.currentTime;
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
          const elapsedS = Math.min((Date.now() - windowStart) / 1000, CAPTURE_WINDOW_MS / 1000);
          this.progress = `Capturing ${elapsedS.toFixed(1)} / ${
            CAPTURE_WINDOW_MS / 1000
          } s — perform the sign now`;
        }
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
    if (raw.length < MIN_CAPTURE_FRAMES || raw.every((f) => f.flat(2).every((v) => v === 0))) {
      this.status = "error";
      this.error = "No hands detected during capture — move closer, improve light, reframe.";
      throw new Error(this.error);
    }
    this.status = "ready";
    // Full-T rows (no 45-frame subsample): the whole 3.5 s capture reaches
    // the backend, which owns the single 45-row resample (preprocess_window).
    return buildFeatureRows(raw);
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
