import math

# ---- Energies in Rydberg from QE ----
E0_Ry = -216.94157910      # unstrained: quartz_scf.out
Ep_Ry = -216.94163844      # +0.5% strain: eps_p005_xx.out
Em_Ry = -216.94108468      # -0.5% strain: eps_m005_xx.out

# ---- Cell volume in (a.u.)^3 from QE ----
V0_au3 = 758.2272          # "unit-cell volume = 758.2272 (a.u.)^3"

# ---- Constants ----
RY_TO_EV = 13.605698066
EV_TO_J = 1.602176634e-19
BOHR_TO_ANG = 0.529177249
ANG3_TO_M3 = 1e-30

eps = 0.005  # ±0.5% strain

# ---- Convert energies to Joules ----
def ry_to_j(ery):
    return ery * RY_TO_EV * EV_TO_J

E0 = ry_to_j(E0_Ry)
Ep = ry_to_j(Ep_Ry)
Em = ry_to_j(Em_Ry)

# ---- Convert volume from (a.u.)^3 to m^3 ----
V0_A3 = V0_au3 * (BOHR_TO_ANG ** 3)  # Å^3
V0_m3 = V0_A3 * ANG3_TO_M3          # m^3

# ---- Finite-difference curvature ----
# C11 = [E(+eps) + E(-eps) - 2E(0)] / (eps^2 * V)
numerator = Ep + Em - 2.0 * E0
C11_Pa = numerator / (eps ** 2 * V0_m3)
C11_GPa = C11_Pa / 1e9

print(f"Quartz: E0 = {E0_Ry:.8f} Ry")
print(f"        Ep = {Ep_Ry:.8f} Ry  ( +0.5% strain )")
print(f"        Em = {Em_Ry:.8f} Ry  ( -0.5% strain )")
print(f"        V0 = {V0_A3:.4f} Å^3")
print(f"Estimated C11 ≈ {C11_GPa:.2f} GPa")
