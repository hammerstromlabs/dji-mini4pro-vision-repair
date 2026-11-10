"""Make a copy of DJIVisionCalibration3.dll whose wa140 pair uses the forward cameras.

Each patch is (VA, original bytes, new bytes); the script refuses to write if any
original bytes differ, so it can't silently patch the wrong build.
"""
import hashlib
import sys
import pefile

src, dst = sys.argv[1], sys.argv[2]

PATCHES = [
    # wa140 result file: "cali_ab.txt" -> "cali_cd.txt" (same length, 0xb)
    (0x10089F18, bytes.fromhex("b8be6110"), bytes.fromhex("f8be6110")),
    # left topic: len 0xd "raw/down/left" -> len 0xe "raw/front/left"
    (0x10089FC9, bytes.fromhex("0d"), bytes.fromhex("0e")),
    (0x10089FCB, bytes.fromhex("ccbe6110"), bytes.fromhex("04bf6110")),
    # right topic: len 0xe "raw/down/right" -> len 0xf "raw/front/right"
    (0x1008A00B, bytes.fromhex("0e"), bytes.fromhex("0f")),
    (0x1008A00D, bytes.fromhex("dcbe6110"), bytes.fromhex("14bf6110")),
]

pe = pefile.PE(src)
base = pe.OPTIONAL_HEADER.ImageBase
buf = bytearray(open(src, "rb").read())
print("original sha1", hashlib.sha1(buf).hexdigest())

for va, old, new in PATCHES:
    off = pe.get_offset_from_rva(va - base)
    cur = bytes(buf[off:off + len(old)])
    if cur != old:
        sys.exit(f"mismatch at {va:#x} (file {off:#x}): have {cur.hex()} want {old.hex()}")
    buf[off:off + len(new)] = new
    print(f"patched {va:#x} (file {off:#x}): {old.hex()} -> {new.hex()}")

open(dst, "wb").write(buf)
print("patched sha1", hashlib.sha1(buf).hexdigest())
