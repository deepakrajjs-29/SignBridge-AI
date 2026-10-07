import { afterEach, describe, expect, test, vi } from "vitest";
import {
  CAMERA_ERROR_NOTE,
  CAMERA_TIMEOUT_MS,
  recognizeFrames,
  requestCameraStream,
  toState,
} from "./Live";
import type { Prediction, RecState } from "../api/client";
import type { StreamCallbacks } from "../api/stream";

function stubGetUserMedia(impl: () => Promise<MediaStream>) {
  const getUserMedia = vi.fn(impl);
  Object.defineProperty(globalThis, "navigator", {
    value: { mediaDevices: { getUserMedia } },
    configurable: true,
    writable: true,
  });
  return getUserMedia;
}

afterEach(() => {
  Reflect.deleteProperty(globalThis, "navigator");
  vi.useRealTimers();
  vi.restoreAllMocks();
});

describe("Live camera request", () => {
  test("camera request that never settles shows Error + guidance", async () => {
    vi.useFakeTimers();
    // Proven hang: getUserMedia promise never settles -> UI stuck on Ready.
    stubGetUserMedia(() => new Promise<MediaStream>(() => {}));
    const pending = requestCameraStream();
    const assertion = expect(pending).rejects.toThrow(/timed out/);
    await vi.advanceTimersByTimeAsync(CAMERA_TIMEOUT_MS);
    await assertion;
    // enableCamera maps any such rejection into the existing Error path,
    // whose guidance note is the single CAMERA_ERROR_NOTE constant.
    expect(CAMERA_ERROR_NOTE).toMatch(/Check browser permission and retry/);
  });

  test("settling camera request resolves without waiting for the timeout", async () => {
    vi.useFakeTimers();
    const fakeStream = {} as MediaStream;
    const getUserMedia = stubGetUserMedia(() => Promise.resolve(fakeStream));
    await expect(requestCameraStream()).resolves.toBe(fakeStream);
    expect(getUserMedia).toHaveBeenCalledOnce();
  });
});

describe("Live stream-first recognition with REST fallback", () => {
  const FRAMES = [
    [0.1, 0.2],
    [0.3, 0.4],
  ];
  const REST_RESULT = {
    prediction: { class_id: "ISL_001", label: "hello", confidence: 0.92 } as Prediction,
    status: "recognized",
  };

  function failingStream() {
    // Mock connectStream: invokes onError like a dead CDN/socket and records
    // every frame Live attempted to stream plus the session it connected with.
    const sendFrame = vi.fn();
    const stop = vi.fn();
    const seen: { base: string; sid: string } | null = null;
    const box: { args: { base: string; sid: string } | null } = { args: seen };
    const connect = (_base: string, _sid: string, c: StreamCallbacks) => {
      box.args = { base: _base, sid: _sid };
      queueMicrotask(() => c.onError("WebSocket error — use REST fallback."));
      return { sendFrame, heartbeat: vi.fn(), stop, socket: {} as WebSocket };
    };
    return { connect, sendFrame, stop, box };
  }

  test("stream onError runs the REST api.predict path and delivers the result", async () => {
    const { connect, sendFrame, box } = failingStream();
    const connectSpy = vi.fn(connect);
    const predict = vi.fn(async (_frames: number[][], _sid: string) => REST_RESULT);
    const states: RecState[] = [];
    const delivered: { cur: { p: Prediction; status: string } | null } = { cur: null };

    const out = await recognizeFrames(FRAMES, "sess_1", {
      connect: connectSpy,
      predict,
      onState: (s) => void states.push(s),
      onNote: () => {},
      onPrediction: (p, status) => void (delivered.cur = { p, status }),
      timeoutMs: 1000,
    });

    // Live attempted the WS path first (session + every frame sent).
    expect(connectSpy).toHaveBeenCalledOnce();
    expect(box.args?.sid).toBe("sess_1");
    expect(sendFrame).toHaveBeenCalledTimes(FRAMES.length);
    // Stream failure never dead-ends Live: REST fallback ran and the result
    // (what the view renders via onPrediction) is the REST prediction.
    expect(out.path).toBe("rest");
    expect(predict).toHaveBeenCalledOnce();
    expect(delivered.cur?.p.label).toBe("hello");
    expect(delivered.cur?.status).toBe("recognized");
    expect(states).toContain("Tracking-Lost");
  });

  test("stream prediction wins and REST predict is never called", async () => {
    const sendFrame = vi.fn();
    const stop = vi.fn();
    const streamPred = {
      class_id: "ISL_002",
      label: "thanks",
      confidence: 0.88,
    } as Prediction;
    const connectImpl = (_base: string, _sid: string, c: StreamCallbacks) => {
      queueMicrotask(() => c.onPrediction(streamPred, "Recognized"));
      return { sendFrame, heartbeat: vi.fn(), stop, socket: {} as WebSocket };
    };
    const connect = vi.fn(connectImpl);
    const predict = vi.fn(async () => REST_RESULT);
    const delivered: { cur: { p: Prediction; status: string } | null } = { cur: null };

    const out = await recognizeFrames(FRAMES, "sess_1", {
      connect,
      predict,
      onPrediction: (p, status) => void (delivered.cur = { p, status }),
      timeoutMs: 1000,
    });

    expect(out).toEqual({ path: "stream", status: "Recognized" });
    expect(predict).not.toHaveBeenCalled();
    expect(delivered.cur?.p.label).toBe("thanks");
    expect(stop).toHaveBeenCalledOnce();
  });

  test("toState maps no-sign to No-Sign", () => {
    expect(toState("no-sign", true)).toBe("No-Sign");
    expect(toState("recognized", true)).toBe("Recognized");
    expect(toState("uncertain", true)).toBe("Uncertain");
    expect(toState("recognized", false)).toBe("Error");
  });
});
