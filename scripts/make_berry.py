import sys,re
if len(sys.argv)!=3:
    print("Usage: python3 scripts/make_berry.py <src.in> <dst.in>"); exit(1)
src,dst=sys.argv[1],sys.argv[2]
t=open(src).read()
# ensure we can edit &system
m=re.search(r"(&system\b.*?)/", t, flags=re.I|re.S)
assert m, "&system not found"
body=m.group(1)
def set_kv(s,k,v):
    r=re.compile(rf'^\s*{k}\s*=.*$', flags=re.I|re.M)
    line=f"    {k} = {v}"
    return r.sub(line, s) if r.search(s) else s+"\n"+line
for k,v in {
    "lberry": ".true.",
    "lelfield": ".true.",
    "gdir": "1",      # polarization along x
    "nppstr": "1"
}.items():
    body=set_kv(body,k,v)
t = t[:m.start(1)] + body + t[m.end(1):]
open(dst,"w").write(t)
print("Wrote", dst)
