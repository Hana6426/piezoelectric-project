import sys
sys.path.append("/home/bond/piezoelectric-project")
import utils.Strain as Strain
import subprocess

material = "PbTiO3"
functional = "PBEsol"
nk = 8 #test values
ecut = 60 #test values
runfile = "PbTiO3_nk8_ecut60_relaxation/pwscf.out"
path = "/home/bond/piezoelectric-project/PBEsol/PbTiO3PBE/PbTiO3_nk8_ecut60_relaxation/strains/"

# Apply strain and relax
strain_type = "zz"
magnitude = -0.005
Strain.strain_and_relax(runfile, material, functional, strain_type, magnitude, path, nk, ecut)
# Run Berry phase calculation
Strain.Berry_phase_calculation(path + "zz_strain_-0.0050", material, functional, nk, ecut)