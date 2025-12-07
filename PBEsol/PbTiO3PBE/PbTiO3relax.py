import sys
sys.path.append("/home/bond/piezoelectric-project")
import utils.Relax as Relax
import subprocess


material = "PbTiO3"
functional = "PBEsol"
nk = 8
ecut = 60
path = "/home/bond/piezoelectric-project/PBEsol/PbTiO3PBE/"
Relax.relax_structure_dft(material, functional, nk, ecut, path)
