#!/usr/bin/env python3
"""
Summarize k-point convergence for quartz SCF runs.

Reads:
  quartz/scf/quartz_scf_nk4.out
  quartz/scf/quartz_scf_nk6.out
  quartz/scf/quartz_scf_nk8.out
  quartz/scf/quartz_scf_nk10.out

and prints a small table of energies in Ry, eV, and meV/cell
relative to the tightest mesh (nk=10).
"""

import os
from pathlib import Path

RY_TO_EV = 13.605698066

# repo_root/quartz
quartz_dir = Path(__file__).resolve().parents[1]
scf_dir = quartz_dir / "scf"

kmeshes = [4, 6, 8, 10]

def parse_total_energy(path):
    """Return total energy in Ry from a QE pw.x output."""
    E = None
    with open(path, "r") as f:
        for line in f:
            if "!    total energy" in line:
                # line like: "!    total energy              =    -216.94157910 Ry"
                parts = line.split()
                try:
                    E = float(parts[-2])
                except (IndexError, ValueError):
                    pass
    if E is None:
        raise RuntimeError(f"Could not find total energy in {path}")
    return E

def main():
    data = []
    for nk in kmeshes:
        fname = scf_dir / f"quartz_scf_nk{nk}.out"
        if not fname.exists():
            print(f"# WARNING: missing file {fname}")
            continue
        E_Ry = parse_total_energy(fname)
        data.append((nk, E_Ry))

    if not data:
        print("# No data found, nothing to summarize.")
        return

    # reference: tightest mesh (largest nk)
    ref_nk, ref_E = sorted(data, key=lambda x: x[0])[-1]

    print("# Quartz k-point convergence summary")
    print("# Files: quartz/scf/quartz_scf_nk{4,6,8,10}.out")
    print("# Energies relative to nk = {} (tightest mesh)".format(ref_nk))
    print()
    print("{:>6s}  {:>18s}  {:>18s}  {:>14s}".format(
        "nk", "E_tot (Ry)", "E_tot (eV)", "ΔE (meV/cell)"
    ))
    print("-" * 64)

    for nk, E_Ry in sorted(data, key=lambda x: x[0]):
        E_eV = E_Ry * RY_TO_EV
        dE_meV = (E_Ry - ref_E) * RY_TO_EV * 1000.0
        print("{:6d}  {:18.10f}  {:18.10f}  {:14.4f}".format(
            nk, E_Ry, E_eV, dE_meV
        ))

if __name__ == "__main__":
    main()
