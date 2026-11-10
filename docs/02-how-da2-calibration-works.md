# 02 — How DJI Assistant 2's vision calibration works

All findings are from **DJI Assistant 2 (Consumer Drones Series) 2.1.42** (Windows, released 2026-09-22),
installed at `C:\Program Files (x86)\DJI Product\DJI Assistant 2 (Consumer Drones Series)\`.

## USB interfaces of the drone

The Mini 4 Pro enumerates as `VID_2CA3 & PID_0020` (it also enumerates while powered off, on USB power alone).

| Interface | Function |
|---|---|
| MI_00 | RNDIS network. The drone is `192.168.42.2`, serves DHCP, and runs FTP on port 21 (login requires DA2 to enable it first via `ActionEnableFTPReq`) |
| MI_02 | Mass storage: `InternalStorage` (exFAT, ~2.2 GB) |
| MI_03 | **ss_dbus** — DJI's publish/subscribe transport, used for raw camera image streams |
| MI_05 | **DUML v1** command protocol. The calibrator talks to device type `0x12` index `0x04` (perception) |
| MI_04, 06, 07 | Other bulk interfaces (not yet identified) |

DA2 installs a libusb-win32 driver for MI_03–07. Without it there is no COM port and no access.

Plugging the drone into a PC puts it in USB mode: it won't link to the remote. The author found it got hot
on the bench (unmeasured) and used a fan; treat that as a precaution, not a characterised limit.

## The components

| File (under `DJIEngine\`) | Role |
|---|---|
| `defaultsettings.ini` | Per-model feature switches. `[wa140] vision_enable=0` hides calibration for the Mini 4 Pro |
| `DJIVisionCalibration3.dll` (v2.5.0.7, built 2024-09-05) | The calibrator: image capture, pattern detection, Ceres solver, result file |
| `dbus_pc.json` | Transport/topology config. `wa140` uses the `dual_chip_a7` profile |
| `DJIServices\DJIUavService.dll` | Pushes result files to the drone (`transfer_calibrate_result_file`); knows `/cali_ab.txt` … `/cali_kl.txt` |
| `config.ini` | Calibrator settings. `recordSetting.mode`: 0 off, 1 record, 2 replay |
| `DJIApp\app.asar` | Electron UI. **Integrity-checked** via `HASH.FILES`/`HASH.SIG`; DLLs and INIs are not |

## Calibration flow

1. The UI (Electron) connects to the calibrator over a local websocket
   (`/controller/vision_calibration/<hash>`) and sends JSON commands:
   `vision_calibration_init {DEVICE:"wa140", WIDTH, HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT}` →
   `config_screen_size` → `set_cam_pair {INDEX}` → `enter_match_rect` → `enter_track` →
   `start_calculation`.
2. The calibrator sends `start dji_perception` to the drone over DUML (MI_05), then subscribes to two
   ss_dbus image topics over MI_03.
3. The monitor shows patterns while you move the drone. The calibrator detects them and solves the
   stereo pair with Ceres (Levenberg–Marquardt).
4. On `vision_calibration_calculation_ok`, the UI calls `transfer_calibrate_result_file`, which pushes
   the result file to the drone. DA2 then asks you to **restart the aircraft**.

For the Mini 4 Pro the UI hard-codes `cameraIndex = 0`, a 2-step flow.

## Per-model configuration inside `DJIVisionCalibration3.dll`

The function at VA `0x10089500`–`0x1008a3b0` builds a camera-pair list per model by string-comparing
the device name. Relevant fields:

| Model | Pairs | Topic | Size | Nominal focal | Nominal baseline | Model | Output |
|---|---|---|---|---|---|---|---|
| `wm169` | 1 | `raw/down/*` | 640×480 | — | 40 mm | Opencv | `cali_ab.txt` |
| `ag701` pair 1 | 2 | `raw/down/*` | — | — | 130 mm | Opencv | `cali_ab.txt` |
| `ag701` pair 2 | | **`raw/front/*`** | **1280×960** | 475 | 130 mm | Opencv | **`cali_cd.txt`** |
| `wa233` | 1 | `raw/down/*` | — | — | 60 mm | Opencv | `cali_ab.txt` |
| **`wa140`** | 1 | `raw/down/*` | 640×480 | 245 | **38 mm** | Opencv | `cali_ab.txt` |
| `wa234` | 1 | `visp/down/*` | — | — | 60.5 mm | Opencv | `cali_ab.txt` |
| `wa150` | 1 | `visp/down/*` | — | — | 36 mm | Opencv | `cali_ab.txt` |

Camera models compiled into the DLL: `Equidistant`, `Pinhole`, `Pinhole_opencv`, `Pinhole_opencvext`,
`Pinhole_opencvk4`, `Ftheta_opencv`. The fisheye-capable ones (`Equidistant`, `Ftheta_opencv`) exist
but none of the configs above use them.

## Result file format (`cali_ab.txt`, as produced for the Mini 4 Pro downward pair)

```
image_size: 640 480
rotation_left_in_right_euler_deg:
-0.412445 -0.146507 0.537403
translation_left_in_right:
-0.133571 -37.9139 -0.00775907
intrinsic_model: pinhole_opencv
camera0:            # 3x3 K
camera1:
coeffs0: / coeffs1: # k1 k2 p1 p2 k3
_R:  _P0:  _P1:  _R0:  _R1:   # rectification
create_time: ...
creator: user 2.5.0.7
cali_rms: 0.167768
```

## Debug switches found in the calibrator

Create these files in `DJIEngine\`:

| File | Effect |
|---|---|
| `TESTFLAG_CALIFAIL.txt` | Forces the calibration result to "fail", so **nothing is pushed** to the drone |
| `TESTFLAG_SAVRESULT.txt` | Dumps intermediate results at the calculation step |
| `TESTFLAG_SCNGETFAIL.txt` | Simulates a screen-size detection failure |

## Other leads

- `DJIUavService.dll` contains `DownloadCameraCalibrationFileBySn` / `OnCalibrationFileNeedUpgradeReq`:
  the drone can ask DA2 to download factory calibration **by camera SN** from DJI's servers. It's unclear
  whether this covers vision cameras or only the main gimbal camera.
- DUML general command set: `0x00/0x51` Get Serial Number (documented by the o-gs/dji-firmware-tools
  dissectors). Read-only; not yet tested on this aircraft.

## Open: adapting the calibrator to another camera pair

Not attempted. The per-model table above suggests the inputs a pair needs: image topics, image size,
nominal focal length, baseline, intrinsic model and output filename. Which of these the drone's perception
stack requires, and whether it will accept the result for a pair other than the downward one, is unknown.
Only the Mini 4 Pro's downward pair has been calibrated and pushed.
