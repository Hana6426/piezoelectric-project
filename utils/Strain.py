"""
contains scripts to create strained structures for finite difference DFT calculations of bery phase piezoelectric constants
Essential workflow:
1. take in previously computed final relaxed structure
2. open a new directory for each strain case
3. apply strain to the structure, run a 'relax' calculation in the new directory, WITH FLAG TO SAVE TO DISK TURNED ON
    with cell fixed to allow atomic positions to relax within strained cell
"""

import os
import sys
sys.path.append("/home/bond/piezoelectric-project")
import numpy as np
from labutil.plugins.pwscf import run_qe_pwscf, PWscf_inparam, parse_qe_pwscf_output
from labutil.objects import Struc, Dir, ase2struc, Kpoints, Constraint, PseudoPotential, File, ExternalCode
from labutil.util import prepare_dir, run_command
from utils.Structures import read_final_geometry, make_final_struc, make_final_positions
from utils.DFPT import pseudos
from ase import Atoms


def get_strained_cells(original_cell, strain_type, magnitude):
    """
    Applies the given strain tensor to the original cell parameters.
    :param original_cell: The original cell parameters as a 3x3 numpy array
    :param strain_type: The type of strain to apply, for right now (xx, zz, yz))
    :param magnitude: The magnitude of the strain to apply, as a decimal (e.g., 0.01 for 1%)
    :return: The strained cell parameters as a 3x3 numpy array
    """

    if strain_type == "xx":
        strain_tensor = np.array([[magnitude, 0, 0],
                                  [0, 0, 0],
                                  [0, 0, 0]])
    elif strain_type == "zz":
        strain_tensor = np.array([[0, 0, 0],
                                  [0, 0, 0],
                                  [0, 0, magnitude]])
    elif strain_type == "yz":
        strain_tensor = np.array([[0, 0, 0],
                                   [0, 0, magnitude/2],
                                   [0, magnitude/2, 0]])
    else:
        raise ValueError("Unsupported strain type: {}".format(strain_type))
    #because the cell parameters are the lattice vectors as rows, we need to transpose the strain tensor and multiply on the right
    strained_cell = original_cell + np.dot(original_cell, strain_tensor.T) #transpose not necessary for symmetric tensors, but good practice

    return strained_cell

if __name__ == "__main__":
    #test run:
    cell = np.array([[4.916, 0, 0],
                     [-2.458, 4.256, 0],
                     [0, 0, 5.405]])
    strain_type = "yz"
    magnitude = 0.01
    strained_cell = get_strained_cells(cell, strain_type, magnitude)
    print("Original Cell:")
    print(cell)
    print("Strained Cell ({} strain of {}):".format(strain_type, magnitude))
    print(strained_cell)


def strain_and_relax(vc_file, material, functional,  strain_type, magnitude, path, nk = 6, ecut = 60):
    """
    Applies strain to the relaxed structure and relaxes atomic positions within the strained cell.

    :param vc_file: str: path to the out file of the run vc-relax calculation
    :param material: The material structure to strain
    :param functional: The DFT functional to use (LDA or PBEsol)
    :param nk: k-point grid size
    :param ecut: energy cutoff
    :param path: The path to the directory where the DFT calculations will be run
    :param strain_type: The type of strain to apply (e.g., "xx", "zz", "yz")
    :param magnitude: The magnitude of the strain to apply, as a decimal (e.g., 0.01 for 1%)
    """
    # Load the previously relaxed structure

    original_cell, atomic_positions, atomic_symbols = read_final_geometry(vc_file)

    # Apply strain to the cell
    strained_cell = get_strained_cells(original_cell, strain_type, magnitude)

    # Create new directory for strained calculation
    strain_dirname = "{}_strain_{:.4f}".format(strain_type, magnitude)
    runpath = Dir(path=os.path.join(path, strain_dirname))
    prepare_dir(runpath.path)

    # Prepare the structure with strained cell and original atomic positions
    cell_strained = Atoms(symbols=atomic_symbols, positions=atomic_positions, cell=strained_cell, pbc=True)
    struc = Struc(ase2struc(cell_strained))

    # Define pseudos and kpoints
    pseudopots = pseudos(material, functional)
    kpts = Kpoints(gridsize=[nk, nk, nk], option="automatic", offset=True)

    # Prepare input parameters for relaxation with fixed cell
    input_params = PWscf_inparam(
            {
            "CONTROL": {
                "calculation": "relax",
                "pseudo_dir": os.environ["QE_POTENTIALS"],
                "outdir": runpath.path,
                "tstress": True,
                "tprnfor": True,
            },
            "SYSTEM": {
                "ecutwfc": ecut,
                "ecutrho": ecut * 8,
                "input_dft": functional,
            },
            "ELECTRONS": {
                "diagonalization": "david",
                "mixing_beta": 0.7,
                "conv_thr": 1e-7,
            },
            "IONS": {"ion_dynamics": "bfgs"},
            "CELL": {
                "cell_dofree": "none",  # keep cell fixed during relaxation
            },
        }
    )


    # Run the DFT calculation
    output_file = run_qe_pwscf(
        runpath=runpath,
        struc=struc,
        pseudopots=pseudopots,
        params=input_params,
        kpoints=kpts,
        ncpu=2,
    )
    return output_file






def Berry_phase_calculation(save_dir, material, functional, nk, ecut):
    """
    Runs a Berry phase calculation on the given saved file from a previous relax calculation.
    :param saved_file: The path to the directory containinmg the strained run
    :param material: The material structure to calculate
    :param functional: The DFT functional to use (LDA or PBEsol)
    :param nk: k-point grid size
    :param ecut: energy cutoff
    :param path: The path to the directory where the berry phase calculation DFT calculations will be run
    """
    # Define pseudos and kpoints
    pseudopots = pseudos(material, functional)
    kpts = Kpoints(gridsize=[nk, nk, nk], option="automatic", offset=True)
    struc = make_final_positions(os.path.join(save_dir, "pwscf.out"), os.path.join(save_dir, "pwscf.in"))
    runpath = os.path.join(save_dir, "berry_phase")
    # Prepare input parameters for Berry phase calculation,
    input_params = PWscf_inparam(
        {
            "CONTROL": {
                "calculation": "nscf",
                "pseudo_dir": os.environ["QE_POTENTIALS"],
                "outdir": save_dir,
                "tstress": True,
                "tprnfor": True,
                "lberry": True,
                "disk_io": "none",
                "gdir": 1, # direction of polarization calculation
                "nppstr": 10
            },
            "SYSTEM": {
                "ecutwfc": ecut,
                "ecutrho": ecut * 8,
                "input_dft": functional,
            },
            "ELECTRONS": {
                "diagonalization": "david",
                "mixing_beta": 0.7,
                "conv_thr": 1e-7,
            },
            "IONS": {"ion_dynamics": "bfgs"},
            "CELL": {
                "cell_dofree": "none",  # keep cell fixed during relaxation
            },
        }
    )

    # Run the DFT calculation
    output_file = run_qe_pwscf(
        runpath=Dir(path=runpath),
        struc=struc, # Structure is read from the saved file
        pseudopots=pseudopots,
        params=input_params,
        kpoints=kpts,
        ncpu=2,
    )
    return output_file