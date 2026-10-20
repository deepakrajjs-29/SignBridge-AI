# Webcam Protocol Attempt Deck (M13 §13)

Truth sheet: Docs/eval/webcam_truth.csv (attempt_id + expected_class_id pre-filled).
Fill displayed_* from the SCREEN (nothing from memory).

- displayed_label: exact word text shown (e.g. Hello, Thank You); empty if nothing shown.
- displayed_state: Recognized | Provisional | Uncertain | No-Sign (as shown).
- displayed_conf: integer percent in the Confidence box (e.g. 90).
- flips_in_attempt: pre-filled 0; overwrite with the actual change count during the attempt.
- Verify Settings shows AUTOMATIC mode (no manual threshold override) before starting.

## Part 1 — 80 Single-mode attempts (20 signs x 4, shuffled; seed 20261019)

- A001: **ISL_004 = Market**
- A002: **ISL_025 = Time**
- A003: **ISL_004 = Market**
- A004: **ISL_061 = Bread**
- A005: **ISL_041 = Father**
- A006: **ISL_085 = Lion**
- A007: **ISL_071 = Good Evening**
- A008: **ISL_025 = Time**
- A009: **ISL_042 = Child**
- A010: **ISL_025 = Time**
- A011: **ISL_075 = I**
- A012: **ISL_012 = Water**
- A013: **ISL_085 = Lion**
- A014: **ISL_032 = What**
- A015: **ISL_019 = House**
- A016: **ISL_004 = Market**
- A017: **ISL_056 = Wait**
- A018: **ISL_071 = Good Evening**
- A019: **ISL_063 = Road**
- A020: **ISL_032 = What**
- A021: **ISL_032 = What**
- A022: **ISL_081 = Pizza**
- A023: **ISL_063 = Road**
- A024: **ISL_004 = Market**
- A025: **ISL_048 = Boy**
- A026: **ISL_075 = I**
- A027: **ISL_042 = Child**
- A028: **ISL_085 = Lion**
- A029: **ISL_012 = Water**
- A030: **ISL_019 = House**
- A031: **ISL_041 = Father**
- A032: **ISL_092 = Sunday**
- A033: **ISL_092 = Sunday**
- A034: **ISL_092 = Sunday**
- A035: **ISL_081 = Pizza**
- A036: **ISL_061 = Bread**
- A037: **ISL_019 = House**
- A038: **ISL_046 = Sit**
- A039: **ISL_044 = Eat**
- A040: **ISL_061 = Bread**
- A041: **ISL_043 = Car**
- A042: **ISL_063 = Road**
- A043: **ISL_044 = Eat**
- A044: **ISL_092 = Sunday**
- A045: **ISL_071 = Good Evening**
- A046: **ISL_025 = Time**
- A047: **ISL_056 = Wait**
- A048: **ISL_053 = Why**
- A049: **ISL_048 = Boy**
- A050: **ISL_041 = Father**
- A051: **ISL_044 = Eat**
- A052: **ISL_053 = Why**
- A053: **ISL_043 = Car**
- A054: **ISL_043 = Car**
- A055: **ISL_081 = Pizza**
- A056: **ISL_019 = House**
- A057: **ISL_044 = Eat**
- A058: **ISL_061 = Bread**
- A059: **ISL_048 = Boy**
- A060: **ISL_056 = Wait**
- A061: **ISL_085 = Lion**
- A062: **ISL_042 = Child**
- A063: **ISL_081 = Pizza**
- A064: **ISL_012 = Water**
- A065: **ISL_046 = Sit**
- A066: **ISL_032 = What**
- A067: **ISL_056 = Wait**
- A068: **ISL_041 = Father**
- A069: **ISL_046 = Sit**
- A070: **ISL_075 = I**
- A071: **ISL_042 = Child**
- A072: **ISL_071 = Good Evening**
- A073: **ISL_048 = Boy**
- A074: **ISL_075 = I**
- A075: **ISL_012 = Water**
- A076: **ISL_046 = Sit**
- A077: **ISL_063 = Road**
- A078: **ISL_053 = Why**
- A079: **ISL_043 = Car**
- A080: **ISL_053 = Why**

## Part 2 — stress rows

- H1-H4: hold **ISL_001 = Hello** continuously for >= 8 s (one attempt each). Expect exactly 1 commit.
- R1-R3: sign **ISL_002 = Thank You** three times in a row (one row per repeat). Expect one commit each.
- S1-S5: ONE sentence in Continuous mode, words in order: **Hello -> Please -> Help -> Yes -> Thank You**. One row per word; displayed_label = word text as it appeared (empty if missed).

## After all rows

    py -3 scripts/eval_webcam_report.py --truth Docs/eval/webcam_truth.csv --out Docs/eval/webcam_report.json
