#!/usr/bin/env python3
import numpy as np

# ====== INPUTS FROM QE BERRY-PHASE RUNS ======

# Total Berry phases (dimensionless), taken from
# quartz_e11_0_berry.out, quartz_e11_p0.005_berry.out, quartz_e11_m0.005_berry.out
phi_0 = -0.10989    # eps = 0.000
phi_p = -0.44111    # eps = +0.005
phi_m = -0.16675    # eps = -0.005

# Strain amplitude for +/- runs (0.5% along direction 1)
eps = 0.005  # dimensionless

# CELL_PARAMETERS for eps = 0.0 (from quartz_ibrav4/pol/quartz_e11_0.in), in Angstrom:
a1 = np.array([ 5.006779,  0.000000, 0.000000])
a2 = np.array([-2.503390,  4.335998, 0.000000])
a3 = np.array([ 0.000000,  0.000000, 5.215118])

# We are interested in e11, i.e. polarization response along the
# lattice direction corresponding to gdir = 1 -> a1
R_dir = a1.copy()


# ====== CONSTANTS ======
e_charge = 1.602176634e-19  # C
two_pi   = 2.0 * np.pi

# ====== GEOMETRY ======

# Cell volume in Angstrom^3
Omega_A3 = np.dot(a1, np.cross(a2, a3))

# Convert to m^3
Omega_m3 = Omega_A3 * 1.0e-30

# Lattice vector magnitude for direction 1 in meters
R_dir_m = R_dir * 1.0e-10
R_norm  = np.linalg.norm(R_dir_m)

print("=== Geometry check ===")
print(f"Cell volume Ω [Å^3]: {Omega_A3:.6f}")
print(f"Cell volume Ω [m^3]: {Omega_m3:.6e}")
print(f"|a1| [m]:            {R_norm:.6e}")

# ====== PHASE → POLARIZATION ======
# Simple 1D formula:
#   P = (e / (2π Ω)) * φ * |R_dir|
#
# This gives the component of P along the lattice direction a1.

def phase_to_P(phi):
    return e_charge * phi * R_norm / (two_pi * Omega_m3)

P0 = phase_to_P(phi_0)
Pp = phase_to_P(phi_p)
Pm = phase_to_P(phi_m)

print("\n=== Polarizations along a1 [C/m^2] ===")
print(f"P( eps = 0.000 )  = {P0: .6e}")
print(f"P( eps = +0.005)  = {Pp: .6e}")
print(f"P( eps = -0.005)  = {Pm: .6e}")

# ====== FINITE DIFFERENCE FOR e11 ======
# Central finite difference:
#   e11 ≈ [P(+eps) - P(-eps)] / (2 * eps)
e11_central = (Pp - Pm) / (2.0 * eps)

# Optional: forward difference from 0 -> +eps:
#   e11 ≈ [P(+eps) - P(0)] / eps
e11_forward = (Pp - P0) / eps

print("\n=== Piezoelectric coefficient e11 [C/m^2] ===")
print(f"Central difference: e11 ≈ {e11_central: .6e} C/m^2")
print(f"Forward difference: e11 ≈ {e11_forward: .6e} C/m^2")

