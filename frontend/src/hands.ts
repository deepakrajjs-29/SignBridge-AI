/**
 * Hand-landmark preprocessing — EXACT port of ai/preprocessing/landmarks.py
 * + ai/features/build.py (FV-1.0). Any change here breaks model agreement;
 * verify against src/hands.parity.json (generated from the Python pipeline).
 *
 * Layout: frames[T][2][21][3] (mirrors h5 'intermediate').
 * Per frame features (189): 126 wrist-normalized xyz (h0 then h1)
 * + 42 speed magnitudes + 21 hand-shape stats. Then sample/pad to 45.
 */

export const SEQ_LEN = 45;
export const FEAT_DIM = 189;
const HANDS = 2;
const JPTS = 21;

export type Frames = number[][][][]; // [T][2][21][3]

function handPresent(hand: number[][]): boolean {
  for (const p of hand) for (const v of p) if (v !== 0) return true;
  return false;
}

/** Least-active-hand-first seating; deterministic, train/serve identical (mirrors canonicalize(); swap on tie). */
export function canonicalize(frames: Frames): Frames {
  let a0 = 0;
  let a1 = 0;
  for (const f of frames) {
    for (const p of f[0]) for (const v of p) if (v !== 0) a0++;
    for (const p of f[1]) for (const v of p) if (v !== 0) a1++;
  }
  if (a1 > a0) return frames;
  return frames.map((f) => [f[1], f[0]]);
}

/** Wrist-relative, hand-size scaled (mirrors normalize()). */
export function normalize(frames: Frames): Frames {
  return frames.map((f) =>
    f.map((hand) => {
      if (!handPresent(hand)) return hand.map(() => [0, 0, 0]);
      const ref = hand[0];
      const shifted = hand.map((p) => [p[0] - ref[0], p[1] - ref[1], p[2] - ref[2]]);
      let scale = 0;
      for (const p of shifted) {
        const n = Math.hypot(p[0], p[1], p[2]);
        if (n > scale) scale = n;
      }
      if (scale <= 1e-6) return shifted;
      return shifted.map((p) => [p[0] / scale, p[1] / scale, p[2] / scale]);
    })
  );
}

function finite(v: number): number {
  return Number.isFinite(v) ? v : 0;
}

/** (T,2,21,3) -> (T,189) (mirrors frame_features()). */
export function frameFeatures(norm: Frames): number[][] {
  const T = norm.length;
  const coords: number[][] = norm.map((f) => f.flat(2));
  // speed magnitude per landmark vs previous frame
  const speed: number[][] = [];
  for (let t = 0; t < T; t++) {
    const row: number[] = [];
    for (let h = 0; h < HANDS; h++)
      for (let j = 0; j < JPTS; j++) {
        if (t === 0) {
          row.push(0);
        } else {
          const a = norm[t][h][j];
          const b = norm[t - 1][h][j];
          row.push(Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]));
        }
      }
    speed.push(row);
  }
  // per-hand bbox stats: min(3)+max(3)+center(3)+size(1) per hand, + hand-count/2
  const stats: number[][] = norm.map((f) => {
    const row = new Array(21).fill(0) as number[];
    let n = 0;
    for (let h = 0; h < HANDS; h++) {
      const hand = f[h];
      if (!handPresent(hand)) continue;
      n++;
      const mn = [Infinity, Infinity, Infinity];
      const mx = [-Infinity, -Infinity, -Infinity];
      for (const p of hand)
        for (let d = 0; d < 3; d++) {
          if (p[d] < mn[d]) mn[d] = p[d];
          if (p[d] > mx[d]) mx[d] = p[d];
        }
      for (let d = 0; d < 3; d++) {
        row[h * 10 + d] = mn[d];
        row[h * 10 + 3 + d] = mx[d];
        row[h * 10 + 6 + d] = (mn[d] + mx[d]) / 2;
      }
      row[h * 10 + 9] = Math.hypot(mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2]);
    }
    row[20] = n / 2;
    return row;
  });
  return coords.map((c, t) => [...c, ...speed[t], ...stats[t]].map(finite));
}

/** (T,189) -> {seq (45,189), mask (45,)} (mirrors to_sequence()). */
export function toSequence(feats: number[][]): { seq: number[][]; mask: number[] } {
  const T = feats.length;
  if (T >= SEQ_LEN) {
    const idx: number[] = [];
    for (let k = 0; k < SEQ_LEN; k++) idx.push(Math.floor((k * (T - 1)) / (SEQ_LEN - 1)));
    return { seq: idx.map((i) => [...feats[i]]), mask: new Array(SEQ_LEN).fill(1) };
  }
  const last = feats[T - 1];
  const seq = [...feats.map((r) => [...r])];
  const mask = [...new Array(T).fill(1)];
  for (let k = T; k < SEQ_LEN; k++) {
    seq.push([...last]);
    mask.push(0);
  }
  return { seq, mask };
}

/** Full pipeline: raw landmark frames -> 45x189 model-ready rows. */
export function buildSequence(frames: Frames): number[][] {
  return toSequence(frameFeatures(normalize(canonicalize(frames)))).seq;
}
