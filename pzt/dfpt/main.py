#contains main workflow for producing a piezoelectric tensor using Linear response and DFPT
import numpy, os, sys
import matplotlib.pyplot as plt
from labutil.plugins.pwscf import run_qe_pwscf, PWscf_inparam, parse_qe_pwscf_output
from labutil.objects import Struc, Dir, ase2struc, Kpoints, Constraint, PseudoPotential, File, ExternalCode 
from labutil.util import prepare_dir, run_command
from ase.io import write

sys.path.append("/home/bond/piezoelectric-project")
from baseline_lattice.PZT_relax import make_Pb_Ti_O_struc


def run_scf(nk, ecut, runpath):
    #runs a self-consistent field calculation on the optimized lattice shape, produces the charge density
    print("Running SCF calculation...")
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
    dirname = "PbTiO3_scf"
    runpath = Dir(path=os.path.join("/home/bond/piezoelectric-project/pzt/dfpt", dirname))
    input_params = PWscf_inparam(
        {
            "CONTROL": {
                "calculation": "scf",
                "pseudo_dir": os.environ["QE_POTENTIALS"],
                "outdir": runpath.path,
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
        ncpu=4,
    )
    output = parse_qe_pwscf_output(outfile=output_file)
    return output

import subprocess

def run_qe_ph( #DEPRECIATED
    runpath,
    ph_input_name="ph.in",
    ph_output_name="ph.out",
    ncpu=1,
    mpirun_command="mpirun"
):
    """
    Run a Quantum ESPRESSO ph.x calculation using a pre-written input file.
    
    Args:
        runpath (str): Directory where calculation is run.
        ph_input_file (str): Name of the ph.x input file (must already exist).
        ph_output_file (str): Name of output file to write.
        ncpu (int): Number of MPI processes.
        mpirun_command (str): MPI command (default "mpirun").
        
    Returns:
        str: Path to the output file.
        
    Raises:
        FileNotFoundError: If the input file doesn't exist.
        RuntimeError: If the ph.x command fails.
    """
    # Get ph.x executable path from environment variable
    ph_code = ExternalCode({"path": os.environ["QE_PH_COMMAND"]})
    # Check if input file exists
    ph_in_path = os.path.join(runpath.path, ph_input_name)
    if not os.path.exists(ph_in_path):
        raise FileNotFoundError(f"Ph.x input file not found: {ph_in_path}")

    ph_out_path = os.path.join(runpath.path, ph_output_name)

    # Build the command (following your wrapper's pattern)
    ph_command = (
        f'bash -c "set -eo pipefail; '
        f'{mpirun_command} -np {ncpu} {ph_code.path} -inp {ph_in_path} | tee {ph_out_path}"'
    )
    
    print(f"Running ph.x command: {ph_command}")
    print(f"Working directory: {runpath}")
    
    # Run the command
    result = subprocess.run(
        ph_command,
        shell=True,
        cwd=runpath.path,
        capture_output=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Ph.x calculation failed with return code {result.returncode}")

    return ph_out_path


def run_qe_ph(runpath, ph_input_name="ph.in", ph_output_name="ph.out", ncpu=1):
    # Use the same command that works from terminal
    ph_command = f'mpirun -np {ncpu} ph.x < {ph_input_name} > {ph_output_name}'
    
    result = subprocess.run(ph_command, shell=True, cwd=runpath.path)
    return os.path.join(runpath.path, ph_output_name)


def parse_ph_output(runpath, ph_output_name="ph.out"):
    #read the ph.out file and extract the relevant tensors and matrices.
    ph_out_path = os.path.join(runpath.path, ph_output_name)
    if not os.path.exists(ph_out_path):
        raise FileNotFoundError(f"Ph.x output file not found: {ph_out_path}")
    
    






if __name__ == "__main__":
    nk = 8  # k-point grid size
    ecut = 60  # energy cutoff in Ry

    #scf_output = run_scf(nk, ecut)
    runpath = Dir(path="/home/bond/piezoelectric-project/pzt/dfpt/PbTiO3_scf")
    ph_output = run_qe_ph(
        runpath=runpath,
        ncpu=4,
    )