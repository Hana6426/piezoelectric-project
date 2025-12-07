#module for DFPT calculations.
#all functions should only be run from a Working Directory that is directly parent to the scf folder containing scf and phonon outputs
#contains main workflow for producing a piezoelectric tensor using Linear response and DFPT
import numpy, os, sys
from labutil.plugins.pwscf import run_qe_pwscf, PWscf_inparam, parse_qe_pwscf_output
from labutil.objects import Struc, Dir, ase2struc, Kpoints, Constraint, PseudoPotential, File, ExternalCode 
from labutil.util import prepare_dir, run_command
from ase.spacegroup import crystal
from ase import Atoms

import subprocess
sys.path.append("/home/bond/piezoelectric-project")


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
    structure = Struc(ase2struc(quartz_left))
    return structure


def read_final_geometry(file_path):
    """
    Reads cell parameters and atomic positions from hana's final geometry file
    :param file_path: path to the geometry file
    :return: lattice parameters as an array, atomic positions as a list of tuples, and atomic symbols as a list
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if "CELL_PARAMETERS (angstrom)" in line:
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
    return numpy.array(cell_params), atomic_positions, atomic_symbols


def make_quartz_final():
    """
    Creates the relaxed quartz crystal structure using ASE. Uses numbers from Hana's final geometry file.
    :return: structure object converted from ase
    """
    cell_params, atomic_positions, atomic_symbols = read_final_geometry('quartz_final_geometry.txt')
    quartz_final = Atoms(symbols=atomic_symbols, positions=atomic_positions, cell=cell_params, pbc=True)
    structure = Struc(ase2struc(quartz_final))
    return structure

def make_Pb_Ti_O3_struc():
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

def pseudos(molecule, functional="LDA"):
    if functional == "LDA":
        if molecule == "quartz":
            pseudopots = {
                "Si": PseudoPotential(
                    ptype="uspp", element="Si", functional="LDA", name="Si_r.upf"
                ),
                "O": PseudoPotential(
                    ptype="uspp", element="O", functional="LDA", name="O.pz-rrkjus.UPF"
                ),
            }
        elif molecule == "PbTiO3":
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
    elif functional == "PBEsol":
        if molecule == "quartz":
            pseudopots = {
                "Si": PseudoPotential(
                    ptype="uspp", element="Si", functional="PBEsol", name="Si.pbesol-n-rrkjus_psl.1.0.0.UPF"
                ),
                "O": PseudoPotential(
                    ptype="uspp", element="O", functional="PBEsol", name="O.pbesol-n-rrkjus_psl.1.0.0.UPF"
                ),
            }
        elif molecule == "PbTiO3":
            pseudopots = {
                "Pb": PseudoPotential(
                    ptype="uspp", element="Pb", functional="PBEsol", name="Pb.pbesol-dn-rrkjus_psl.1.0.0.UPF"
                ),
                "Ti": PseudoPotential(
                    ptype="uspp", element="Ti", functional="PBEsol", name="Ti.pbesol-spn-rrkjus_psl.1.0.0.UPF"
                ),
                "O": PseudoPotential(
                    ptype="uspp", element="O", functional="PBEsol", name="O.pbesol-n-rrkjus_psl.1.0.0.UPF"
                ),
            }
    return pseudopots



def run_scf(molecule, nk = None, ecut = None, ncpu = 4):
    """
    Run a self-consistent field (SCF) calculation for quartz using Quantum ESPRESSO, to prepare for a phonon run.
    :param molecule: (str) The type of molecule, e.g., 'quartz' or 'PbTiO3'
    :param nk: (int) The k-point grid size.
    :param ecut: (int) The energy cutoff in Ry.
    :param ncpu: (int) Number of CPUs to use for the calculation.
    :return: path object to directory containing the SCF output file.
    """
    if ecut == None:
        ecut = 60  # default energy cutoff in Ry

    pseudopots = psuedos(molecule) #just returns the right pseudoss, moved out for clarity
    if molecule == "quartz":
        struc = make_quartz_final()
        nk = 8 if nk is None else nk  # default k-point grid size
    elif molecule == "PbTiO3":
        struc = make_Pb_Ti_O3_struc()
        nk = 6 if nk is None else nk  # default k-point grid size
    kpts = Kpoints(gridsize=[nk, nk, nk], option="automatic", offset=True)

    runpath = Dir(path=os.path.join(os.getcwd(), f"{molecule}_scf")) #keeping labutils Dir object structure
    input_params = PWscf_inparam(
        {
            "CONTROL": {
                "calculation": "scf",
                "pseudo_dir": os.environ["QE_POTENTIALS"],
                "outdir": runpath.path, #right now, will always just make the scf folder in the current directory
                "tstress": True,
                "tprnfor": True,
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
        ncpu=ncpu,
    )
    return runpath

def generate_phonon_input(path):
    """
    Generate the phonon input file for Quantum ESPRESSO's ph.x module.
    :param molecule: (str) The type of molecule, e.g., 'quartz' or 'PbTiO3'
    :return: None (writes ph.in file in the appropriate directory)
    """
    ph_input_content = """&inputph
    prefix = 'pwscf'
    outdir = '/home/bond/piezoelectric-project/pzt/dfpt/PbTiO3_scf'
    tr2_ph = 1.0d-14
    fildyn = 'matdyn_G'
    ldisp = .false.
    epsil = .true.
    zue = .true.
    /
    0.0 0.0 0.0
    """
    with open(os.path.join(path.path, "ph.in"), "w") as ph_in_file:
        ph_in_file.write(ph_input_content)



def run_qe_ph(molecule, ncpu=4):
    # Use the same command that works from terminal
    ph_command = f'mpirun -np {ncpu} ph.x < ph.in > ph.out'
    runpath = Dir(path = os.getcwd()) #assumes running from directory of scf folder
    #check if phonon input file exists, if not generate it
    ph_in_path = os.path.join(runpath.path, "ph.in")
    if not os.path.isfile(ph_in_path):
        generate_phonon_input(runpath)
    subprocess.run(ph_command, shell=True, cwd=runpath.path) #temporarily shifts working directory to child to runpath for command execution
    return os.path.join(runpath.path, 'ph.out')


def parse_phonon_output(molecule):
    outfile = os.path.join(os.getcwd(), "ph.out")
    with open(outfile, "r") as outf:
        for line in outf:
            if line.startswith("          Dielectric constant in cartesian axis"):
                # Skip the next line
                next(outf)
                # Read the next three lines for the dielectric tensor
                dielectric_tensor = []
                for _ in range(3):
                    line = next(outf)
                    dielectric_tensor.append([float(x) for x in line.strip("() \n").split()])
                dielectric_tensor = numpy.array(dielectric_tensor)
            if line.startswith("          Effective charges (d P / du) in cartesian axis"):
                # Skip the next line
                next(outf)
                #assemble a dictionary of effective charge tensors for each atom
                effective_charges = {}
                while True:
                    line = next(outf)
                    if line.strip() == "":
                        break  # End of effective charges section
                    if line.startswith("           atom"):
                        parts = line.split()
                        atom_key = parts[1]
                        # Read the next three lines for the effective charge tensor
                        eff_charge_tensor = []
                        for _ in range(3):
                            line = next(outf)
                            #EXAMPLE LINE: Px  (       -6.04766        0.00000        0.00000 )
                            line = line.strip()
                            line = line.split("(")[1]
                            eff_charge_tensor.append([float(x) for x in line.strip("() \n").split()])
                        effective_charges[atom_key] = numpy.array(eff_charge_tensor)


    result = {
        "dielectric_tensor": dielectric_tensor,
        "effective_charge_dict": effective_charges,
    }
    return result