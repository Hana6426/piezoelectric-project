import numpy, os
import matplotlib.pyplot as plt
from labutil.plugins.pwscf import run_qe_pwscf, PWscf_inparam, parse_qe_pwscf_output
from labutil.objects import Struc, Dir, ase2struc, Kpoints, Constraint, PseudoPotential
from ase.io import write
from ase import Atoms


def make_Pb_Ti_O_struc():
    """
    Creates the Perovskite crystal structure using ASE. NOTE: this version creates the structure but at the wrong lattice parameter.
    Feel free to import this for now though to have something to test code with!
    :param alat: Lattice parameter in angstrom
    :return: structure object converted from ase
    running DFT revealed:

    """
    a = 3.9#These are guesses based on experiment

    c = 4.0#guess, replace for the base structure to use in DFt calcs. 
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


def parse_qe_pwscf_output(outfile):
    cell_parameters = None #for scf calculations when cell parameters are never reported, so it doesnt freak out
    positions = None
    with open(outfile.path, "r") as outf:
        for line in outf:
            if line.lower().startswith("     pwscf"):
                walltime = line.split()[-3] + line.split()[-2]
            if line.lower().startswith("     total force"):
                total_force = float(line.split()[3]) * (13.605698066 / 0.529177249)
            if line.lower().startswith("!    total energy"):
                total_energy = float(line.split()[-2]) * 13.605698066
            if line.lower().startswith("          total   stress"):
                pressure = float(line.split()[-1])
            if line.lower().startswith("cell_parameters"):
                # we could extract cell parameters here if needed
                cell_parameters = []
                for _ in range(3):
                    line = next(outf)
                    cell_parameters.append([float(x) for x in line.split()])
            if line.lower().startswith("     unit-cell volume"):
                volume = float(line.split()[-2])  # in Au^3
                volume = volume * 0.529177249**3  # convert to Angstrom^3
            if line.startswith("ATOMIC_POSITIONS"):
                # grab the next 5 lines verbatim, preserving all whitespace and newlines
                positions = []
                for _ in range(5):
                    positions.append(next(outf))
    result = {
        "energy": total_energy,
        "force": total_force,
        "pressure": pressure,
        "walltime": walltime,
        "cell_parameters": cell_parameters,
        "volume": volume,
        "positions": positions
    }
    return result


def relax_lats(nk, ecut):
    """
    Make an input template and select potential and structure, and the path where to run
    """
    pseudopots = {
        "Pb": PseudoPotential(
            ptype="uspp", element="Pb", functional="LDA", name="Pb.pz-d-van.UPF"
        ),
        "Ti": PseudoPotential(
            ptype="uspp", element="Ti", functional="LDA", name="Ti.pz-sp-van_ak.UPF"
        ),
        "O": PseudoPotential(
            ptype="uspp", element="O", functional="LDA", name="O.pz-rrkjus.UPF"
        ),
    }
    struc = make_Pb_Ti_O_struc()
    kpts = Kpoints(gridsize=[nk, nk, nk], option="automatic", offset=True)
    dirname = "PbTiO3_nk{}_relaxation".format(nk)
    runpath = Dir(path=os.path.join("/home/bond/piezoelectric-project/baseline_lattice/PbTiO3_relaxations", dirname))
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


def lattice_scan():
    nk = 10
    ecut = 30
    output = relax_lats(nk, ecut)
    cell_params = output["cell_parameters"]
    return cell_params



if __name__ == "__main__":
    # put here the function that you actually want to run
    print(lattice_scan())
