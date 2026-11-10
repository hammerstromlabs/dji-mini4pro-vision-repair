"""Find code references to given strings in a 32-bit PE and dump surrounding disassembly."""
import sys
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

path = sys.argv[1]
needles = [s.encode() for s in sys.argv[2:]]
ctx_before = 40
ctx_after = 60

pe = pefile.PE(path, fast_load=False)
base = pe.OPTIONAL_HEADER.ImageBase
data = pe.get_memory_mapped_image()

# Locate each needle as a NUL-terminated string in the image.
targets = {}
for n in needles:
    start = 0
    while True:
        i = data.find(n + b"\x00", start)
        if i < 0:
            break
        if i == 0 or data[i - 1] == 0:
            targets[base + i] = n.decode()
        start = i + 1

print("string VAs:", {hex(k): v for k, v in targets.items()})

text = next(s for s in pe.sections if s.Name.rstrip(b"\x00") == b".text")
tva = base + text.VirtualAddress
tbytes = data[text.VirtualAddress:text.VirtualAddress + text.Misc_VirtualSize]

# Raw scan for little-endian 32-bit immediates equal to the string VA.
hits = []
for va, name in targets.items():
    le = va.to_bytes(4, "little")
    start = 0
    while True:
        i = tbytes.find(le, start)
        if i < 0:
            break
        hits.append((tva + i, name))
        start = i + 1

md = Cs(CS_ARCH_X86, CS_MODE_32)
for hit_va, name in sorted(hits):
    print(f"\n==== ref to '{name}' near {hit_va:#x}")
    off = hit_va - tva
    lo = max(0, off - ctx_before)
    for ins in md.disasm(tbytes[lo:off + ctx_after], tva + lo):
        mark = "  <--" if ins.address <= hit_va < ins.address + ins.size else ""
        print(f"  {ins.address:#x}: {ins.mnemonic} {ins.op_str}{mark}")
