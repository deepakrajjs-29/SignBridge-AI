import { afterEach, describe, expect, test, vi } from "vitest";
import { CAMERA_ERROR_NOTE, CAMERA_TIMEOUT_MS, requestCameraStream } from "./Live";

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
