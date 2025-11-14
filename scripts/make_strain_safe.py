import sys, re
if len(sys.argv)!=4:
    print("Usage: python3 scripts/make_strain_safe.py <eta> <scf.in> <out.in>"); sys.exit(1)
eta=float(sys.argv[1]); src=sys.argv[2]; dst=sys.argv[3]
txt=open(src).read()
m=re.search(r"(CELL_PARAMETERS[^\n]*\n)([^\n]+)\n([^\n]+)\n([^\n]+)", txt, re.I)
assert m, "CELL_PARAMETERS block not found"
r1=[float(x) for x in m.group(2).split()]
r1=[(1+eta)*x for x in r1]
cell = m.group(1) + f"  {r1[0]:.10f}  {r1[1]:.10f}  {r1[2]:.10f}\n" + m.group(3)+"\n"+m.group(4)
out = txt[:m.start()] + cell + txt[m.end():]
open(dst,"w").write(out)
print("Wrote", dst)
