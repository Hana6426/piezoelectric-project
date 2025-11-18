#!/usr/bin/env python3
"""
Compute C33 for tetragonal PZT (PbTiO3) from ±0.2% xx strain
using finite-difference of total energies.

Assumes these files already exist and are converged:
  - pzt/scf/pzt_scf.out              (unstrained)
  - pzt/elastic_tet/eps_p002_zz.out  (+0.2% strain)
  - pzt/elastic_tet/eps_m002_zz.out  (-0.2% strain)
"""

RY_TO_EV   = 13.605693009        # eV per Ry
EV_TO_J    = 1.602176634e-19     # J per eV
BOHR_TO_A  = 0.529177210903      # Å per bohr


def get_energy_Ry(path):
    """Return the LAST '!    total energy = ... Ry' value in Ry."""
    E = None
    with open(path, "r") as f:
        for line in f:
            if "!    total energy" in line:
                parts = line.split()
                # ... total energy              =    -333.76331702 Ry
                # last numeric before 'Ry'
                E = float(parts[-2])
    if E is None:
        raise RuntimeError(f"No total energy found in {path}")
    return E


def get_volume_A3(path):
    """
    Read 'unit-cell volume = ... (a.u.)^3' from SCF output,
    convert from bohr^3 to Å^3.
    """
    vol_au3 = None
    with open(path, "r") as f:
        for line in f:
            if "unit-cell volume" in line:
                parts = line.split()
                # e.g.: unit-cell volume          =     407.8422 (a.u.)^3
                vol_au3 = float(parts[-2])
    if vol_au3 is None:
        raise RuntimeError(f"No unit-cell volume found in {path}")

    a0 = BOHR_TO_A
    vol_A3 = vol_au3 * (a0 ** 3)
    return vol_A3


def main():
    scf_file   = "pzt/scf/pzt_scf.out"
    eps_p_file = "pzt/elastic_tet/eps_p002_zz.out"
    eps_m_file = "pzt/elastic_tet/eps_m002_zz.out"

    # Strain magnitude ±0.2% in zz
    eps = 0.002

    # Energies in Ry
    E0_Ry = get_energy_Ry(scf_file)
    Ep_Ry = get_energy_Ry(eps_p_file)
    Em_Ry = get_energy_Ry(eps_m_file)

    # Volume in Å^3
    V0_A3 = get_volume_A3(scf_file)

    # Second derivative of energy w.r.t. strain (per cell), still in Ry
    d2E_Ry = Ep_Ry + Em_Ry - 2.0 * E0_Ry

    # Convert to Joules per cell
    d2E_J = d2E_Ry * RY_TO_EV * EV_TO_J

    # Volume in m^3
    V0_m3 = V0_A3 * 1.0e-30

    # Elastic constant in Pa, then GPa
    C33_Pa  = d2E_J / (V0_m3 * eps ** 2)
    C33_GPa = C33_Pa / 1.0e9

    print("PZT (tetragonal) C33 from ±0.2% xx strain (energy FD):")
    print(f"  E0  = {E0_Ry:.11f} Ry")
    print(f"  Ep  = {Ep_Ry:.11f} Ry")
    print(f"  Em  = {Em_Ry:.11f} Ry")
    print(f"  V0  = {V0_A3:.4f} Å^3")
    print(f"  eps = {eps:.4f}")
    print(f"  C33 ≈ {C33_GPa:.2f} GPa")


if __name__ == "__main__":
    main()
