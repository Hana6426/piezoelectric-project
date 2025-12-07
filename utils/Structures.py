"""
Module containing various structure functions for quartz and PbTiO3
all take the role of make_struc(), but with varying capabilities, mainly around adding cell strains.


"""
from labutil.plugins.pwscf import run_qe_pwscf, PWscf_inparam, parse_qe_pwscf_output
from labutil.objects import Struc, Dir, ase2struc, Kpoints, Constraint, PseudoPotential, File, ExternalCode 
from labutil.util import prepare_dir, run_command
from ase.spacegroup import crystal
from ase import Atoms
from ase.io import write
import os
import numpy as np


def make_unrelaxed_quartz_struc():
    """
    Creates the Quartz crystal structure using ASE. designed to then be relaxed into DFT structure according to desired parameters.
    :param alat: Lattice parameter in angstrom
    :return: structure object converted from ase
    """

    # Typical values for SiO2 quartz:
    a = 4.916  # Å
    c = 5.405  # Å

    # From your JSON data
    space_group = 152  # P3_121
    wyckoff_positions = [
        ('Si', (0.531089, 0.531089, 0)),        # 3a site
        ('O',  (0.269223, 0.413394, 0.784891))  # 6c site
    ]

    # Method 1: Using ASE's crystal function with spacegroup
    quartz_left = crystal(
        symbols=['Si', 'O'],
        basis=[(0.531089, 0.531089, 0),         # Si position
            (0.269223, 0.413394, 0.784891)], # O position
        spacegroup=152,  # P3_121
        cellpar=[a, a, c, 90, 90, 120]  # hexagonal cell parameters
    )
    structure = Struc(ase2struc(quartz_left))
    return structure

def make_unrelaxed_Pb_Ti_O3_struc():
    """
    Creates the Perovskite crystal structure using ASE.
    :param alat: Lattice parameter in angstrom
    :return: structure object converted from ase
    running DFT revealed: a = 3.860676393, c = 4.054793487

    """
    a = 3.860676393 #This is properly relaxed lattice constant from DFT

    c = 4.054793487 
    lattice = [[a, 0, 0], [0, a, 0], [0, 0, c]] # tetragonal cell
    symbols = ["Pb", "Ti", "O", "O", "O"]
    sc_pos = [
        [0, 0, 0],
        [0.5, 0.5, 0.5],
        [0, 0.5, 0.5],
        [0.5, 0, 0.5],
        [0.5, 0.5, 0],
    ]
    perov = Atoms(symbols=symbols, scaled_positions=sc_pos, cell=lattice)
    # check how your cell looks like
    # write('s.cif', perov)
    structure = Struc(ase2struc(perov))
    return structure



def read_final_geometry(file_path):
    """
    Reads cell parameters and atomic positions from a dft output file.
    reads through the file to find the CELL_PARAMETERS and ATOMIC_POSITIONS blocks
    repeatedly overwrites variables until both blocks are found
    :param file_path: path to the geometry file
    :return: lattice parameters as an array, atomic positions as a list of tuples, and atomic symbols as a list
    """
    cell_params = None
    with open(file_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if "CELL_PARAMETERS (angstrom)" in line or "CELL_PARAMETERS {angstrom}" in line:
            cell_params = []
            for i in range(3):
                cell_params.append([float(x) for x in lines[lines.index(line)+1+i].strip().split()])
        if "ATOMIC_POSITIONS" in line:
            atomic_positions = []
            atomic_symbols = []
            for pos_line in lines[lines.index(line)+1:]:
                if pos_line.strip() == "":
                    break
                parts = pos_line.strip().split()
                atomic_symbols.append(parts[0])
                atomic_positions.append([float(x) for x in parts[1:]])
    return np.array(cell_params), atomic_positions, atomic_symbols

def make_final_struc(file_path):
    """
    Creates the final crystal structure from hana's output file.
    agnostic to the type of material (reads atomic species from file)
    :return: structure object converted from ase
    """
    cell_params, atomic_positions, atomic_symbols = read_final_geometry(file_path)
    cell_final = Atoms(symbols=atomic_symbols, positions=atomic_positions, cell=cell_params, pbc=True)
    structure = Struc(ase2struc(cell_final))
    return structure

def make_final_positions(outfile, infile):
    """
    does waht make final struc does, but for 'relax' calculations that are missing the cell paremeters output block.
    it looks into the input file to get the cell parameters, and the output file to get the final atomic positions.
    :return: structure object converted from ase
    """
    cell_params, atomic_positions, atomic_symbols = read_final_geometry(outfile)
    print(cell_params)
    if cell_params == None:
        cell_params, _, _ = read_final_geometry(infile)
        print(cell_params)
    cell_final = Atoms(symbols=atomic_symbols, positions=atomic_positions, cell=cell_params, pbc=True)
    structure = Struc(ase2struc(cell_final))
    return structure

