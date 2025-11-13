#!/usr/bin/env python3
from pathlib import Path

RY_TO_EV = 13.605698066

nks = [4, 6, 8, 10]
energies_ry = {}

for nk in nks:
    out_path = Path(f"pzt/scf/pzt_scf_nk{nk}.out")
    if not out_path.exists():
        print(f"# WARNING: {out_path} does not exist, skipping")
        continue

    E_ry = None
    with out_path.open() as f:
        for line in f:
            if line.strip().startswith("!    total energy"):
                # line like: !    total energy =   -333.xxx Ry
                parts = line.split()
                E_ry = float(parts[-2])
    if E_ry is None:
        print(f"# WARNING: no total energy found in {out_path}")
    else:
        energies_ry[nk] = E_ry

if not energies_ry:
    raise SystemExit("No energies found – did the runs finish?")

# Use the tightest mesh (max nk that succeeded) as reference
nk_ref = max(energies_ry.keys())
E_ref_ry = energies_ry[nk_ref]

lines = []
lines.append("# PZT k-point convergence summary")
lines.append("# Files: pzt/scf/pzt_scf_nk{4,6,8,10}.out")
lines.append("# Energies relative to nk = {} (tightest mesh)".format(nk_ref))
lines.append("")
lines.append("    nk          E_tot (Ry)          E_tot (eV)   ΔE (meV/cell)")
lines.append("----------------------------------------------------------------")

for nk in sorted(energies_ry.keys()):
    E_ry = energies_ry[nk]
    E_ev = E_ry * RY_TO_EV
    dE_meV = (E_ry - E_ref_ry) * RY_TO_EV * 1000.0
    lines.append(f"{nk:6d}  {E_ry:16.10f}  {E_ev:16.10f}  {dE_meV:14.4f}")

text = "\n".join(lines)
print(text)

# also save to a text file next to the outputs
out_summary = Path("pzt/scf/pzt_kconv_summary.txt")
out_summary.write_text(text + "\n")
print(f"\n# Wrote summary to {out_summary}")

