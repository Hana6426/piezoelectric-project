import re, sys, pathlib

if len(sys.argv) != 3:
    print("Usage: python3 scripts/replace_geom.py <final_geom.txt> <scf.in>")
    sys.exit(1)

geom_path  = pathlib.Path(sys.argv[1])
scf_path   = pathlib.Path(sys.argv[2])
bak_path   = scf_path.with_suffix(scf_path.suffix + ".bak")

geom = geom_path.read_text()
scf  = scf_path.read_text()

# Extract blocks from final geometry
cell_match = re.search(r"(CELL_PARAMETERS[^\n]*\n(?:.*\n){3})", geom, flags=re.I)
if not cell_match:
    sys.exit("Could not find CELL_PARAMETERS block in final geometry.")
cell_block = cell_match.group(1).rstrip()

# ATOMIC_POSITIONS: grab until a blank line or EOF
apos_match = re.search(r"(ATOMIC_POSITIONS[^\n]*\n(?:.+\n)+?)(?:\n\s*\n|$)", geom, flags=re.I)
if not apos_match:
    sys.exit("Could not find ATOMIC_POSITIONS block in final geometry.")
apos_block = apos_match.group(1).rstrip()

# Replace blocks in SCF input
scf_new = re.sub(r"CELL_PARAMETERS[^\n]*\n(?:.*\n){3}", cell_block, scf, count=1, flags=re.I)
scf_new2 = re.sub(r"ATOMIC_POSITIONS[^\n]*\n(?:.+\n)+?(?=\n\S|\Z)", apos_block+"\n", scf_new, count=1, flags=re.I)

# Backup and write
bak_path.write_text(scf)
scf_path.write_text(scf_new2)
print(f"Updated {scf_path} (backup at {bak_path})")
