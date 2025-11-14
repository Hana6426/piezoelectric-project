import sys, re
eta = float(sys.argv[1]); src = sys.argv[2]; dst = sys.argv[3]
txt = open(src).read()
m = re.search(r"CELL_PARAMETERS *\((?:angstrom|bohr)\)\s+([^\n]+)\n([^\n]+)\n([^\n]+)", txt, re.I)
assert m, "CELL_PARAMETERS not found"
r1 = [float(x) for x in m.group(1).split()]
r1 = [(1+eta)*x for x in r1]
new = ("CELL_PARAMETERS (angstrom)\n"
       f"  {r1[0]:.10f}  {r1[1]:.10f}  {r1[2]:.10f}\n"
       "  "+m.group(2)+"\n  "+m.group(3))
txt = re.sub(r"CELL_PARAMETERS *\((?:angstrom|bohr)\)\s+[^\n]+\n[^\n]+\n[^\n]+", new, txt, 1, re.I)
open(dst,"w").write(txt)
