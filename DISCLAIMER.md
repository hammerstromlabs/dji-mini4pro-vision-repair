# Disclaimer

## Safety

A drone with wrong vision calibration can misjudge distances to obstacles and drift while hovering,
**without warning you**. Vision positioning and obstacle sensing are safety systems.

- Do not trust a calibration you produced yourself until you have verified it: hover low over a textured
  surface, check for drift, then test obstacle sensing at walking speed with a soft target, in an open
  area away from people and property.
- Never push a calibration result computed with a build whose parameters do not match the cameras (for
  example the forward-capture patch). Use the `TESTFLAG_CALIFAIL.txt` switch described in
  [docs/03-procedures.md](docs/03-procedures.md) with every experimental build.
- Calibration files describe one specific set of lenses. **Do not copy another aircraft's calibration
  files onto yours**; the result is silently wrong geometry.
- Plugging a drone into a PC for calibration can cause it to overheat within minutes. Keep a fan on it.

## Warranty, regulations, support

- Modifying DJI software settings, or using unofficial calibration, may void your warranty, may be
  rejected by DJI service, and may not be permitted where you fly. You are responsible for complying with
  the aviation rules that apply to you.
- This is a research and repair-interoperability project. It is not intended to help bypass flight
  restrictions, geofencing, remote identification, or any safety or regulatory feature, and no part of it
  does so.

## Legal

- Not affiliated with or endorsed by DJI. "DJI", "Mini 4 Pro" and "DJI Assistant 2" are trademarks of
  their respective owners.
- The repository contains no DJI code or data files. The patch script holds a handful of byte values and
  addresses needed to find the bytes to change in a copy of the file you already own, and it verifies them
  before writing anything. Do not redistribute modified or original DJI binaries.
- Provided "as is", with no warranty (see [LICENSE](LICENSE)). Use at your own risk. Authors accept no
  liability for damage, injury, or loss.
