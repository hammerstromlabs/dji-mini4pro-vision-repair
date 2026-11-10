# 01 — Diagnosis

## Hardware & history

- Aircraft: DJI Mini 4 Pro (`wa140`).
- The upper vision sensor module was replaced with one **taken from a donor Mini 4 Pro**.
- The module is a set of individual camera units, each on its own small flex, joined to a larger
  flex that carries every camera's channel to the core board.

## Error codes (DJI Fly)

| Code | Text | Interpretation |
|---|---|---|
| `1A011342` | Vision system calibration error. Contact DJI Support | Overall vision self-check failed |
| `1A510381` | Forward vision sensor calibration error. Auto calibration in progress... | Only the **forward pair** is flagged; the online self-calibration (`*.selfcali`) is trying and failing |
| `16200202` | Vision sensors calibration error. Unable to take off | Flight controller takeoff lock that follows from the vision fault |

## Evidence from exported logs

DJI Assistant 2 log export produces `DJI_Mini_4_Pro_<date>.DAT` archives. Their contents are encrypted
(`*.enc`), but **file names and the per-archive header are plaintext**, which is enough to map out the
on-board layout (inferred from names only). On the E1E processor (`perception/dji_perception/`):

- Stereo calibration per pair: `cali_ab.txt`, `cali_cd.txt`, `cali_de.txt`, `cali_ef.txt`, `cali_fc.txt`.
  Each has a `.txt.1` backup and `.selfcali` variants written by in-flight self-calibration.
- `vp_sensor_sn.txt`, `fpn_sn.txt`, `json/calibration_factory_cali.json`, `json/calibration_module_paras.json`.
- Lens-shading files **named by camera serial number**, one per fisheye camera:
  `<14-char camera SN>.lsc` (serials redacted).
- ToF (downward distance sensor) data in a directory named by its own SN (redacted).
- HMS logs: `vp_hms.log`, `hms/hms_01.log`.

Pair naming is partly a guess: `ab` = downward pair (consistent with the calibrator writing `cali_ab.txt`
from `raw/down/*`) and `cd` = forward pair (consistent with the patched run using `raw/front/*`). That
`c,d,e,f` are the four fisheye cameras chained as front, side, rear, side is unverified.

## The left-camera finding

On the unit tested (observed 2026-10-20), using the patched calibrator (see [03-procedures.md](03-procedures.md)) with recording mode on, 58 frames were captured
from each forward camera (`raw/front/left`, `raw/front/right`).

| Metric | Front-right | Front-left |
|---|---|---|
| Image | Clean 1024×1152 fisheye view of the room | Uniform "TV static" |
| Brightness range across 10×16 blocks | 8.8 – 158.0 | 142.1 – 146.0 (flat) |
| Adjacent-pixel correlation (H / V) | +0.96 / +0.98 | −0.005 / +0.006 |
| Spatial correlation in any single bit plane | 0.06 – 0.93 | ~0.00 in all 8 bits |
| Header row (frame counter / timestamp) | Present | Present, appears in sync with right |

What the data shows: the left channel delivers frames with a plausible metadata header, but the pixel
payload is statistically indistinguishable from random noise (no spatial correlation in any bit plane),
so a different decoding of the same bytes is unlikely to recover an image.

What is **not** established:

- Whether this noise is what triggers `1A510381`. It is plausible (the flagged pair contains this camera),
  but it was not tested.
- The cause. Untested possibilities: a poorly seated or damaged flex/connector on the front-left branch;
  a damaged front-left camera or its board; a sensor configuration problem (less likely, since the right
  camera on the same module works). No light test, reseat comparison or module swap has been recorded.

Script: [`tools/noise_stats.py`](../tools/noise_stats.py). A sample front-left frame is in
[`examples/front-left-noise-frame.png`](../examples/front-left-noise-frame.png).

## Next diagnostic steps

1. Reseat the upper-module flex at the core board (done before the recording above, so the noise
   persisted with a seated cable). Then inspect the front-left branch under
   magnification for creases, tears, corrosion or bent pins.
2. Light test: record while alternately covering the front-left lens and shining a light into it. If the
   noise statistics don't change, the camera or its link is dead.
3. If the original upper module is available, compare it or swap the camera.
