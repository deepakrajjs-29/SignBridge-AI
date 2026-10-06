import { describe, expect, it } from "vitest";
import { DemoProvider, isFiniteFrame } from "./landmarks";

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
