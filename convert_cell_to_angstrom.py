#!/usr/bin/env python3
import numpy as np

# ---- EDIT THESE VALUES FOR EACH SYSTEM ----

# 1) alat value (in Bohr) from QE output
alat_bohr = 9.27890000   # example for quartz; change as needed

# 2) CELL_PARAMETERS (alat=...) matrix from QE
#    Copy exactly the 3 lines under CELL_PARAMETERS (alat=...)
cell_alat = np.array([
    [ 1.019672712,  0.000000000,  0.000000000],
    [-0.509836356,  0.883062472,  0.000000000],
    [ 0.000000000,  0.000000000,  1.062102652]
])

# ------------------------------------------

# Conversion constant
BOHR_TO_ANG = 0.529177210903

# First convert to Bohr:
cell_bohr = alat_bohr * cell_alat

# Then convert to Angstrom:
cell_ang = cell_bohr * BOHR_TO_ANG

print("CELL_PARAMETERS (angstrom)")
for row in cell_ang:
    print(f"{row[0]:11.6f}  {row[1]:11.6f}  {row[2]:11.6f}")
