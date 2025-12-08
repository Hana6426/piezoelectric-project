import sys
import os
sys.path.append("/home/bond/piezoelectric-project") #this is barbaric

import numpy as np
from utils.DFPT import parse_phonon_output
from utils.DFPT import run_qe_ph




molecule = 'PbTiO3'
ncpu = 4   # Number of processors to use

ph_outpath = run_qe_ph(molecule, ncpu=ncpu)
results = parse_phonon_output(molecule)
print("Dielectric Tensor:")
print(results['dielectric_tensor'])
#save data to a dielectric tensor file
with open('dielectric_tensor.txt', 'w') as f:
    f.write("Dielectric Tensor:\n")
    for row in results['dielectric_tensor']:
        f.write(" ".join(f"{val:.6f}" for val in row) + "\n")