#!/usr/bin/env python3
"""
Compute PZT (tetragonal) e33 from Berry-phase polarization vs strain.

Edit the P_plus, P_minus, and eps values below to match your runs.
Run this script from the project root, e.g.:

    python3 pzt/scripts/pzt_e33_from_polarization.py

You can redirect the output to a log file if you like:

    python3 pzt/scripts/pzt_e33_from_polarization.py > pzt/e33/pzt_e33_results.txt
"""

def main():
    # === INPUTS (EDIT THESE FOR NEW RUNS) ===
    # Berry-phase total polarization along 3 (z) in C/m^2
    # For your current runs:
    #   eps3 = +0.005  --> P_plus  = 1.3422520 C/m^2
    #   eps3 = -0.005  --> P_minus = 1.3438060 C/m^2
    P_plus  = 1.3422520   # P3(+Δε3), C/m^2
    P_minus = 1.3438060   # P3(-Δε3), C/m^2

    # Strain amplitude Δε3 used for ±strain (dimensionless)
    eps = 0.005  # ±0.5% strain along c

    # === FINITE-DIFFERENCE e33 ===
    dP   = P_plus - P_minus
    e33  = dP / (2.0 * eps)

    # === PRINT NICE SUMMARY ===
    print("PZT (tetragonal) e33 from ±{:.3f}% c-axis strain (Berry-phase P3 FD):"
          .format(eps * 100.0))
    print("  P3(+eps) = {: .7f} C/m^2".format(P_plus))
    print("  P3(-eps) = {: .7f} C/m^2".format(P_minus))
    print("  dP       = {: .7f} C/m^2".format(dP))
    print("  eps      = {: .4e}".format(eps))
    print("  e33 ≈ {: .4f} C/m^2".format(e33))


if __name__ == "__main__":
    main()

