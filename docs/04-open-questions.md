# 04 — Open questions & next steps

## Q1. Does each camera have its own serial number that must match the drone?

**Each camera does have its own SN.** The core board keeps a lens-shading file for each of the four
fisheye cameras, named by a 14-character serial (redacted here), plus `vp_sensor_sn.txt`. The drone reads these serials
from the camera units at boot.

**Where the SN physically lives is not confirmed.** The calibrator's log shows
`save to eeprom error ret_code= 224` at startup, which suggests DJI's tooling expects some writable
storage in the vision chain. This project does not attempt to read or change camera serials.

**Do they have to "match"? Unknown. Circumstantial evidence suggests SN mismatch is not what's blocking the drone, but this is not proven:**

- A replacement module's **right** forward camera streams a perfect image, so the drone appears to run a
  camera it has not seen before (assumes its SN differs; the SNs were not compared).
- Only the **forward** pair is flagged (`1A510381`). If every new SN were rejected, other cameras on the
  replacement module might be flagged too (reasoning, not tested).
- The flagged pair is the one containing the camera that outputs noise.

**Why changing the SN would probably be the wrong fix (reasoning, untested):** the core board's `cali_*.txt` files belong to the
*old* cameras. Making new cameras report old serials would make the drone apply the old lenses'
geometry to new lenses. Distance estimates would be silently wrong. The better approach is new calibration
for the new cameras. DA2 has produced and pushed one for the downward pair only.

**How to check (later):** read the per-camera SNs over DUML (`0x00/0x51 Get SN`, read-only) or from a
fresh log export, and compare them with the lens-shading file names.

## Q2. Forward-pair calibration

Requirements to calibrate `cali_cd.txt` properly:

- Image size **1024×1152** (confirmed from recording) instead of 640×480.
- A **fisheye** intrinsic model (`Equidistant` or `Ftheta_opencv`; both are compiled into the DLL) instead
  of `Opencv` pinhole.
- Correct nominal focal length and baseline for the forward pair (unknown: derive from frames or from
  the factory `cali_cd.txt`).
- The `cali_cd.txt` format the drone's perception expects. Unknown: the on-board file is encrypted in
  log exports. Options: obtain it via FTP once DA2 enables FTP, or infer it from DJI's other fisheye
  configurations.

Alternative: capture frames with recording mode and calibrate offline with OpenCV's fisheye model, then
write a `cali_cd.txt` in the right format and push it.

## Q3. Remaining sensors

| Pair | Status |
|---|---|
| `ab` downward | ✅ Calibrated via DA2 and pushed |
| `cd` forward | In progress. Frames captured via the patched calibrator (right clean, left noise). Calibration not attempted; cause of the left-camera noise not yet confirmed |
| `de`, `ef`, `fc` (sides/rear) | Not yet investigated. No topic names or captures. Contributions welcome |

## Next actions

1. **Hardware (if you hit the noise symptom):** inspect the front-left camera flex, then run the light test
   from [01-diagnosis.md](01-diagnosis.md).
2. Once front-left gives an image: confirm resolution and format, and pick the fisheye model.
3. Extend `patch_front.py` to also set image size, nominal focal and baseline, and the intrinsic model.
4. Find out the expected `cali_cd.txt` format before pushing anything.
5. Document the side and rear pairs the same way.
6. Keep this repository free of DJI binaries: docs and the patch script only.
