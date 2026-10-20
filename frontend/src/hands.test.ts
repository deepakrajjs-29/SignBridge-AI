import { describe, expect, it } from "vitest";
import {
  buildFeatureRows,
  buildSequence,
  toSequence,
  frameFeatures,
  normalize,
  canonicalize,
} from "./hands";
import fixture from "./hands.parity.json";

const TOL = 1e-5;

function close(a: number[][], b: number[][]): number {
  let m = 0;
  for (let i = 0; i < a.length; i++)
    for (let j = 0; j < a[i].length; j++) m = Math.max(m, Math.abs(a[i][j] - b[i][j]));
  return m;
}

describe("hands.ts parity with Python FV-1.0 pipeline", () => {
  it("pad path (T=4, one-hand): matches Python incl. mask", () => {
    const seq = buildSequence(fixture.pad.input as number[][][][]);
    expect(seq.length).toBe(45);
    expect(seq[0].length).toBe(189);
    expect(close(seq, fixture.pad.expected as number[][])).toBeLessThan(TOL);
    const { mask } = toSequence(frameFeatures(normalize(canonicalize(fixture.pad.input as number[][][][]))));
    expect(mask.reduce((s, v) => s + v, 0)).toBe(4);
  });
  it("sample path (T=50, left-handed): matches Python incl. canonicalize", () => {
    const seq = buildSequence(fixture.sample.input as number[][][][]);
    expect(close(seq, fixture.sample.expected as number[][])).toBeLessThan(TOL);
  });
  it("T=45: full-T buildFeatureRows IS the model window (no subsample loss)", () => {
    const f = (fixture.sample.input as number[][][][]).slice(0, 45);
    expect(f).toHaveLength(45);
    const rows = buildFeatureRows(f);
    // Full-T rows and the 45-row sequence agree exactly at T=45 (identity resample).
    expect(rows).toEqual(toSequence(rows).seq);
    expect(buildSequence(f)).toEqual(rows);
    expect(rows[0]).toHaveLength(189);
  });
});
