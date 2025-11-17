import os
from labutil.plugins.pwscf import run_qe_pwscf, PWscf_inparam, parse_qe_pwscf_output
from labutil.objects import Dir, Kpoints, PseudoPotential
from quartz_updated import make_quartz_struc


def run_quartz_relax(nk=8, ecut=60):
    """
    Relax α-quartz (SiO2) using LDA ultrasoft pseudopotentials,
    starting from Lucas's geometry.

    Defaults:
      - nk   = 8  (8×8×8 Monkhorst-Pack grid)
      - ecut = 60 Ry (typical for LDA USPP, with ecutrho = 8*ecut)
    """

    # 1. Pseudopotentials: standard QE LDA ultrasoft set you've been using
    pseudopots = {
        "Si": PseudoPotential(
            ptype="uspp",
            element="Si",
            functional="LDA",
            name="Si_r.upf",
        ),
        "O": PseudoPotential(
            ptype="uspp",
            element="O",
            functional="LDA",
            name="O.pz-rrkjus.UPF",
        ),
    }

    # 2. Structure from Lucas's quartz_updated.py (ASE → labutil Struc)
    struc = make_quartz_struc()

    # 3. k-point grid (Monkhorst-Pack, with offset as in labs)
    kpts = Kpoints(gridsize=[nk, nk, nk], option="automatic", offset=True)

    # 4. Run directory (inside your current project folder)
    run_dirname = f"quartz_relax_LDA_nk{nk}_ecut{ecut}"
    runpath = Dir(path=os.path.join(os.getcwd(), run_dirname))

    # 5. QE input parameters (LDA, vc-relax, bfgs, etc.)
    input_params = PWscf_inparam(
        {
            "CONTROL": {
                "calculation": "vc-relax",
                "pseudo_dir": os.environ["QE_POTENTIALS"],
                "outdir": runpath.path,
                "tstress": True,
                "tprnfor": True,
                "disk_io": "none",
                "verbosity": "high",
            },
            "SYSTEM": {
                "ecutwfc": ecut,
                "ecutrho": ecut * 8,
                "input_dft": "LDA",
                "occupations": "fixed",  # quartz is an insulator
                # ibrav is handled via the structure (CELL_PARAMETERS + ATOMIC_POSITIONS)
            },
            "ELECTRONS": {
                "diagonalization": "david",
                "mixing_beta": 0.7,
                "conv_thr": 1.0e-8,
            },
            "IONS": {
                "ion_dynamics": "bfgs",
            },
            "CELL": {
                "cell_dynamics": "bfgs",
                "cell_dofree": "all",  # relax all cell parameters
            },
        }
    )

    # 6. Run QE using Lucas-style labutil call
    outfile = run_qe_pwscf(
        runpath=runpath,
        struc=struc,
        pseudopots=pseudopots,
        params=input_params,
        kpoints=kpts,
        ncpu=2,   # adjust if you want more cores
    )

    # 7. Parse output and print key relaxed quantities
    output = parse_qe_pwscf_output(outfile=outfile)

    print("\n=== QUARTZ vc-relax (LDA USPP) ===")
    print(f"nk = {nk}, ecut = {ecut} Ry\n")

    if "cell_parameters" in output:
        print("Final cell vectors (Å):")
        for line in output["cell_parameters"]:
            print("  ", line)

    if "atomic_positions" in output:
        print("\nFinal atomic positions (fractional):")
        for line in output["atomic_positions"]:
            print("  ", line)

    if "total_energy" in output:
        print("\nFinal total energy:", output["total_energy"])

    return output


if __name__ == "__main__":
    # Single, reasonably converged LDA quartz relaxation
    run_quartz_relax()

