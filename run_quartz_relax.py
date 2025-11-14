# run_quartz_relax.py

import os
from labutil.plugins.pwscf import run_qe_pwscf, PWSCF_inparam, parse_qe_pwscf_output
from labutil.objects import Dir, Kpoints, PseudoPotential
from quartz_lucas import make_quartz_struc

# 1. Working directory
workdir = Dir('quartz_relax_lucas')

# 2. Structure from Lucas
struc = make_quartz_struc()

# 3. K-points (coarse first; you can tighten later)
kpts = Kpoints(mesh=[4, 4, 4], offset=[0, 0, 0])

# 4. Pseudopotentials
#   Use *exact* filenames from your pseudo directory (same ones you used in Al/quartz labs)
pseudo = PseudoPotential({
    'Si': 'Si.pbe-n-rrkjus_psl.1.0.0.UPF',
    'O':  'O.pbe-n-rrkjus_psl.1.0.0.UPF'
})

# 5. Input parameters for vc-relax
#   Names may vary slightly depending on labutil version — mirror your Lab 5 script!
inp = PWSCF_inparam(
    calculation='vc-relax',          # relax ions + cell
    prefix='quartz_lucas',
    pseudo_potential=pseudo,
    kpoints=kpts,
    ecutwfc=60.0,                    # adjust if your prof gave a specific value
    ecutrho=480.0,
    conv_thr=1.0e-8,
    forc_conv_thr=1.0e-4,
    cell_dofree='all',               # let all cell vectors relax
    ion_dynamics='bfgs',
    cell_dynamics='bfgs',
)

# 6. Run QE
#    Use the same qe_cmd and ncpu pattern you used in earlier labs
qe_cmd = 'pw.x'   # or full path if needed, e.g. '/n/holystore01/.../bin/pw.x'

outfile = run_qe_pwscf(
    struc=struc,
    inparam=inp,
    directory=workdir,
    qe_cmd=qe_cmd,
    ncpu=4
)

# 7. Parse output and print the final relaxed structure info
parsed = parse_qe_pwscf_output(outfile)

# Depending on your labutil version, 'parsed' is usually a dict-like object.
# The keys you care about: 'final_struc', 'final_energy', 'final_forces', 'final_stress'.
if 'final_struc' in parsed:
    final_struc = parsed['final_struc']
    print("\n=== RELAXED QUARTZ (Lucas start) ===")
    print("Final lattice vectors (Å):")
    for v in final_struc.cell:
        print("  ", v)

    print("\nAtomic positions (fractional):")
    for sp, pos in zip(final_struc.species, final_struc.frac_coords):
        print(f"  {sp:2s}  {pos[0]:8.5f}  {pos[1]:8.5f}  {pos[2]:8.5f}")

if 'final_energy' in parsed:
    print("\nFinal total energy (Ry):", parsed['final_energy'])

if 'final_forces' in parsed:
    print("Max |force| (Ry/Bohr):", max(parsed['final_forces']))
