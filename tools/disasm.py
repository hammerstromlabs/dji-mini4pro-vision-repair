"""Disassemble a VA range of a 32-bit PE, annotating pointers to strings and doubles."""
import struct
import sys
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

path, start, end = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
pe = pefile.PE(path)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()


def cstr(va):
    off = va - base
    if not 0 <= off < len(img):
        return None
    s = img[off:off + 80].split(b"\x00")[0]
    if len(s) >= 3 and all(32 <= c < 127 for c in s):
        return s.decode()
    return None


def dbl(va):
    off = va - base
    if 0 <= off < len(img) - 8:
        return struct.unpack("<d", img[off:off + 8])[0]
    return None


md = Cs(CS_ARCH_X86, CS_MODE_32)
code = img[start - base:end - base]
for ins in md.disasm(code, start):
    note = ""
    for tok in ins.op_str.replace("[", " ").replace("]", " ").replace(",", " ").split():
        if tok.startswith("0x") and len(tok) >= 9:
            v = int(tok, 16)
            s = cstr(v)
            if s:
                note = f'   ; "{s}"'
            elif "movsd" in ins.mnemonic or "qword" in ins.op_str:
                d = dbl(v)
                if d is not None:
                    note = f"   ; {d!r}"
    print(f"{ins.address:#x}: {ins.mnemonic} {ins.op_str}{note}")
