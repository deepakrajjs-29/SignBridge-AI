import { afterEach, describe, expect, test, vi } from "vitest";
import {
  CAMERA_ERROR_NOTE,
  CAMERA_TIMEOUT_MS,
  COUNTDOWN_MS,
  COUNTDOWN_TICKS,
  DEFAULT_THRESHOLD_PERCENT,
  MAX_SESSION_RECOVERIES,
  appendConfirmedWord,
  confidenceNote,
  isUnknownSessionError,
  readThresholdGate,
  recognizeFrames,
  requestCameraStream,
  resolveCommit,
  runCountdown,
  runSingleAttempt,
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
  Reflect.deleteProperty(globalThis, "localStorage");
  vi.useRealTimers();
  vi.restoreAllMocks();
});

/** Minimal in-memory localStorage (vitest runs in the node environment). */
function stubLocalStorage(initial?: Record<string, string>) {
  const store = new Map<string, string>(Object.entries(initial ?? {}));
  Object.defineProperty(globalThis, "localStorage", {
    value: {
      getItem: (k: string) => (store.has(k) ? (store.get(k) as string) : null),
      setItem: (k: string, v: string) => void store.set(k, String(v)),
      removeItem: (k: string) => void store.delete(k),
    },
    configurable: true,
  });
  return store;
}

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

describe("unknown-session error detection (session recovery)", () => {
  test("REST 404 UNKNOWN_SESSION code is detected", () => {
    const e = new Error("unknown session") as Error & { code?: string };
    e.code = "UNKNOWN_SESSION";
    expect(isUnknownSessionError(e)).toBe(true);
  });

  test("HTTP_404 and message-only forms are detected", () => {
    const withCode = new Error("not found") as Error & { code?: string };
    withCode.code = "HTTP_404";
    expect(isUnknownSessionError(withCode)).toBe(true);
    expect(isUnknownSessionError(new Error("Unknown session — re-open session and retry."))).toBe(true);
  });

  test("hands-lost / timeout / non-errors are not treated as session failures", () => {
    expect(isUnknownSessionError(new Error("No hands detected"))).toBe(false);
    const timeout = new Error("Request timed out after 1000 ms — retry.") as Error & { code?: string };
    timeout.code = "TIMEOUT";
    expect(isUnknownSessionError(timeout)).toBe(false);
    expect(isUnknownSessionError("unknown session")).toBe(false);
    expect(isUnknownSessionError(null)).toBe(false);
  });

  test("recovery is capped so continuous mode cannot loop forever", () => {
    expect(MAX_SESSION_RECOVERIES).toBe(2);
  });
});

