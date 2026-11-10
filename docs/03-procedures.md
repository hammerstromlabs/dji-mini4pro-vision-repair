# 03 — Procedures

All paths below are relative to
`C:\Program Files (x86)\DJI Product\DJI Assistant 2 (Consumer Drones Series)\DJIEngine\`.
Close DJI Assistant 2 completely before changing any file.

## A. Calibrate the downward pair — tested, works

> **Check first whether you need the settings edit.** The stock `defaultsettings.ini` has `[wa140]
> vision_enable=0`, and the author reports Assistant 2 already offers the lower-assembly calibration by
> default. It is **not verified** whether the downward calibration appears without the edit. Try the stock
> install first; only apply step 2 if the option is missing.

1. Install DJI Assistant 2 (Consumer Drones Series) 2.1.42 and sign in.
2. In `defaultsettings.ini`, change
   ```ini
   [wa140]
   vision_enable=0
   ```
   to `vision_enable=1`.
3. Restart DA2, connect the drone over USB (fan on it), and open the vision calibration.
4. Follow the on-screen pattern steps. On success DA2 pushes `cali_ab.txt` and asks you to restart the
   aircraft.

Result on our aircraft: RMS 0.168 px, baseline 37.91 mm (nominal 38.0).

## B. Point the calibrator at the forward cameras — experimental

Patch `DJIVisionCalibration3.dll` (sha1 `ddbcbdd09d459aad2f13e8d285e5b6504c5787e4`) with
[`tools/patch_front.py`](../tools/patch_front.py). It verifies the original bytes before writing:

| VA | Original | New | Meaning |
|---|---|---|---|
| `0x10089F18` | `cali_ab.txt` ptr | `cali_cd.txt` ptr | Output file (protects the good downward file) |
| `0x10089FC9` / `0x10089FCB` | len 0x0d, `raw/down/left` | len 0x0e, `raw/front/left` | Left topic |
| `0x1008A00B` / `0x1008A00D` | len 0x0e, `raw/down/right` | len 0x0f, `raw/front/right` | Right topic |

```
python tools/patch_front.py DJIVisionCalibration3.dll.orig DJIVisionCalibration3.front.dll
```

Patched sha1: `6d7db4c7f32cb3f349ea02106847d74da5cd2ad9`. Copy it over `DJIVisionCalibration3.dll`
(admin rights needed).

**Known limitation:** this patch keeps the Mini 4 Pro's downward parameters (640×480, focal 245, baseline
38 mm, pinhole model). The forward cameras are 1024×1152 fisheye, so this build is for **capturing
frames only**. Do not run a forward calibration to completion with it.

## C. Safety switches (always use with experimental builds)

```powershell
Set-Content TESTFLAG_CALIFAIL.txt 1     # nothing gets pushed to the drone
Set-Content TESTFLAG_SAVRESULT.txt 1    # dump intermediate results
```

## D. Record raw camera frames

In `config.ini`:

```ini
[DJIVisionCalibrationWorker]
recordSetting.mode=1
```

Start the calibration and wait on the camera-image screen for 20–30 s. Frames are saved as PNG to
`record\0\N.png` (left) and `record\1\N.png` (right). Mode `2` replays a recording (not yet tested).

## E. Revert everything to stock

Take your own backups **before** changing anything (copy the original `DJIVisionCalibration3.dll`,
`defaultsettings.ini` and `config.ini` somewhere safe). They are not provided here.

```powershell
$E = "C:\Program Files (x86)\DJI Product\DJI Assistant 2 (Consumer Drones Series)\DJIEngine"
$B = "<folder where you saved your own backups>"
Copy-Item -Force "$B\DJIVisionCalibration3.dll" "$E\DJIVisionCalibration3.dll"
Copy-Item -Force "$B\defaultsettings.ini"      "$E\defaultsettings.ini"
Remove-Item "$E\TESTFLAG_*.txt"
(Get-Content "$E\config.ini") -replace 'recordSetting.mode=\d','recordSetting.mode=0' | Set-Content "$E\config.ini"
```

Run this in an **administrator** PowerShell. Reinstalling DA2 also restores the stock files.
