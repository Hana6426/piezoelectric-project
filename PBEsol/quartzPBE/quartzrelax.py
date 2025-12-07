import sys
sys.path.append("/home/bond/piezoelectric-project")
import utils.Relax as Relax
import subprocess


material = "quartz"
functional = "PBEsol"
nk = 10
ecut = 60
path = "/home/bond/piezoelectric-project/PBEsol/quartzPBE/"
Relax.relax_structure_dft(material, functional, nk, ecut, path)
