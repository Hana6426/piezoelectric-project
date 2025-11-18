#!/usr/bin/env python3
import math

RY_TO_EV = 13.605693009
EV_TO_J  = 1.602176634e-19
BOHR2M   = 0.529177210903e-10
GPA_TO_PA = 1.0e9

# ---- file paths ----
scf_file = "pzt/scf/pzt_scf.out"
Ep_file  = "pzt/elastic_tet/eps_p002_xxyy.out"
Em_file  = "pzt/elastic_tet/eps_m002_xxyy.out"

# strain magnitude (±0.2% biaxial)
eps = 0.002

# C11 from your earlier script (update if you re-compute it)
C11_GPa = 310.92

def get_energy_Ry(path):
    with open(path) as f:
        for line in f:
            if "!    total energy" in line:
                return float(line.split("=")[1].split()[0])
    raise RuntimeError(f"No total energy found in {path}")

def get_volume(path):
    with open(path) as f:
        for line in f:
            if "unit-cell volume" in line:
                parts = line.split()
                # ... volume          =     407.8422 (a.u.)^3
                vol_au3 = float(parts[3])
                break
        else:
            raise RuntimeError(f"No unit-cell volume line in {path}")
    # (a.u.)^3 -> m^3
    vol_m3 = vol_au3 * (BOHR2M**3)
    vol_A3 = vol_m3 * 1.0e30
    return vol_A3, vol_m3

# ---- main ----
E0_Ry  = get_energy_Ry(scf_file)
Ep_Ry  = get_energy_Ry(Ep_file)
Em_Ry  = get_energy_Ry(Em_file)

V0_A3, V0_m3 = get_volume(scf_file)

# average energy change for ±eps
Eavg_Ry = 0.5 * (Ep_Ry + Em_Ry)
dE_Ry   = Eavg_Ry - E0_Ry   # ΔE = Ē(eps) - E0

# convert ΔE to J
dE_J = dE_Ry * RY_TO_EV * EV_TO_J

# For ε1 = ε2 = eps, ε3 = 0:
#   ΔE = V * (C11 + C12) * eps^2
# => K = C11 + C12 = ΔE / (V * eps^2)
K_Pa  = dE_J / (V0_m3 * eps**2)
K_GPa = K_Pa / GPA_TO_PA

C12_GPa = K_GPa - C11_GPa

print("PZT (tetragonal) C12 from ±0.2% xx+yy biaxial strain (energy FD):")
print(f"  E0   = {E0_Ry: .11f} Ry")
print(f"  Ep   = {Ep_Ry: .11f} Ry")
print(f"  Em   = {Em_Ry: .11f} Ry")
print(f"  Eavg = {Eavg_Ry: .11f} Ry")
print(f"  dE   = {dE_Ry: .5e} Ry")
print(f"  V0   = {V0_A3: .4f} Å^3")
print(f"  eps  = {eps: .4e}")
print(f"  K = C11 + C12 ≈ {K_GPa: .2f} GPa")
print(f"  Using C11 = {C11_GPa:.2f} GPa")
print(f"  => C12 ≈ {C12_GPa:.2f} GPa")

with open("pzt/elastic_tet/C_results.txt", "a") as f:
    f.write("\n--- Biaxial ±0.2% xx+yy ---\n")
    f.write(f"E0   = {E0_Ry:.11f} Ry\n")
    f.write(f"Ep   = {Ep_Ry:.11f} Ry\n")
    f.write(f"Em   = {Em_Ry:.11f} Ry\n")
    f.write(f"eps  = {eps:.4e}\n")
    f.write(f"K = C11 + C12 = {K_GPa:.3f} GPa\n")
    f.write(f"C11 (input)   = {C11_GPa:.3f} GPa\n")
    f.write(f"C12           = {C12_GPa:.3f} GPa\n")
