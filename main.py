from solver import resolve_with_assumptions
from print import print_result
from helpers import initial_possibilities_calculation
from grid_info import height, width
import numpy as np

print_result(resolve_with_assumptions(remaining_possibilities=initial_possibilities_calculation(),
                                      grid_state=np.zeros((height, width), dtype=int)))
