# M12 — Webcam Accuracy: Root Cause, Fixes & Evidence

Status: capture/commit fixes implemented + verified (no commit made).
Model unchanged (active `4.0.0`, ensemble test acc 0.8129 / macro-F1 0.8079).

> Follow-up: [`Docs/M13_ACCURACY_CALIBRATION.md`](M13_ACCURACY_CALIBRATION.md)
> (calibration, three-state decision policy, full-T WS path, final VAL/TEST
> numbers, and the manual webcam protocol) builds on this report's root causes
> RC-A/B/C/E/F.

## TL;DR

The reported "20–30% real-world accuracy" is reproduced **offline, without a
camera**, purely from capture-window semantics — and it lands inside that band:

| condition | acc | visible correct @ gate 0.60 |
|---|---|---|
| `old_45_center` — old ~0.75 s window | 0.475 | **0.287** ← the complaint |
| `old_rafdup` — old loop reprocessing 30 fps at 60 Hz | 0.279 | **0.131** |
| `idle_realistic` — new 3.5 s capture +1 s reaction +1.5 s idle | 0.769 | **0.642** |
| `full_sign` — new capture target (whole performance) | 0.822 | **0.715** |

(n = 1500 frozen-test clips, active backend ensemble, seed 11. The model was
never the bottleneck; what the browser feeds it was.)

## Root causes (measured, not guessed)

- **RC-A — capture window ≠ training window.** Training sequences span the
  whole sign (h5 median 122 frames ≈ 4 s); the old loop took 45 rAF ticks
  ≈ 0.75 s and the UI said "hold the sign steady", clipping dynamic signs
  mid-performance (`old_45_center` = 0.475; truncate-to-3.5 s of a full clip
  = 0.815, so duration alone is not the issue — clipping the performance is).
- **RC-B — rAF duplication.** 60 Hz rAF over a 30 fps camera processed each
  camera frame twice → zero-speed interleave in FV-1.0 speed features
  (`old_rafdup` = 0.279).
- **RC-C — double gate.** Frontend stacked `sb_threshold` default **0.70**
  over backend policy 0.4: on test, 0.70 accepts 69% vs 0.60 accepting 78%
  (precision 0.93 vs 0.91) — 9 points of coverage for 2 points of precision.
- **RC-E — fixed 2.5 s cooldown instead of release-based re-arm** let a held
  pose re-commit every 2.5 s (sequence pollution + speech repeats).
- **RC-F — speech interruption.** Per-sign words cancelled the generated
  sentence mid-flight and vice versa; a single-sign sentence re-spoke the word
  ("HELLO" → "Hello." echo).
- Trim/settle alternatives were tested and **rejected on evidence**: edge trim
  0.798→0.759, motion-settle early stop 0.822→0.643 (both harmful).

## Fixes implemented (working tree, uncommitted)

1. `frontend/src/landmarks.ts` — capture is now **time-boxed (3.5 s)** over
   unique video frames (dedupe via `video.currentTime`, fixes RC-B), collects
   the whole performance (RC-A), prompt text "perform the sign now".
   `CAPTURE_WINDOW_MS=3500`, `MIN_CAPTURE_FRAMES=30`; all prior error messages
   and the deadline path preserved.
2. `frontend/src/views/Live.tsx` — **release-based commit gate**
   (`resolveCommit`): one performance = one commit; same label re-observed is
   suppressed until a release window (uncertain/no-sign/below-gate) re-arms it;
   Single-sign click always commits (`freshAttempt`); continuous loop now
   survives up to 3 consecutive bad windows instead of dying on the first;
   prompts guide release between signs; default gate **70→60**
   (`DEFAULT_THRESHOLD_PERCENT`, also used by Settings).
3. **TTS policy** — sign words queue (never cancel an in-flight sentence);
   sentences/replay interrupt; single-sign sentence echo suppressed
   (`isEchoOfLastSpoken`).
4. WS path verified end-to-end against the live server (below).

## Regression suites (all green)

- frontend: `npm test` → **38/38** (6 new: commit-gate + threshold default)
- typecheck: `npx tsc --noEmit` → clean
- backend: `py -3 -m pytest tests/ -q` → **102/102** (incl. 12 WS scenarios)
- live WS probe: session → `Ready` → `Tracking` → 45 frames → prediction
  from `4.0.0`; synthetic input correctly gated `Uncertain` @ 0.248.

## Reproduce the evidence

```bash
py -3 scripts/eval_webcam_sim.py            # table above (n=1500, ~2 min)
py -3 scripts/eval_webcam_sim.py --thr 0.7  # old gate for comparison
```

## Manual webcam protocol (required — no camera in CI)

Camera hardware is not available to CI, so the pixel-level half must be
measured once on a real device:

1. `npm run dev` + backend on :8000; open Live; Enable Camera; accept token.
2. **Single-sign accuracy**: pick 5 signs (2 fast-dynamic, 2 slow-dynamic,
   1 short). For each, press Single Sign and perform it ONCE —
   no repeats. 5 trials per sign (25 total). Record: label accepted? conf?
   Expected band after the fix: ~65–75% visible-correct, of accepted ≥ ~89%.
3. **One-sign-one-result**: hold one sign for 10 s in continuous mode.
   Expected: exactly 1 sequence entry (was: ~4 with the old cooldown), 1 speech.
4. **Intentional repeat**: sign A, release (hands down 2 s), sign A again.
   Expected: 2 entries (release re-arms the gate).
5. **5-sign sentence** in continuous mode (e.g. HELLO → HOW → ARE → YOU →
   TODAY): record entries vs intended (misses/duplicates) and whether speech
   says each word once, then the sentence once.
6. Note WS vs REST path (state pill) — a "used REST fallback" note is a
   logged degradation, not a failure.

## Honest caveats

- Offline replay consumes **h5 landmark sequences**, not webcam pixels;
  MediaPipe extraction quality on a real device (lighting, angle, distance)
  is only covered by the protocol above.
- 0.90 release gates remain open debt (see `Docs/M11_GATE_109REAL.md`);
  nothing here claims those.
- Idle/head delay costs accuracy vs the ideal window (0.769 vs 0.822) — that
  is the accepted design point after measuring trim/settle as harmful.
