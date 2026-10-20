# Image Reference Audit — 109 ISL Classes

Date: 2026-10-20

## Canonical sources

| Source | Path | Rows |
|--------|------|------|
| Class map (labels) | `data/dataset/annotations/class_map.csv` | 109 (`ISL_001`…`ISL_109`) |
| Asset manifest | `data/assets/manifest.csv` | 109 |
| Reference status | `data/assets/reference_status.csv` | 109 |
| Backend `/api/v1/classes` | `backend/app/deps.py::class_list()` | 109 + `asset_status` |
| UI runtime images | `frontend/public/assets/ISL_*.jpg` | 109 |
| Backend static mount | `data/assets/ISL_*.jpg` | 109 (identical MD5 to public) |

## Counts by status (`reference_status.csv`)

| Status | Count | Meaning |
|--------|------:|---------|
| `placeholder` | 50 | Synthetic label-card render (`ISL_001`–`ISL_050`) — shows correct word text, not a verified photo of the ISL sign |
| `dataset_render` | 51 | Landmark-skeleton render from training-pipeline extraction (`ISL_051`–`ISL_109` except blanks) |
| `needs_verified_reference` | 8 | Byte-identical near-blank JPEGs — **must not** be shown as if they were the sign |

### `needs_verified_reference` IDs

`ISL_053`, `ISL_063`, `ISL_065`, `ISL_069`, `ISL_071`, `ISL_080`, `ISL_081`, `ISL_108`

All eight share MD5 prefix `ef8f592a` (9,615 B). UI shows the **label + badge** instead of the blank image.

## UI behavior

- Vocab grid + modal (`frontend/src/views/Vocab.tsx`): `asset_status === "needs_verified_reference"` → large uppercase label + amber “Verified reference needed” badge (no misleading image).
- Broken image (`onError`) → label fallback (existing).
- Class cards still always show class ID + word label for all 109 entries.
- Header badge now reflects active model `SBAI-MDL-ISL-4.0.0 • SOFTMAX(109)`.

## Policy

No invented gestures. No reusing one image for different words. Unverified blanks are documented and degraded in the UI rather than fabricated.

## Regenerating status

```bash
py -3 -c "import csv; from pathlib import Path; print(sum(1 for _ in csv.DictReader(open('data/assets/reference_status.csv'))))"
```
