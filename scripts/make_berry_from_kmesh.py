import sys, re
if len(sys.argv)!=3:
    print("Usage: python3 scripts/make_berry_from_kmesh.py <src.in> <dst.in>"); exit(1)
src, dst = sys.argv[1], sys.argv[2]
t = open(src).read()

# find K_POINTS automatic line and capture nkx
m = re.search(r'K_POINTS\s+automatic\s*\n\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', t, re.I)
assert m, "Could not find 'K_POINTS automatic' 3+3 integers"
nkx = int(m.group(1))

# locate &system and inject/replace the required keys
ms = re.search(r'(&system\b.*?)/', t, flags=re.I|re.S)
assert ms, "&system not found"
body = ms.group(1)

def set_kv(s,k,v):
    import re
    r = re.compile(r'^\s*'+re.escape(k)+r'\s*=.*$', re.I|re.M)
    line = f"    {k} = {v}"
    return r.sub(line, s) if r.search(s) else s + "\n" + line

body = set_kv(body, "lberry", ".true.")
body = set_kv(body, "lelfield", ".true.")
body = set_kv(body, "gdir", "1")
body = set_kv(body, "nppstr", str(nkx))

# (often helpful for polarization)
body = set_kv(body, "nosym", ".true.")
body = set_kv(body, "noinv", ".true.")

t = t[:ms.start(1)] + body + "\n" + t[ms.start(2):]

open(dst, "w").write(t)
print(f"Wrote {dst} with nppstr={nkx}")
