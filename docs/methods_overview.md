# Methods Overview

We compare three ways of computing the piezoelectric response for α-quartz (SiO₂) and PZT (Pb(Zr,Ti)O₃):

## 1. Finite Strain (Hana)
- Apply small ± strains to the relaxed structure.
- Run SCF for each strained cell.
- Extract stress tensor.
- Use Δσ / Δη to compute e_ij.

## 2. Finite Field / Polarization (Hana)
- Apply small ± distortions or fields (where allowed).
- Compute polarization (Berry phase or charge integration).
- Use ΔP / Δη to extract e_ij.

## 3. DFPT / Born Effective Charges (Partner)
- Use phonon/DFPT to compute Born effective charges and dielectric response.
- Combine with internal strain derivatives to obtain e_ij.
- Use as a benchmark to compare against finite methods.

Each method is implemented for:
- `quartz/`
- `pzt/`

with parallel folder structures for clarity.
