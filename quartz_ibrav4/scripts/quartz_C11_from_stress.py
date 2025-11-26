#!/usr/bin/env python3
"""
Compute C11 for quartz from ± strain SCF runs using stress output.

Assumes the files quartz_scf_eps+0.005.out and quartz_scf_eps-0.005.out
live in the current working directory and contain a block like:

  total   stress  (Ry/bohr**3)                   (kbar)
   ... ... ...    sigma_xx  sigma_yy  sigma_zz

We grab sigma_xx in kbar for +eps and -eps and use:

    C11 = [sigma_xx(+eps) - sigma_xx(-eps)] / (2 * eps)
"""

import pathlib

EPS = 0.005  # 0.5% strain


def get_sigma_xx_kbar(outfile: str) -> float:
    """Parse sigma_xx (kbar) from QE 'total   stress' block."""
    path = pathlib.Path(outfile)
    if not path.exists():
        raise FileNotFoundError(f"{outfile} not found")

    with path.open() as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "total   stress" in line and "(kbar)" in line:
            # Next line has three stress components in Ry/bohr^3 and kbar
            # Example:
            #  0.00002245  -0.00005723   0.00005356            3.30  -8.42   7.88
            row = lines[i + 1]
            parts = row.split()
            # Last 3 entries are the kbar components: sigma_xx, sigma_yy, sigma_zz
            sigma_xx_kbar = float(parts[-3])
            return sigma_xx_kbar

    raise RuntimeError(f"Could not find stress block in {outfile}")


def main():
    plus_file = "quartz_scf_eps+0.005.out"
    minus_file = "quartz_scf_eps-0.005.out"

    sigma_plus = get_sigma_xx_kbar(plus_file)
    sigma_minus = get_sigma_xx_kbar(minus_file)

    print(f"sigma_xx(+eps) = {sigma_plus:.4f} kbar")
    print(f"sigma_xx(-eps) = {sigma_minus:.4f} kbar")
    print(f"eps = {EPS:.4f}")

    C11_kbar = (sigma_plus - sigma_minus) / (2 * EPS)
    C11_GPa = C11_kbar * 0.1  # 1 kbar = 0.1 GPa

    print()
    print(f"C11 ≈ {C11_kbar:8.2f} kbar")
    print(f"C11 ≈ {C11_GPa:8.2f} GPa")


if __name__ == "__main__":
    main()

