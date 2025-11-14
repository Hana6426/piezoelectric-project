from ase import Atoms
from ase.spacegroup import crystal
from labutil.objects import Struc, ase2struc

def make_PbTiO3_struc(a=3.90, c=4.14):
    """
    5-atom tetragonal perovskite (PbTiO3) P4mm-like.
    A = Pb at (0,0,0); B = Ti at (1/2,1/2,1/2); O at equatorial/apical positions.
    """
    lattice = [[a,0,0],[0,a,0],[0,0,c]]
    symbols = ["Pb","Ti","O","O","O"]
    sc_pos = [
        [0.00, 0.00, 0.00],  # Pb
        [0.50, 0.50, 0.50],  # Ti
        [0.00, 0.50, 0.50],  # O
        [0.50, 0.00, 0.50],  # O
        [0.50, 0.50, 0.00],  # O
    ]
    return Struc(ase2struc(Atoms(symbols=symbols, scaled_positions=sc_pos, cell=lattice, pbc=True)))

def make_quartz_struc(a=4.916, c=5.405):
    """
    α-quartz (SiO2), space group P3_121 (#152).
    Fractional basis from Lucas’s script.
    """
    q = crystal(
        symbols=['Si','O'],
        basis=[(0.531089, 0.531089, 0.0),
               (0.269223, 0.413394, 0.784891)],
        spacegroup=152,
        cellpar=[a, a, c, 90, 90, 120]
    )
    return Struc(ase2struc(q))
