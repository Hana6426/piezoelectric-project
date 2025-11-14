import os
from labutil.plugins.pwscf import run_qe_pwscf, PWscf_inparam, parse_qe_pwscf_output
from labutil.objects import Dir, Kpoints, PseudoPotential
from baseline_lattice.structures import make_PbTiO3_struc

def relax_once(nk=6, ecut=60):
    pseudos_dir = "./pseudos"
    pseudopots = {
        "Pb": PseudoPotential(ptype="uspp", element="Pb", functional="LDA", name="Pb.pz-d-van.UPF"),
        "Ti": PseudoPotential(ptype="uspp", element="Ti", functional="LDA", name="Ti.pz-sp-van_ak.UPF"),
        "O" : PseudoPotential(ptype="uspp", element="O",  functional="LDA", name="O.pz-van_ak.UPF"),
    }
    struc = make_PbTiO3_struc()
    kpts = Kpoints(gridsize=[nk, nk, nk], option="automatic", offset=False)

    runpath = Dir(path=os.path.join("./tmp_baselines/PbTiO3_relaxations", f"PbTiO3_nk{nk}_ecut{ecut}"))
    params = PWscf_inparam({
        "CONTROL": {
            "calculation": "vc-relax",
            "pseudo_dir": pseudos_dir,
            "outdir": runpath.path,
            "tstress": True,
            "tprnfor": True,
            "disk_io": "none",
        },
        "SYSTEM": {
            "ecutwfc": ecut,
            "ecutrho": int(ecut * 9),
            "occupations": "fixed",
            "input_dft": "LDA",
        },
        "ELECTRONS": {
            "diagonalization": "david",
            "mixing_beta": 0.3,
            "conv_thr": 1e-8,
        },
        "IONS": {"ion_dynamics": "bfgs"},
        "CELL": {"cell_dynamics": "bfgs"},
    })

    outfile = run_qe_pwscf(runpath=runpath, struc=struc, pseudopots=pseudopots, params=params, kpoints=kpts, ncpu=2)
    return parse_qe_pwscf_output(outfile=outfile)

if __name__ == "__main__":
    out = relax_once(nk=6, ecut=60)
    print("Energy (eV):", out.get("energy"), "Volume (Å^3):", out.get("volume"))
