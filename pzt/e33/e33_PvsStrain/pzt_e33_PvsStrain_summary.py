#!/usr/bin/env python3
"""
Summary script for PZT (tetragonal) e33 and d33
from Berry-phase polarization vs strain (P vs ε).

Run from the project root:
    python3 pzt/e33/e33_PvsStrain/pzt_e33_PvsStrain_summary.py
"""

def main():
    # === INPUTS: update these if you recompute ===
    # Polarization along z (P3) from Berry phase, in C/m^2
    P_plus  = 1.3422520   # P3 at +0.5% strain (eps = +0.005)
    P_minus = 1.3438060   # P3 at -0.5% strain (eps = -0.005)

    # Strain amplitude used (dimensionless)
    eps = 0.005  # ±0.5% along c

    # Elastic constant C33 from your previous energy-strain fit
    C33_GPa = 322.64       # GPa
    C33_SI  = C33_GPa * 1e9  # convert to N/m^2

    # === e33 from central finite difference ===
    dP  = P_plus - P_minus
    e33 = dP / (2.0 * eps)    # C/m^2

    # === d33 from e33 and C33 ===
    d33_SI      = e33 / C33_SI          # m/V = C/N
    d33_pC_per_N = d33_SI * 1e12        # pC/N

    # === Print nice summary ===
    print("PZT (tetragonal) e33 and d33 from P vs strain (Berry phase):")
    print(f"  eps magnitude     = {eps:.4e}  (±{eps*100:.3f} % along c)")
    print(f"  P3(+eps)          = {P_plus: .7f} C/m^2")
    print(f"  P3(-eps)          = {P_minus: .7f} C/m^2")
    print(f"  dP                = {dP: .7f} C/m^2")
    print()
    print(f"  e33               = {e33: .4f} C/m^2")
    print()
    print(f"  C33               = {C33_GPa:.2f} GPa")
    print(f"  d33 (SI)          = {d33_SI: .4e} m/V  (C/N)")
    print(f"  d33               = {d33_pC_per_N: .3f} pC/N")


if __name__ == "__main__":
    main()
