#script where DFPT calculations are run. uses functions from utils/DFPT.py
import os
import sys
# Add project root to Python path so we can import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) #this is barbaric
from utils.DFPT import *


def main():
    molecule = 'PbTiO3'
    ncpu = 4   # Number of processors to use
    
    #runpath = run_scf(molecule, ncpu = ncpu)
    #ph_outpath = run_qe_ph(molecule, ncpu=ncpu)
    results = parse_phonon_output(molecule)
    print("Dielectric Tensor:")
    print(results['dielectric_tensor'])
    #save data to a dielectric tensor file
    with open(os.path.join('/home/bond/piezoelectric-project/pzt/dfpt/PbTiO3_scf', 'dielectric_tensor.txt'), 'w') as f:
        f.write("Dielectric Tensor:\n")
        for row in results['dielectric_tensor']:
            f.write(" ".join(f"{val:.6f}" for val in row) + "\n")


main()

