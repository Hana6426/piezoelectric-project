#!/usr/bin/env python3
"""
Compute C11 for quartz from ± strain SCF runs using stress output.
Also saves the result into quartz_ibrav4/results/C11_result.txt
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
            row = lines[i + 1]
            parts = row.split()
            sigma_xx_kbar = float(parts[-3])
            return sigma_xx_kbar

    raise RuntimeError(f"Could not find stress block in {outfile}")


def main():
    plus_file = "quartz_scf_eps+0.005.out"
    minus_file = "quartz_scf_eps-0.005.out"

    sigma_plus = get_sigma_xx_kbar(plus_file)
    sigma_minus = get_sigma_xx_kbar(minus_file)

    C11_kbar = (sigma_plus - sigma_minus) / (2 * EPS)
    C11_GPa = C11_kbar * 0.1  # 1 kbar = 0.1 GPa

    # Print results
    print(f"sigma_xx(+eps) = {sigma_plus:.6f} kbar")
    print(f"sigma_xx(-eps) = {sigma_minus:.6f} kbar")
    print(f"eps = {EPS:.6f}")
    print()
    print(f"C11 = {C11_kbar:.6f} kbar")
    print(f"C11 = {C11_GPa:.6f} GPa")

    # Save to file
    results_dir = pathlib.Path("quartz_ibrav4/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    outfile = results_dir / "C11_result.txt"
    with outfile.open("w") as f:
        f.write("Quartz C11 finite-strain result\n")
        f.write("--------------------------------\n")
        f.write(f"epsilon = {EPS}\n")
        f.write(f"sigma_xx(+eps) = {sigma_plus:.6f} kbar\n")
        f.write(f"sigma_xx(-eps) = {sigma_minus:.6f} kbar\n")
        f.write("\n")
        f.write(f"C11 = {C11_kbar:.6f} kbar\n")
        f.write(f"C11 = {C11_GPa:.6f} GPa\n")

    print(f"\nSaved results to {outfile}")


if __name__ == "__main__":
    main()
