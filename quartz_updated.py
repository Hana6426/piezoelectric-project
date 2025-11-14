# quartz_lucas.py

import numpy, os
from labutil.objects import Struc, ase2struc
from ase.spacegroup import crystal

def make_quartz_struc():
    """
    Creates the Quartz crystal structure using ASE.
    NOTE: Lucas mentioned this is approximately quartz and not perfectly relaxed;
    we’ll let QE relax it.
    Returns a labutil Struc object.
    """

    # Lucas’s lattice parameters (example)
    a = 4.916  # Å
    c = 5.405  # Å

    # Whatever Lucas had here:
    # (don’t change his Wyckoff positions / space group)
    space_group = 152  # P3_121, for example

    # Reuse his crystal() call exactly:
    quartz_ase = crystal(
        symbols=['Si', 'O', 'O', ...],  # <- Lucas’s list
        basis=[...],                    # <- Lucas’s fractional coords
        spacegroup=space_group,
        cellpar=[a, a, c, 90, 90, 120]
    )

    # Convert ASE Atoms → labutil Struc
    quartz_struc = ase2struc(quartz_ase)
    return quartz_struc
