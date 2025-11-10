# PZT — Finite Strain Method

- Use tetragonal P4mm PZT cell (Pb(Zr0.5Ti0.5)O3).
- Relax structure in `../scf/`.
- Apply small ± strains to relevant tensor components.
- Run SCF, extract stress.
- Compute e_ij by finite differences.
