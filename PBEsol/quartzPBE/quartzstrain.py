import sys
sys.path.append("/home/bond/piezoelectric-project")
import utils.Strain as Strain
import subprocess


material = "quartz"
functional = "PBEsol"
nk = 6 #test values
ecut = 60 #test values
runfile = "SiO2_nk6_ecut60_relaxation/pwscf.out"
path = "/home/bond/piezoelectric-project/PBEsol/quartzPBE/SiO2_nk6_ecut60_relaxation/strains/"

# Apply strain and relax
strain_type = "xx"
magnitude = -0.01
#Strain.strain_and_relax(runfile, material, functional, strain_type, magnitude, path, nk, ecut)
# Run Berry phase calculation
Strain.Berry_phase_calculation(path + "xx_strain_-0.0100", material, functional, nk, ecut)