describe("user-confirmed word append (no duplicate spam)", () => {
  test("appends a normal confirmed label uppercased", () => {
    expect(appendConfirmedWord(["I"], "market")).toEqual(["I", "MARKET"]);
  });

  test("suppresses immediate duplicate of the last word", () => {
    expect(appendConfirmedWord(["SCHOOL", "MARKET"], "market")).toEqual(["SCHOOL", "MARKET"]);
  });

  test("rejects no-sign and empty labels", () => {
    expect(appendConfirmedWord(["A"], "no sign detected")).toEqual(["A"]);
    expect(appendConfirmedWord(["A"], "")).toEqual(["A"]);
    expect(appendConfirmedWord([], "  ")).toEqual([]);
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
    // every window Live attempted to stream plus the session it connected with.
    const sendFrame = vi.fn();
    const sendWindow = vi.fn();
    const stop = vi.fn();
    const seen: { base: string; sid: string } | null = null;
    const box: { args: { base: string; sid: string } | null } = { args: seen };
    const connect = (_base: string, _sid: string, c: StreamCallbacks) => {
      box.args = { base: _base, sid: _sid };
      queueMicrotask(() => c.onError("WebSocket error — use REST fallback."));
      return { sendFrame, sendWindow, heartbeat: vi.fn(), stop, socket: {} as WebSocket };
    };
    return { connect, sendFrame, sendWindow, stop, box };
  }

  test("stream onError runs the REST api.predict path and delivers the result", async () => {
    const { connect, sendFrame, sendWindow, box } = failingStream();
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

    // Live attempted the WS path first: ONE full-T window message, never per-frame.
    expect(connectSpy).toHaveBeenCalledOnce();
    expect(box.args?.sid).toBe("sess_1");
    expect(sendWindow).toHaveBeenCalledTimes(1);
    expect(sendWindow).toHaveBeenCalledWith(FRAMES);
    expect(sendFrame).not.toHaveBeenCalled();
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
    const sendWindow = vi.fn();
    const stop = vi.fn();
    const streamPred = {
      class_id: "ISL_002",
      label: "thanks",
      confidence: 0.88,
    } as Prediction;
    const connectImpl = (_base: string, _sid: string, c: StreamCallbacks) => {
      queueMicrotask(() => c.onPrediction(streamPred, "Recognized"));
      return { sendFrame, sendWindow, heartbeat: vi.fn(), stop, socket: {} as WebSocket };
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

  test("toState maps provisional (REST lowercase and WS capitalized)", () => {
    expect(toState("provisional", true)).toBe("Provisional");
    expect(toState("Provisional", true)).toBe("Provisional");
    expect(toState("provisional", false)).toBe("Error");
  });

  test("confidenceNote distinguishes provisional, uncertain, recognized", () => {
    expect(confidenceNote("recognized", 0.9)).toBeNull();
    expect(confidenceNote("Recognized", 0.9)).toBeNull();
    const prov = confidenceNote("provisional", 0.52);
    expect(prov).toContain("Provisional (52.0%)");
    expect(prov).toContain("Not added to your sequence");
    expect(confidenceNote("Provisional", 0.4)).toContain("Provisional (40.0%)");
    const unc = confidenceNote("uncertain", 0.12);
    expect(unc).toContain("Low confidence (12.0%)");
    expect(unc).toContain("shown as Uncertain, not definitive");
    expect(confidenceNote("no-sign", 0)).toContain("shown as Uncertain");
  });
});

describe("release-based commit gate (one performance = one commit)", () => {
  const base = { label: "HELLO", lastLabel: "", armed: true, freshAttempt: false };

  test("first accepted sign commits and closes the gate", () => {
    expect(resolveCommit({ ...base, accepted: true })).toEqual({
      commit: true,
      armed: false,
      lastLabel: "HELLO",
    });
  });

  test("held sign re-observed in later windows is suppressed until release", () => {
    const held = { accepted: true, label: "hello", lastLabel: "HELLO", armed: false, freshAttempt: false };
    const first = resolveCommit(held);
    expect(first.commit).toBe(false);
    expect(first.armed).toBe(false); // still held -> gate stays closed
    expect(first.lastLabel).toBe("HELLO");
  });

  test("a release window (hard release: no-sign) re-arms the same sign", () => {
    const released = resolveCommit({
      accepted: false,
      label: "NO SIGN DETECTED",
      lastLabel: "HELLO",
      armed: false,
      freshAttempt: false,
      hardRelease: true,
    });
    expect(released.commit).toBe(false);
    expect(released.armed).toBe(true);
    // Next accepted HELLO after the release commits again (repeat preserved).
    expect(
      resolveCommit({ accepted: true, label: "HELLO", lastLabel: "HELLO", armed: released.armed, freshAttempt: false })
    ).toEqual({ commit: true, armed: false, lastLabel: "HELLO" });
  });

  test("a single soft window does NOT re-arm (mid-hold flicker protection)", () => {
    expect(
      resolveCommit({ ...base, accepted: false, armed: false, streak: 1 }).armed
    ).toBe(false);
  });

  test("two consecutive soft windows re-arm (true release)", () => {
    expect(
      resolveCommit({ ...base, accepted: false, armed: false, streak: 2 }).armed
    ).toBe(true);
  });

  test("flicker sequence A -> soft -> A commits exactly once", () => {
    const r1 = resolveCommit({ ...base, accepted: true }); // commit, armed false
    const r2 = resolveCommit({ ...base, accepted: false, armed: r1.armed, streak: 1 });
    // held same label (lastLabel carried from r1) -> suppressed
    const r3 = resolveCommit({ ...base, accepted: true, armed: r2.armed, lastLabel: r1.lastLabel });
    expect(r1.commit).toBe(true);
    expect(r2.armed).toBe(false);
    expect(r3.commit).toBe(false);
  });

  test("A -> soft -> soft -> A commits twice (real release between)", () => {
    const a1 = resolveCommit({ ...base, accepted: true });
    const s1 = resolveCommit({ ...base, accepted: false, armed: a1.armed, streak: 1 });
    const s2 = resolveCommit({ ...base, accepted: false, armed: s1.armed, streak: 2 });
    expect(s1.armed).toBe(false);
    expect(s2.armed).toBe(true);
    const a2 = resolveCommit({ ...base, accepted: true, armed: s2.armed, lastLabel: a1.lastLabel });
    expect(a2.commit).toBe(true);
  });

  test("no-sign arms in one window (hardRelease beats the streak)", () => {
    const soft = resolveCommit({ ...base, accepted: false, armed: false, streak: 1 });
    expect(soft.armed).toBe(false);
    const hard = resolveCommit({
      ...base,
      accepted: false,
      armed: false,
      streak: 1,
      hardRelease: true,
    });
    expect(hard.armed).toBe(true);
  });

  test("single-sign attempt bypasses a closed gate", () => {
    expect(
      resolveCommit({ accepted: true, label: "HELLO", lastLabel: "HELLO", armed: false, freshAttempt: true })
    ).toEqual({ commit: true, armed: false, lastLabel: "HELLO" });
  });

  test("a different sign commits regardless of arm state", () => {
    expect(
      resolveCommit({ accepted: true, label: "WORLD", lastLabel: "HELLO", armed: false, freshAttempt: false })
    ).toEqual({ commit: true, armed: false, lastLabel: "WORLD" });
  });

  test("default confidence gate is 60 percent (evidence-based)", () => {
    expect(DEFAULT_THRESHOLD_PERCENT).toBe(60);
  });
});

describe("readThresholdGate (explicit user gate only)", () => {
  test("unset -> null; explicit value -> percent; garbage -> null", () => {
    stubLocalStorage();
    expect(readThresholdGate()).toBeNull();
    localStorage.setItem("sb_threshold", "75");
    expect(readThresholdGate()).toBe(75);
    localStorage.setItem("sb_threshold", "not-a-number");
    expect(readThresholdGate()).toBeNull();
    localStorage.removeItem("sb_threshold");
    expect(readThresholdGate()).toBeNull();
  });
});

describe("single-sign countdown (pre-capture readiness)", () => {
  test("constants are 3 ticks x 400ms = 1200ms total", () => {
    expect(COUNTDOWN_TICKS).toBe(3);
    expect(COUNTDOWN_MS).toBe(400);
  });

  test("ticks 3,2,1 then clears 0 across exactly 1200ms", async () => {
    vi.useFakeTimers();
    const ticks: number[] = [];
    const done = runCountdown((r) => void ticks.push(r));
    await vi.advanceTimersByTimeAsync(0);
    expect(ticks).toEqual([3]);
    await vi.advanceTimersByTimeAsync(400);
    expect(ticks).toEqual([3, 2]);
    await vi.advanceTimersByTimeAsync(400);
    expect(ticks).toEqual([3, 2, 1]);
    await vi.advanceTimersByTimeAsync(400);
    expect(ticks).toEqual([3, 2, 1, 0]);
    await done;
  });

  test("stops early and clears when cancelled mid-countdown", async () => {
    vi.useFakeTimers();
    const ticks: number[] = [];
    let checks = 0;
    const done = runCountdown((r) => void ticks.push(r), () => ++checks > 1);
    await vi.advanceTimersByTimeAsync(0);
    expect(ticks).toEqual([3]);
    await vi.advanceTimersByTimeAsync(400);
    await done;
    expect(ticks).toEqual([3, 0]);
  });

  test("capture does not start before the countdown completes", async () => {
    vi.useFakeTimers();
    const order: string[] = [];
    const p = runSingleAttempt(
      () => runCountdown(() => {}),
      async () => void order.push("capture")
    );
    await vi.advanceTimersByTimeAsync(0);
    expect(order).toEqual([]);
    await vi.advanceTimersByTimeAsync(1200);
    await p;
    expect(order).toEqual(["capture"]);
  });
});
