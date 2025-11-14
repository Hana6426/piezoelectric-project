import re, sys, pathlib
if len(sys.argv)!=3:
    print("Usage: python3 scripts/extract_final_geom.py <relax.out> <final_geom.txt>")
    sys.exit(1)
src = pathlib.Path(sys.argv[1]).read_text()
# find last CELL_PARAMETERS and its 3 lines
cell_iter = list(re.finditer(r"CELL_PARAMETERS[^\n]*\n(?:.*\n){3}", src, flags=re.I))
if not cell_iter:
    sys.exit("Could not find CELL_PARAMETERS block in relax output.")
cell_block = cell_iter[-1].group(0).rstrip()

# find last ATOMIC_POSITIONS block (until blank line/next header/EOF)
apos_iter = list(re.finditer(r"ATOMIC_POSITIONS[^\n]*\n(?:.+\n)+?(?=\n\S|\Z)", src, flags=re.I))
if not apos_iter:
    sys.exit("Could not find ATOMIC_POSITIONS block in relax output.")
apos_block = apos_iter[-1].group(0).rstrip()

out = f"{cell_block}\n\n{apos_block}\n"
pathlib.Path(sys.argv[2]).write_text(out)
print(f"Wrote final geometry to {sys.argv[2]}")
