# contains basic functions to calculate constants (piezoelectric, elastic etc) from DFT outputs

import os
import sys
sys.path.append("/home/bond/piezoelectric-project")
import utils.DFPT as DFPT
import numpy as np

def parse_berry_phase_output(output_path):
    # Parse the Berry phase output file to extract polarization data
    polarization_data = {}
    with open(output_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "Polarization" in line:
                parts = line.split()
                strain = float(parts[2])
                polarization = float(parts[4])
                polarization_data[strain] = polarization
    return polarization_data


def calculate_piezoelectric_constants(berry_phase_paths, strain_type):
    # Extract relevant data from Berry phase outputs
    #@ :param berry_phase_paths: dictionary of "plus", "minus" paths to berry phase outputs
    polarization_data = {}
    for key, path in berry_phase_paths.items():
        polarization_data[key] = parse_berry_phase_output(path)
    
    #assuming strain is 0.01 and -0.01 for plus and minus respectively
    delta_polarization = polarization_data["plus"][0.01] - polarization_data["minus"][-0.01]
    piezoelectric_constant = delta_polarization / (0.01 - (-0.01))
    print("piezoelectric strain constant for {} strain: {}".format(strain_type, piezoelectric_constant))
    return piezoelectric_constant
