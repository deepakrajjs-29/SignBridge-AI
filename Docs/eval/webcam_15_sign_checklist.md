# 15-Sign Live Webcam Checklist

**Status: PARTIALLY OBSERVED — 7 of 15 rows have no recorded automatic primary; no aggregate accuracy claimed.**  
Live observations recorded below and in `Docs/37_Results_Analysis_SignBridge_AI.md` §17.1. Rows were also written to `Docs/eval/webcam_truth.csv` as attempt IDs `C01`–`C15` (plus extra trial `X01` = Police). A row counts as PASS only when the automatic primary exactly equals Expected — suggestions are never counted as correct. Unverified rows are excluded from any correctness count.

Model under test: `SBAI-MDL-ISL-4.0.0` (109 classes). Labels verified against `data/dataset/annotations/class_map.csv`.

## How to run

1. Backend: `cd backend && py -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
2. Frontend: `cd frontend && npm run dev` → open http://127.0.0.1:3000
3. Live Translator → enable camera → **Single Sign** (or Continuous).
4. Perform the sign; note Primary prediction + confidence %.
5. If “Recognition uncertain” appears, note the top alternative and whether you confirmed it.
6. Mark Correct = Yes only when the **automatic** primary equals Expected (a confirmed alternative is **not** an automatic pass).
7. Save notes; optionally paste finished rows into `webcam_truth.csv`.

## Selection rationale

Balanced: greetings, daily actions, college/education vocabulary, place words, and easily-confused pairs (Market/Big, Go/Walk, Sit/Stay).

| # | Expected class | Expected word | Auto primary | Conf % | Alt shown? | Correct (auto)? | Notes / failure mode |
|--:|----------------|---------------|--------------|-------:|------------|-----------------|----------------------|
| 1 | ISL_001 | Hello | *not_observed* | 8.2* | Yes — Go / Child / T / Hello | Unverified | primary not captured; *conf attached to Hello suggestion (attachment not disambiguated); suggestions ≠ auto pass |
| 2 | ISL_002 | Thank You | *not_observed* | 11.4* | Yes — Thank You as suggestion | Unverified | primary not captured; *conf attached to suggestion |
| 3 | ISL_003 | Please | *unverified* | *unverified* | *unverified* | Unverified | no reliable observation recorded — nothing invented |
| 4 | ISL_004 | Market | What | 100 (Market 34) | — | No | automatic primary incorrect; Market expected-sign conf 34 |
| 5 | ISL_011 | Help | YOU | Help 12.4 | — | No | automatic primary incorrect; Help expected-sign conf 12.4 |
| 6 | ISL_012 | Water | *not_observed* | 9.6 | — | Unverified | primary not captured; conf displayed-box reading |
| 7 | ISL_028 | School | *not_observed* | 26.7 | — | Unverified | primary not captured; conf displayed-box reading |
| 8 | ISL_035 | Go | Walk | 4.7 | — | No | confusable with Walk — incorrect |
| 9 | ISL_039 | Student | *none reported* | *not_observed* | — | No (no output) | sign not recognized; no prediction reported |
| 10 | ISL_045 | Teacher | Baby / Hero (primary not disambiguated) | *not_observed* | Yes — Baby / Hero | No | both displayed predictions wrong; Teacher conf not reported |
| 11 | ISL_046 | Sit | Teacher | *not_observed* | — | No | pair with Stay — incorrect; Sit conf not reported |
| 12 | ISL_049 | Book | *not_observed* | 13.5 | — | Unverified | primary not captured; conf displayed-box reading |
| 13 | ISL_055 | Stay | *none displayed* | *not_observed* | — | No (no output) | pair with Sit — nothing appeared; tester reports Stay not available in sign list (dataset class_map does define ISL_055 = Stay — UI-side availability, not independently re-verified) |
| 14 | ISL_060 | Walk | *not_observed* | 14.7 | — | Unverified | pair with Go — primary not captured; conf displayed-box reading |
| 15 | ISL_097 | Big | Family | 23.7 | — | No | confusable with Market — incorrect |

Additional trial **outside** the 15 (kept separate, not counted above): **Police (ISL_107)** — automatic primary `What`; Police conf 0.2% → incorrect. Recorded as `X01` in `webcam_truth.csv`.

## Honest limits

- 15 signs **do not** prove all 109 classes work live.
- Frozen offline test accuracy remains **81.29%** argmax (n=3629, `Docs/eval/08_final_test.json`) — **not** 90%.
- Automated suite PASS ≠ live webcam accuracy.

## Result summary (counts only — no accuracy percentage)

- Passed (exact automatic match): **0 / 15**
- Incorrect automatic primary: **6 / 15** (#4 Market, #5 Help, #8 Go, #10 Teacher, #11 Sit, #15 Big)
- No output / not recognized: **2 / 15** (#9 Student, #13 Stay)
- Unverified (observation missing — not counted as correct): **7 / 15** (#1, #2, #3, #6, #7, #12, #14)
- Not run: **0 / 15**
- Extra trial (outside the 15, not counted): Police (ISL_107) — incorrect (primary What)
- Static-held vs naturally-moving live comparison: **PENDING** — no such split exists in project artifacts
- Gemini real-API A/B test: **PENDING** — not performed
- Tester name / date: **not provided** (manual session; date not captured)
