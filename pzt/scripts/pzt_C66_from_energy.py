#!/usr/bin/env python3
import os

RY_TO_EV = 13.605693009
EV_TO_J  = 1.602176634e-19

def get_energy_Ry(path):
    with open(path) as f:
        for line in f:
            if "!    total energy" in line:
                # ... =    -333.76331702 Ry
                return float(line.split()[-2])
    raise RuntimeError(f"No total energy found in {path}")

def get_volume(path):
    with open(path) as f:
        for line in f:
            if "unit-cell volume" in line:
                parts = line.split()
                # "unit-cell volume = 407.8422 (a.u.)^3"
                vol_au3 = float(parts[3])   # <-- FIXED INDEX
                au_to_m = 0.529177210903e-10
                V_m3 = vol_au3 * (au_to_m**3)
                A_to_m = 1e-10
                V_A3 = V_m3 / (A_to_m**3)
                return V_A3, V_m3
    raise RuntimeError(f"No unit-cell volume found in {path}")

scf_file = "pzt/scf/pzt_scf.out"
Ep_file  = "pzt/elastic_tet/eps_p002_xy.out"
Em_file  = "pzt/elastic_tet/eps_m002_xy.out"

E0_Ry = get_energy_Ry(scf_file)
Ep_Ry = get_energy_Ry(Ep_file)
Em_Ry = get_energy_Ry(Em_file)

V0_A3, V0_m3 = get_volume(scf_file)

eps = 0.002  # Voigt shear strain γ₆

# central finite difference: ΔE = E(+) + E(-) - 2E0
dE_Ry = Ep_Ry + Em_Ry - 2.0 * E0_Ry
dE_J  = dE_Ry * RY_TO_EV * EV_TO_J

# C66 from ΔE/V ≈ 1/2 * C * eps^2  →  C = ΔE / (V * eps^2)
C66_Pa  = dE_J / (V0_m3 * eps**2)
C66_GPa = C66_Pa / 1.0e9

print("PZT (tetragonal) C66 from ±0.2% xy shear (energy FD):")
print(f"  E0   = {E0_Ry: .11f} Ry")
print(f"  Ep   = {Ep_Ry: .11f} Ry")
print(f"  Em   = {Em_Ry: .11f} Ry")
print(f"  dE   = {dE_Ry: .5e} Ry")
print(f"  V0   = {V0_A3:7.4f} Å^3")
print(f"  eps  = {eps: .4e}")
print(f"  C66 ≈ {C66_GPa:7.2f} GPa")
