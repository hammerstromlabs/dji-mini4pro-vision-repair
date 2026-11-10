# Tools

Python 3.12 scripts. Install the dependencies with `pip install pefile capstone numpy pillow`.
Run them against **your own copies** of files from your own DJI Assistant 2 installation.

| Script | Purpose | Usage |
|---|---|---|
| `xrefs.py` | Find code that references given strings in a 32-bit PE and print the surrounding disassembly | `python xrefs.py <dll> <string> [string...]` |
| `disasm.py` | Disassemble a VA range, annotating string and double constants | `python disasm.py <dll> <start_va_hex> <end_va_hex>` |
| `patch_front.py` | Build a forward-camera copy of `DJIVisionCalibration3.dll` (v2.5.0.7, sha1 `ddbcbdd0...e4`). Refuses to run on a different build. **Capture only; do not complete a calibration with it** | `python patch_front.py <orig.dll> <out.dll>` |
| `noise_stats.py` | Compare recorded camera frames: brightness, spatial and bit-plane correlation, frame changes | `python noise_stats.py <record_dir>` (expects `0/` and `1/` subfolders) |

Do not commit the DLLs or their outputs.
