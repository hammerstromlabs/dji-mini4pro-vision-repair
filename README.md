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

DJI Fly's calibrate option is restricted to authorised technicians, and DJI Assistant 2 does not
officially offer vision calibration for this aircraft.

## What is established (tested on one aircraft)

1. **Calibration is stored on the main (core) board, not on the sensor module.** Files are kept per
   stereo pair: `cali_ab` (downward), `cali_cd`, `cali_de`, `cali_ef`, `cali_fc` (the four fisheye
   cameras), plus per-camera lens-shading files named by each camera's serial number.
2. **DJI Assistant 2 2.1.42 already ships a full PC-side vision calibrator that supports the Mini 4 Pro.**
   It is hidden by one switch in a settings file (`vision_enable`). Enabling it let me calibrate the
   **downward** pair with a monitor and push the result to the drone: RMS reprojection error 0.168 px,
   baseline 37.91 mm versus a nominal 38.0 mm.
3. The calibrator also contains a forward-pair path (`raw/front/*` → `cali_cd.txt`), but it is
   configured for a different DJI model. A 5-byte patch retargets the Mini 4 Pro's pair at the forward
   cameras. That patched build is for **capturing frames only**; see the limitation in
   [docs/03-procedures.md](docs/03-procedures.md).
4. With that patch the forward cameras stream **1024×1152, 8-bit grayscale fisheye**. On my replacement
   module the right camera produced a clean image and the **left camera produced pure noise** (valid
   frame headers, no image). That, and not a serial-number mismatch, is the most likely cause of the
   forward-calibration error on that unit. See [examples/](examples/).

## Status and what is left

- **Cameras:** in the author's testing the vision cameras could be brought up through Assistant 2's
  calibrator. The one failure, a front-left camera that outputs noise, was traced to the **replacement
  camera module, not to Assistant 2 or this method.** Documented evidence in this repo covers the downward
  pair (`raw/down/*`) and forward pair (`raw/front/*`) only; topic names and captures for the side and rear
  cameras are not written up yet (contributions welcome).
- **Forward, side and rear calibration have not been completed end to end.** The calibrator's defaults
  are for a 640×480 pinhole pair, so those pairs still need a fisheye intrinsic model, the 1024×1152
  image size (forward pair), correct nominal focal/baseline values, and the `cali_cd.txt` format the drone
  expects (unknown; on-board files are encrypted in log exports). A working forward run also needs a
  healthy camera pair.
- The findings come from a single aircraft and a single Assistant 2 build (2.1.42, calibrator DLL
  v2.5.0.7). Other builds will have different addresses; the patch script refuses to run on them.

## Why this may help beyond one drone

The calibrator is table-driven: [docs/02](docs/02-how-da2-calibration-works.md) documents the per-model
table inside the DLL (image topic, image size, nominal focal length, baseline, intrinsic model, output
file) and the result-file format. Adding or retargeting a camera pair means changing those entries. If
you have a different drone or camera module, that is the starting point.

## Contents

| Path | What |
|---|---|
| [docs/01-diagnosis.md](docs/01-diagnosis.md) | Error codes, on-board file layout, and the left-camera noise test |
| [docs/02-how-da2-calibration-works.md](docs/02-how-da2-calibration-works.md) | USB interfaces, calibrator flow, per-model config table, result format, debug switches |
| [docs/03-procedures.md](docs/03-procedures.md) | Enable the hidden calibration, patch, safety switches, record frames, **revert to stock** |
| [docs/04-open-questions.md](docs/04-open-questions.md) | Camera serials, forward fisheye calibration, next steps |
| [tools/](tools/) | Python scripts for the analysis and the byte patch |
| [examples/](examples/) | One sample frame showing what a "noise" camera channel looks like |
| [DISCLAIMER.md](DISCLAIMER.md) | Safety, legal and warranty notes |

## Contributing

Results from other aircraft, Assistant 2 versions or camera modules are very welcome, especially: working
forward-pair parameters, the `cali_cd.txt` format, and side/rear topic names. Please **do not** attach DJI
binaries, firmware, encrypted log exports, your drone's calibration files, or camera frames showing your
surroundings. Redact serial numbers.

## License

[MIT](LICENSE).
