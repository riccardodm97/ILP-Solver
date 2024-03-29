from fractions import Fraction
from lib import logger
from lib.bb import bb_algorithm
from lib.simplex import simplex_algorithm
from lib.utils import DomainConstraintType, DomainOptimizationType, ProblemSolution
import numpy as np
import json

class DomainProblem:

    def __init__(self, costs, optimization_type, constraints=[], non_negatives=None, non_positives=[], is_integer=False):
        if non_negatives is None:
            non_negatives = np.arange(costs.size)

        self.costs = costs
        self.constraints = constraints
        self.non_positives = non_positives
        self.optimization_type = optimization_type
        self.is_integer = is_integer
        self.non_negatives = non_negatives

        self._constraint_array = None
        self._constants_array = None

    @staticmethod
    def from_matrix(matrix, type=DomainOptimizationType.MIN, non_negatives=None, non_positives=[], is_integer=False):
        A, b, c = matrix[1:,:-1], matrix[:,-1], matrix[0,:]

        return DomainProblem.from_abc(A, b, c, type, non_negatives, non_positives, is_integer)

    @staticmethod
    def from_abc(A, b, c, type=DomainOptimizationType.MIN, non_negatives=None, non_positives=[], is_integer=False):
        constraints = []
        for coefficients, constant in zip(A, b):
            constraints.append(DomainConstraint(coefficients, constant, DomainConstraintType.EQUAL))

        return DomainProblem(np.array(c), type, constraints, non_negatives, non_positives, is_integer)

    @staticmethod
    def from_json(filename):
        with open(filename) as json_file:
            problem = json.load(json_file)
        
        constraints = []
        for constraint in problem['constraints']:
            constraints.append(DomainConstraint(constraint['coefficients'], constraint['constant'], {
            'EQ': DomainConstraintType.EQUAL,
            'LEQ': DomainConstraintType.LESS_EQUAL,
            'GEQ': DomainConstraintType.GREAT_EQUAL
        }[constraint['type']]))

        #p, A, b, c = problem, np.array(constraints), np.array(constants), np.array(problem['objective']['costs'])
        return DomainProblem(np.array(problem['objective']['costs']), {
            'MIN': DomainOptimizationType.MIN,
            'MAX': DomainOptimizationType.MAX
        }[problem['objective']['optimization']], constraints, problem['non-negatives'], problem.get('non-positives', []), problem.get('integer', False))

    def add_constraint(self, c):
        self.constraints.append(c)

    def get_constraint_array(self):
        if self._constraint_array is None:
            self._constraint_array = np.array([c.coefficients for c in self.constraints])
        return self._constraint_array

    def get_constants_array(self):
        if self._constants_array is None:
            self._constants_array = np.array([c.constant for c in self.constraints])
        return self._constants_array

    def get_standard_form(self):
        logger.write("\nTurning the problem into standard form")
        Ac = np.r_[[self.costs], self.get_constraint_array()]

        # Sets the variable-change map only if the variable is present in the objective function
        var_chg_map = {i: [{'var': i, 'coeff': 1 if self.costs[i] != 0 else 0}] for i in range(self.costs.size)}
        rows, cols = Ac.shape

        # 1. Change objective function to minimization
        if self.optimization_type is DomainOptimizationType.MAX:
            logger.write("Changing the objective function into a minimization function")
            Ac[0,:] *= -1

        # 2. Perform variable change over non-positive variables
        positive_variables = np.zeros(cols, dtype=bool)

        for i in range(cols):
            if i in self.non_negatives:
                positive_variables[i] = True

        for var in np.where(positive_variables == False):
            if var in self.non_positives:
                logger.write("Changing the sign of the negative variable/s " + str(var))
                Ac[:, var] *= -1
                var_chg_map[var[0]][0]['coeff'] = -1
            elif var.size > 0:
                logger.write("Perform variable change for variable/s " + str(var))
                _, Ac_cols = Ac.shape
                var_chg_map[var[0]].append({'var': Ac_cols, 'coeff': -1})
                Ac = np.c_[Ac, Ac[:, var] * -1]

        # 3. Add slack variables to change constraints into equations
        for index, constraint in enumerate(self.constraints):
            if constraint.type != DomainConstraintType.EQUAL:
                logger.write("Adding slack variable for constraint " + str(index))
                Ac = np.c_[Ac, np.zeros(rows)]
                
                if constraint.type == DomainConstraintType.LESS_EQUAL:
                    Ac[index + 1,-1] = 1
                elif constraint.type == DomainConstraintType.GREAT_EQUAL:
                    Ac[index + 1,-1] = -1

        matrix = np.c_[Ac, np.insert(self.get_constants_array(), 0, 0)]

        # 4. Constant terms should be positive or 0
        for index, const in enumerate(self.get_constants_array()):
            if const < 0:
                logger.write("Inverting sign of constraint because of negative constant term")
                matrix[index + 1, :] *= -1

        return matrix, var_chg_map

    def get_problem_sol(self, optimum, standard_sol, var_chg_map):
        sol = np.array([sum([factor['coeff'] * standard_sol[factor['var']] for factor in factors]) for factors in var_chg_map.values()])
        return (optimum if self.optimization_type is DomainOptimizationType.MIN else -optimum), sol

    def solve(self):
        standard_matrix, var_chg_map = self.get_standard_form()

        if self.is_integer:
            ret, std_opt, std_sol = bb_algorithm(standard_matrix, var_chg_map, self.optimization_type)
            opt, sol = std_opt, std_sol 
        else:
            ret, std_opt, std_sol = simplex_algorithm(standard_matrix[0,:-1], standard_matrix[1:,:-1], standard_matrix[1:,-1])
            opt, sol = self.get_problem_sol(std_opt, std_sol, var_chg_map) if ret is ProblemSolution.FINITE else (None, None)

        logger.write("The problem is "+ret.name)
        if ret is ProblemSolution.FINITE: 
            logger.write("The variables values are", sol, "with optimum value", opt)
        
        return ret, opt, sol 

class DomainConstraint:

    def __init__(self, coefficients, constant, const_type):
        self.coefficients = []
        for c in coefficients:
            if type(c) == str:
                val = Fraction(c)
                val = val.numerator / val.denominator
            else:
                val = c
            self.coefficients.append(val)
            
        self.coefficients = np.array(self.coefficients)
        self.constant = constant
        self.type = const_type
