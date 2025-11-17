from labutil.objects import Struc, ase2struc
from ase.spacegroup import crystal

def make_quartz_struc():
    """
    Quartz structure from Lucas, converted to labutil Struc.
    This uses the same geometry Lucas defined in his make_quartz_struc().
    """

    # Typical values for SiO2 quartz:
    a = 4.916  # Å
    c = 5.405  # Å

    space_group = 152  # P3_121

    # Lucas's ASE crystal definition
    quartz_ase = crystal(
        symbols=['Si', 'O'],
        basis=[
            (0.531089, 0.531089, 0.0),       # Si position (3a site)
            (0.269223, 0.413394, 0.784891),  # O position (6c site)
        ],
        spacegroup=space_group,
        cellpar=[a, a, c, 90, 90, 120],     # hexagonal cell parameters
    )

    # Convert ASE Atoms -> labutil Struc (same pattern Lucas used)
    structure = Struc(ase2struc(quartz_ase))
    return structure
