#!/usr/bin/env python3
import math

# Constants
RY_TO_EV   = 13.605698066
EV_TO_J    = 1.602176634e-19
ANG3_TO_M3 = 1.0e-30

def get_energy_Ry(path):
    """
    Return the LAST 'total energy' in Ry from a QE output.
    This is more robust than matching the exact '!    total energy' line.
    """
    E_last = None
    with open(path, "r") as f:
        for line in f:
            if "total energy" in line and "Ry" in line:
                # e.g.: '     total energy              =    -217.03998403 Ry'
                # or:   '!    total energy              =    -217.03998403 Ry'
                parts = line.split()
                # last but one should be the numeric value
                try:
                    E_last = float(parts[-2])
                except ValueError:
                    continue
    if E_last is None:
        raise RuntimeError(f"No total energy found in {path}")
    return E_last

def get_volume_A3(path):
    """Read 'unit-cell volume = ... (a.u.)^3' and convert to Å^3."""
    with open(path, "r") as f:
        for line in f:
            if "unit-cell volume" in line:
                parts = line.split()
                # ['unit-cell','volume','=','759.5734','(a.u.)^3']
                vol_au3 = float(parts[-2])
                bohr_to_ang = 0.529177249
                return vol_au3 * (bohr_to_ang**3)
    raise RuntimeError(f"No unit-cell volume found in {path}")

# === Files ===
scf_file  = "quartz/scf/quartz_scf.out"
eps_p_file = "quartz/elastic_triclinic/eps_p002_xx.out"
eps_m_file = "quartz/elastic_triclinic/eps_m002_xx.out"

# Strain magnitude (±0.2%)
eps = 0.002

# --- Read energies ---
E0_Ry = get_energy_Ry(scf_file)
Ep_Ry = get_energy_Ry(eps_p_file)
Em_Ry = get_energy_Ry(eps_m_file)

# --- Volume in Å^3 ---
V0_A3 = get_volume_A3(scf_file)

# Convert energies to Joules
E0 = E0_Ry * RY_TO_EV * EV_TO_J
Ep = Ep_Ry * RY_TO_EV * EV_TO_J
Em = Em_Ry * RY_TO_EV * EV_TO_J

# Convert volume to m^3
V0 = V0_A3 * ANG3_TO_M3

# Finite-difference second derivative: C11 = (E(+ε) - 2E(0) + E(-ε)) / (V * ε^2)
C11_Pa  = (Ep - 2.0*E0 + Em) / (V0 * eps**2)
C11_GPa = C11_Pa / 1.0e9

print("Quartz (hex) C11 from ±0.2% xx strain (energy FD):")
print(f"  E0  = {E0_Ry:.8f} Ry")
print(f"  Ep  = {Ep_Ry:.8f} Ry")
print(f"  Em  = {Em_Ry:.8f} Ry")
print(f"  V0  = {V0_A3:.4f} Å^3")
print(f"  C11 ≈ {C11_GPa:.2f} GPa")
