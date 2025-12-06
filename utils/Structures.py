"""
Module containing various structure functions for quartz and PbTiO3
all take the role of make_struc(), but with varying capabilities, mainly around adding cell strains.


"""

from utils.Structures import Struc, ase2struc
from ase import Atoms
from ase.io import write
import os



def generate_strain_patterns():

def make_quartz_struc2():
    """
    Creates the relaxed quartz crystal structure using ASE. Uses numbers from Hana's calculation
    with ibrav=4 and c/a=0.635.
    :return: structure object converted from ase
    """
    
