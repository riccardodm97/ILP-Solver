import numpy as np
import json
from enum import Enum

class SimplexSolution(Enum):
    FINITE = 1
    UNLIMITED = 2
    IMPOSSIBLE = 3
  
def deserialize_problem(file_path):
    with open(file_path) as json_file:
        problem = json.load(json_file)
    
    constraints = []
    constants = []
    for index, constraint in enumerate(problem['constraints']):
        constraints.append(constraint['coefficients'])
        constants.append(constraint['constant'])

    return problem, np.array(constraints), np.array(constants), np.array(problem['objective']['costs'])

def get_standard_form(problem, A, b, c):
    Ac = np.r_[[c], A]
    rows, cols = Ac.shape

    # 1. Change objective function to minimization
    if problem['objective']['optmimization'] == 'MAX':
        problem['objective']['costs'] *= -1
        problem['objective']['optmimization'] = 'MIN'
        Ac[0,:] *= -1


    # 2. Perform variable change over non-positive variables
    positive_variables = np.zeros(cols, dtype=bool)

    for i in range(cols):
        if i in problem['non-negatives']:
            positive_variables[i] = True

    for var in np.where(positive_variables == False):
        if 'non-positives' in problem and var in problem['non-positives']:
            Ac[:, var] *= -1
        else: 
            Ac = np.c_[Ac, Ac[:, var] * -1]

    # 3. Add slack variables to change constraints into equations
    for index, constraint in enumerate(problem['constraints']):
        if constraint['type'] != 'EQ':
            Ac = np.c_[Ac, np.zeros(rows)]
            
            if constraint['type'] == 'LEQ':
                Ac[index + 1,-1] = 1
            elif constraint['type'] == 'GEQ':
                Ac[index + 1,-1] = -1

    matrix = np.c_[Ac, np.insert(b, 0, 0)]

    # 4. Constant terms should be positive or 0
    for index, const in enumerate(b):
        if const < 0:
            matrix[index + 1, :] *= -1

    return matrix