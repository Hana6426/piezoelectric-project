#script where DFPT calculations are run. uses functions from utils/DFPT.py
import os
import sys
# Add project root to Python path so we can import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) #this is barbaric
from utils.DFPT import *

def main():
    molecule = 'quartz'
    ncpu = 4  # Number of processors to use



    #parse output
    phonon_data = parse_output(molecule)
    print(phonon_data)

main()