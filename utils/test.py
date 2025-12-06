import os
import sys
# Add project root to Python path so we can import utils
from DFPT import *


cell_params, atomic_positions, atomic_symbols = read_final_geometry('quartz_final_geometry.txt')
print(atomic_positions)
print(make_quartz_final())
