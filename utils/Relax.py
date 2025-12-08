#module containing scripts to help with initial relaxation of structures
#takes you from noting to having a fully relaxed DFT structure on disk
#lets you choose LDA or PBEsol functionals/USPPs

from utils.Structures import make_unrelaxed_quartz_struc, make_unrelaxed_Pb_Ti_O3_struc
import numpy, os, sys
from labutil.plugins.pwscf import run_qe_pwscf, PWscf_inparam, parse_qe_pwscf_output
from labutil.objects import Struc, Dir, ase2struc, Kpoints, Constraint, PseudoPotential, File, ExternalCode 
from labutil.util import prepare_dir, run_command
from ase.spacegroup import crystal
from ase import Atoms
from utils.DFPT import pseudos

import subprocess
sys.path.append("/home/bond/piezoelectric-project")

def relax_structure_dft(material, functional, nk, ecut, path):
    """
    Relaxes the given material structure using DFT.
    :param material: The material structure to relax
    :param functional: The DFT functional to use (LDA or PBEsol)
    :param runpath: The path to the directory where the DFT calculations will be run
    """
    #start by defining pseudos
    pseudopots = pseudos(material, functional)
    if material == "quartz":
        ibrav = 4 #Hexagonal
        struc = make_unrelaxed_quartz_struc()
    elif material == "PbTiO3":
        ibrav = 0 #Tetragonal
        struc = make_unrelaxed_Pb_Ti_O3_struc()
    else:
        raise ValueError("Unsupported material: {}".format(material))
    
    kpts = Kpoints(gridsize=[nk, nk, nk], option="automatic", offset=True)
    dirname = "{}_nk{}_ecut{}_relaxation".format(material, nk, ecut)
    runpath = Dir(path=os.path.join(path, dirname))
    input_params = PWscf_inparam(
        {
            "CONTROL": {
                "calculation": "vc-relax",
                "pseudo_dir": os.environ["QE_POTENTIALS"],
                "outdir": runpath.path,
                "tstress": True,
                "tprnfor": True,
                "disk_io": "none",
            },
            "SYSTEM": {
                "ecutwfc": ecut,
                "ecutrho": ecut * 8,
                "input_dft": functional,
                "ibrav": ibrav,
            },
            "ELECTRONS": {
                "diagonalization": "david",
                "mixing_beta": 0.7,
                "conv_thr": 1e-7,
            },
            "IONS": {"ion_dynamics": "bfgs"},
            "CELL": {
                "cell_dynamics": "bfgs",
                "cell_dofree": 'ibrav', #force relaxation according to bravais lattice
            },
        }
    )
    output_file = run_qe_pwscf(
        runpath=runpath,
        struc=struc,
        pseudopots=pseudopots,
        params=input_params,
        kpoints=kpts,
        ncpu=2,
    )
    output = parse_qe_pwscf_output(outfile=output_file)
    return output