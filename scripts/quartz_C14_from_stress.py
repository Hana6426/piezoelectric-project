#!/usr/bin/env python3
"""
Compute C14 for alpha-quartz from shear-strain stress data.

We assume:
- Two SCF runs with +- shear strain (eps = 0.005) applied to the cell
- Output files:
    quartz_ibrav4/scf/quartz_scf_shear+0.005.out
    quartz_ibrav4/scf/quartz_scf_shear-0.005.out
- We use the xx stress component (sigma_11) in Ry/bohr^3, then convert to GPa.
"""

import re
import pathlib

# Paths (relative to repo root)
plus_file = pathlib.Path("quartz_ibrav4/scf/quartz_scf_shear+0.005.out")
minus_file = pathlib.Path("quartz_ibrav4/scf/quartz_scf_shear-0.005.out")

# Shear strain magnitude
eps = 0.005

# Conversion factor: 1 Ry/bohr^3 -> GPa
RY_PER_BOHR3_TO_GPA = 14710.507725010446  # precomputed

def parse_sigma_xx(fname):
    """
    Parse the total stress tensor from a QE output file and return sigma_xx
    in Ry/bohr^3 (the [0,0] element of the 3x3 tensor).
    """
    text = fname.read_text(errors="ignore")

    # Find the last occurrence of "total   stress"
    blocks = list(re.finditer(r"total\s+stress\s+\(Ry/bohr\*\*3\).*?\n(.*)\n(.*)\n(.*)",
                              text, re.DOTALL))
    if not blocks:
        raise RuntimeError(f"No 'total   stress' block found in {fname}")

    match = blocks[-1]
    line1, line2, line3 = match.group(1), match.group(2), match.group(3)

    # First line has sigma_xx, sigma_xy, sigma_xz in Ry/bohr^3
    parts1 = line1.split()
    sigma_xx_ry_bohr3 = float(parts1[0])

    return sigma_xx_ry_bohr3

def main():
    if not plus_file.exists():
        raise FileNotFoundError(f"Missing file: {plus_file}")
    if not minus_file.exists():
        raise FileNotFoundError(f"Missing file: {minus_file}")

    sigma_xx_plus = parse_sigma_xx(plus_file)
    sigma_xx_minus = parse_sigma_xx(minus_file)

    # Central finite difference derivative dσ1/dε4 in Ry/bohr^3
    d_sigma_d_eps = (sigma_xx_plus - sigma_xx_minus) / (2.0 * eps)

    # Convert to GPa
    C14_GPa = d_sigma_d_eps * RY_PER_BOHR3_TO_GPA

    # Prepare a small report
    report = []
    report.append("Quartz C14 from stress (yz shear, eps = ±0.005)")
    report.append(f"  sigma_xx(+eps) = {sigma_xx_plus: .8e} Ry/bohr^3")
    report.append(f"  sigma_xx(-eps) = {sigma_xx_minus: .8e} Ry/bohr^3")
    report.append(f"  d sigma_xx / d eps = {d_sigma_d_eps: .8e} Ry/bohr^3")
    report.append(f"  C14 ≈ {C14_GPa: .4f} GPa")

    text = "\n".join(report)
    print(text)

    # Also save to a text file
    outpath = pathlib.Path("quartz_ibrav4/C14_from_stress.txt")
    outpath.write_text(text + "\n")
    print(f"\nSaved C14 summary to {outpath}")

if __name__ == "__main__":
    main()

