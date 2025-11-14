import sys, re
if len(sys.argv)!=3:
    print("Usage: python3 scripts/make_berry_blocksafe.py <src.in> <dst.in>"); sys.exit(1)
src, dst = sys.argv[1], sys.argv[2]
txt = open(src).read()

# ---- find K_POINTS automatic to set nppstr = nkx
m = re.search(r'K_POINTS\s+automatic\s*\n\s*(\d+)\s+(\d+)\s+(\d+)\s+\d+\s+\d+\s+\d+', txt, flags=re.I)
if not m:
    raise SystemExit("Could not find 'K_POINTS automatic' with 3+3 integers")
nkx = int(m.group(1))

# ---- locate &SYSTEM block boundaries (line indices)
lines = txt.splitlines()
sys_start = None
sys_end   = None
for i, line in enumerate(lines):
    if sys_start is None and re.match(r'^\s*&\s*system\b', line, flags=re.I):
        sys_start = i
        continue
    if sys_start is not None and re.match(r'^\s*/\s*$', line):
        sys_end = i
        break
if sys_start is None or sys_end is None:
    raise SystemExit("Could not find complete &SYSTEM ... / block")

# ---- edit the &SYSTEM body
body = lines[sys_start:sys_end+1]  # inclusive of trailing '/'
def set_kv(body_lines, key, val):
    pat = re.compile(r'^\s*' + re.escape(key) + r'\s*=', flags=re.I)
    line = f"    {key} = {val}"
    for j in range(1, len(body_lines)-1):  # skip first (&SYSTEM) and last (/)
        if pat.match(body_lines[j]):
            body_lines[j] = line
            return body_lines
    body_lines.insert(len(body_lines)-1, line)
    return body_lines

for k,v in [
    ("lberry",   ".true."),
    ("lelfield", ".true."),
    ("gdir",     "1"),         # polarization along x
    ("nppstr",   str(nkx)),
    ("nosym",    ".true."),    # helpful for polarization runs
    ("noinv",    ".true.")
]:
    body = set_kv(body, k, v)

# ---- rebuild file
new_lines = lines[:sys_start] + body + lines[sys_end+1:]
open(dst, "w").write("\n".join(new_lines) + ("\n" if txt.endswith("\n") else ""))
print(f"Wrote {dst} with nppstr={nkx}")
