# DJI Mini 4 Pro — vision sensor calibration research

Unofficial reverse-engineering notes on how **DJI Assistant 2 (Consumer Drones Series)** calibrates
drone vision sensors, and how that machinery can be used on a **DJI Mini 4 Pro** (internal model code
`wa140`) whose vision module was replaced.

> **Not affiliated with, endorsed by, or supported by DJI.** DJI and related names are trademarks of
> their owners. This repository contains notes, scripts and measurements only. **It contains no DJI
> software, firmware or data files**, and you must not add any. See [DISCLAIMER.md](DISCLAIMER.md)
> before you touch your aircraft.

## The problem

After replacing a Mini 4 Pro's upper vision module, DJI Fly can show:

| Code | Message |
|---|---|
| `1A011342` | Vision system calibration error. Contact DJI Support |
| `1A510381` | Forward vision sensor calibration error. Auto calibration in progress... |
| `16200202` | Vision sensors calibration error. Unable to take off. Restart aircraft... |

Per the author, DJI Fly's calibrate option refused to run (reported as requiring an authorised technician;
not independently verified). Per the author, DJI Assistant 2 offers vision calibration for this aircraft for
the **lower (downward) assembly only**, as its default and only option.

## Observed so far (one aircraft, one software build)

Each item says how it was learned. Nothing here has been independently reproduced yet.

1. **Where calibration lives (inferred).** Encrypted log exports have plaintext file names showing
   per-pair calibration files (`cali_ab`, `cali_cd`, `cali_de`, `cali_ef`, `cali_fc`) and per-camera
   lens-shading files named by serial number, held on the core board's perception processor. The file
   *contents* are encrypted, so this is inferred from names only.
2. **Assistant 2's calibrator is single-pair for this aircraft (read from the install).** DJI Assistant 2
   (Consumer Drones Series) V2.1.42 contains a vision calibrator DLL with a Mini 4 Pro (`wa140`) entry for
   one pair, the downward pair (`raw/down/*` writing `cali_ab.txt`), and its UI code forces the single-pair
   flow for `wa140` (`cameraIndex=0, count=1`). The stock `defaultsettings.ini` has `[wa140]
   vision_enable=0`; **what that flag gates is not verified** (see Ongoing).
3. **Downward pair: calibrated and pushed (tested).** Using Assistant 2's calibrator (with
   `vision_enable=1` set at the time), the downward pair
   calibrated with a monitor and the result was pushed to the drone: RMS reprojection error 0.168 px,
   baseline 37.91 mm against a nominal 38.0 mm. This documents the calibration result only; it does not
   include a flight test of the outcome.
4. **Forward cameras can be streamed by retargeting the calibrator (tested).** A 5-byte patch points the
   Mini 4 Pro entry at `raw/front/*`. The frames recorded were **1024x1152, 8-bit grayscale,
   fisheye-distorted**.
5. **On the replacement module tested, one forward channel produced no image (recorded).** The right
   camera produced a clean image; the left produced uniform noise (with header-like bytes at the start of some frames)
   (statistics in [docs/01](docs/01-diagnosis.md), sample in [examples/](examples/)). The cause is **not
   yet confirmed**: a hardware fault in that camera or its flex is the leading suspect, but no light test
   or module swap has been done. A serial-number mismatch looks less likely because the right camera on the
   same module worked.

## Ongoing / not yet discovered

- **Forward-pair calibration** has not been attempted end to end. It likely needs a fisheye intrinsic
  model, the 1024x1152 image size, correct nominal focal length and baseline, and the `cali_cd.txt` format
  the drone expects (unknown; on-board files are encrypted in log exports). It also needs a working camera
  pair.
- **Side and rear pairs** (`cali_de`, `cali_ef`, `cali_fc`): not investigated. Their image topic names are
  unknown and no frames have been captured.
- **What `vision_enable` does for the Mini 4 Pro.** The stock value is `0` and the UI reads it into a
  `visionEnable` setting, but it has not been tested whether the downward calibration appears with the
  stock value. The author reports the lower-assembly calibration is available by default, which would make
  the edit unnecessary.
- **Whether the drone accepts** a self-generated forward calibration is unknown.
- **Other Assistant 2 builds and other drones** have not been checked. The patch script refuses to run on
  any DLL other than the one it was written for.

## Why this might help beyond one drone

The calibrator is table-driven: [docs/02](docs/02-how-da2-calibration-works.md) documents the per-model
table inside the DLL (image topic, image size, nominal focal length, baseline, intrinsic model, output
file) and the result-file format. Retargeting the pair for the Mini 4 Pro's forward cameras worked at the
level of streaming frames; whether a different drone or camera module can be added this way is an open
question, not a result.

## Contents

| Path | What |
|---|---|
| [docs/01-diagnosis.md](docs/01-diagnosis.md) | Error codes, on-board file layout, and the left-camera noise test |
| [docs/02-how-da2-calibration-works.md](docs/02-how-da2-calibration-works.md) | USB interfaces, calibrator flow, per-model config table, result format, debug switches |
| [docs/03-procedures.md](docs/03-procedures.md) | Downward calibration, forward-capture patch, safety switches, record frames, **revert to stock** |
| [docs/04-open-questions.md](docs/04-open-questions.md) | Camera serials, forward fisheye calibration, next steps |
| [tools/](tools/) | Python scripts for the analysis and the byte patch |
| [examples/](examples/) | One sample frame showing what a "noise" camera channel looks like |
| [DISCLAIMER.md](DISCLAIMER.md) | Safety, legal and warranty notes |

## Contributing

Results from other aircraft, Assistant 2 versions or camera modules are very welcome, especially: working
forward-pair parameters, the `cali_cd.txt` format, and side/rear topic names. Please say how you
verified each claim (log, capture, command). Please **do not** attach DJI
binaries, firmware, encrypted log exports, your drone's calibration files, or camera frames showing your
surroundings. Redact serial numbers.

## License

[MIT](LICENSE).
