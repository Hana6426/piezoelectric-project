# Quartz — Finite Strain Method

1. Start from relaxed structure from `../scf/`.
2. Apply small strains (e.g. ±0.5%, ±1%) to selected components of the strain tensor.
3. For each strained cell, run `pw.x` SCF.
4. Extract stress tensor from each run.
5. Fit σ vs η to obtain piezoelectric coefficients e_ij.
