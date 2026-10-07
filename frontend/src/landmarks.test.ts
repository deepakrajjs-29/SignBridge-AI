import { beforeEach, describe, expect, it, test, vi } from "vitest";
import { DemoProvider, createLandmarker, dispose, isFiniteFrame, landmarker } from "./landmarks";
import { FilesetResolver, HandLandmarker } from "@mediapipe/tasks-vision";

vi.mock("@mediapipe/tasks-vision", () => ({
  FilesetResolver: { forVisionTasks: vi.fn() },
  HandLandmarker: { createFromOptions: vi.fn() },
}));

describe("DemoProvider (unit-test synthetic source)", () => {
  it("emits finite 45x189 frames", async () => {
    const frames = await new DemoProvider().capture(undefined, 45);
    expect(frames).toHaveLength(45);
    expect(isFiniteFrame(frames)).toBe(true);
  });
  it("rejects malformed frames", () => {
    expect(isFiniteFrame([])).toBe(false);
    expect(isFiniteFrame([[0, 1]])).toBe(false);
  });
});

describe("MediaPipe delegate fallback + disposal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    dispose();
  });

  test("falls back to CPU when GPU delegate fails", async () => {
    vi.mocked(FilesetResolver.forVisionTasks).mockResolvedValue({} as never);
    const cpu = { close: vi.fn() };
    vi.mocked(HandLandmarker.createFromOptions).mockImplementation(
      async (_fileset: unknown, options?: { baseOptions?: { delegate?: string } }) => {
        if (options?.baseOptions?.delegate === "GPU") throw new Error("GPU delegate unsupported");
        return cpu as never;
      }
    );

    const lm = await createLandmarker(["GPU", "CPU"]);

    expect(lm).toBe(cpu);
    expect(vi.mocked(FilesetResolver.forVisionTasks)).toHaveBeenCalledOnce();
    const delegates = vi
      .mocked(HandLandmarker.createFromOptions)
      .mock.calls.map((c) => (c[1] as { baseOptions?: { delegate?: string } })?.baseOptions?.delegate);
    expect(delegates).toEqual(["GPU", "CPU"]);
    dispose();
  });

  test("dispose clears the shared landmarker", async () => {
    vi.mocked(FilesetResolver.forVisionTasks).mockResolvedValue({} as never);
    const first = { close: vi.fn() };
    const second = { close: vi.fn() };
    vi.mocked(HandLandmarker.createFromOptions)
      .mockResolvedValueOnce(first as never)
      .mockResolvedValueOnce(second as never);

    const a = await landmarker();
    const b = await landmarker();
    expect(a).toBe(b);
    expect(vi.mocked(HandLandmarker.createFromOptions)).toHaveBeenCalledTimes(1);

    dispose();
    await new Promise<void>((r) => {
      setTimeout(r, 0);
    });
    expect(first.close).toHaveBeenCalledOnce();

    const c = await landmarker();
    expect(c).toBe(second);
    expect(vi.mocked(HandLandmarker.createFromOptions)).toHaveBeenCalledTimes(2);
    dispose();
  });
});
