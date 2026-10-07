import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { api, fetchWithTimeout } from "./client";
import { MediaPipeProvider } from "../landmarks";

vi.mock("@mediapipe/tasks-vision", () => ({
  FilesetResolver: { forVisionTasks: async () => ({}) },
  HandLandmarker: {
    createFromOptions: async () => ({
      detectForVideo: () => ({ landmarks: [] }),
    }),
  },
}));

// Repo precedent (client.test.ts): vitest runs in node (no DOM), so stub
// localStorage for token() instead of adding jsdom.
const store = new Map<string, string>();
beforeEach(() => {
  store.clear();
  vi.stubGlobal("localStorage", {
    getItem: (k: string) => (store.has(k) ? store.get(k)! : null),
    setItem: (k: string, v: string) => void store.set(k, v),
    removeItem: (k: string) => void store.delete(k),
    clear: () => store.clear(),
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
  vi.restoreAllMocks();
});

function neverResolvingFetch() {
  return vi.fn(() => new Promise<Response>(() => {}));
}

describe("client timeouts", () => {
  test("fetchWithTimeout rejects with code TIMEOUT when fetch never settles", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("fetch", neverResolvingFetch());
    const pending = fetchWithTimeout("http://localhost:8000/health", undefined, 1000);
    const assertion = expect(pending).rejects.toMatchObject({ code: "TIMEOUT" });
    await vi.advanceTimersByTimeAsync(1000);
    await assertion;
  });

  test("req times out with code TIMEOUT", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("fetch", neverResolvingFetch());
    const pending = api.health();
    const assertion = expect(pending).rejects.toMatchObject({ code: "TIMEOUT" });
    await vi.advanceTimersByTimeAsync(15_000);
    await assertion;
  });

  test("predict uses the 120 s budget while other endpoints use 15 s", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("fetch", neverResolvingFetch());
    let settled = false;
    const pending = api.predict([[0]], "", "");
    pending.then(
      () => void (settled = true),
      () => void (settled = true)
    );
    await vi.advanceTimersByTimeAsync(15_000);
    expect(settled).toBe(false);
    const assertion = expect(pending).rejects.toMatchObject({ code: "TIMEOUT" });
    await vi.advanceTimersByTimeAsync(105_000);
    await assertion;
  });
});

describe("capture deadline", () => {
  test("capture aborts past its deadline", async () => {
    vi.useFakeTimers();
    // Stall rAF forever (background-tab stall); the deadline must still abort.
    vi.stubGlobal("requestAnimationFrame", vi.fn(() => 0));
    const video = { readyState: 4, videoWidth: 640 } as unknown as HTMLVideoElement;
    const provider = new MediaPipeProvider();
    const pending = provider.capture(video, 45, 1000);
    const assertion = expect(pending).rejects.toThrow(/timed out/i);
    await vi.advanceTimersByTimeAsync(5000);
    await assertion;
    expect(provider.status).toBe("error");
  });
});
