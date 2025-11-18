#!/usr/bin/env python3
import os

RY_TO_EV = 13.605693009
EV_TO_J  = 1.602176634e-19

def get_energy_Ry(path):
    with open(path) as f:
        for line in f:
            if "!    total energy" in line:
                return float(line.split()[-2])
    raise RuntimeError(f"No total energy found in {path}")

def get_volume(path):
    with open(path) as f:
        for line in f:
            if "unit-cell volume" in line:
                parts = line.split()
                vol_au3 = float(parts[3])   # <-- SAME FIX
                au_to_m = 0.529177210903e-10
                V_m3 = vol_au3 * (au_to_m**3)
                A_to_m = 1e-10
                V_A3 = V_m3 / (A_to_m**3)
                return V_A3, V_m3
    raise RuntimeError(f"No unit-cell volume found in {path}")

scf_file = "pzt/scf/pzt_scf.out"
Ep_file  = "pzt/elastic_tet/eps_p002_yz.out"
Em_file  = "pzt/elastic_tet/eps_m002_yz.out"

E0_Ry = get_energy_Ry(scf_file)
Ep_Ry = get_energy_Ry(Ep_file)
Em_Ry = get_energy_Ry(Em_file)

V0_A3, V0_m3 = get_volume(scf_file)

eps = 0.002  # Voigt shear strain γ₄

dE_Ry = Ep_Ry + Em_Ry - 2.0 * E0_Ry
dE_J  = dE_Ry * RY_TO_EV * EV_TO_J

C44_Pa  = dE_J / (V0_m3 * eps**2)
C44_GPa = C44_Pa / 1.0e9

print("PZT (tetragonal) C44 from ±0.2% yz shear (energy FD):")
print(f"  E0   = {E0_Ry: .11f} Ry")
print(f"  Ep   = {Ep_Ry: .11f} Ry")
print(f"  Em   = {Em_Ry: .11f} Ry")
print(f"  dE   = {dE_Ry: .5e} Ry")
print(f"  V0   = {V0_A3:7.4f} Å^3")
print(f"  eps  = {eps: .4e}")
print(f"  C44 ≈ {C44_GPa:7.2f} GPa")
