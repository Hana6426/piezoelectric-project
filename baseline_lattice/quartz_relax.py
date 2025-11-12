import numpy, os
import matplotlib.pyplot as plt
from labutil.plugins.pwscf import run_qe_pwscf, PWscf_inparam, parse_qe_pwscf_output
from labutil.objects import Struc, Dir, ase2struc, Kpoints, Constraint, PseudoPotential
from ase.io import write
from ase.spacegroup import crystal


def make_quartz_struc():
    """
    Creates the Quartz crystal structure using ASE. NOTE: this version creates the structure but at the wrong lattice parameters
    Feel free to import this for now though to have something to test code with!
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
    # Save to CIF for visualization/checking
    structure = Struc(ase2struc(quartz_left))
    return structure





def relax_lats(nk, ecut):
    """
    Make an input template and select potential and structure, and the path where to run
    """
    pseudopots = {
        "Si": PseudoPotential(
            ptype="uspp", element="Si", functional="LDA", name="Si_r.upf"
        ),
        "O": PseudoPotential(
            ptype="uspp", element="O", functional="LDA", name="O.pz-rrkjus.UPF"
        ),
    }
    struc = make_quartz_struc()
    kpts = Kpoints(gridsize=[nk, nk, nk], option="automatic", offset=True)
    dirname = "SiO2_nk{}_ecut{}_relaxation".format(nk, ecut)
    runpath = Dir(path=os.path.join("/home/bond/piezoelectric-project/baseline_lattice/SiO2_relaxations", dirname))
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
                "input_dft": "LDA" #Figure out how to adjust this!!
            },
            "ELECTRONS": {
                "diagonalization": "david",
                "mixing_beta": 0.7,
                "conv_thr": 1e-7,
            },
            "IONS": {"ion_dynamics": "bfgs"},
            "CELL": {},
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

def scan_params():
    nk = 10
    ecut = 30
    output = relax_lats(nk, ecut)
    cell_params = output["cell_parameters"]
    return cell_params

if __name__ == "__main__":
    # put here the function that you actually want to run
    print(scan_params())