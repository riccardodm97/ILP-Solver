
from lib.utils import Parameters
from lib.domain import DomainProblem
import numpy as np
from lib.simplex import SimplexProblem
import unittest
from fractions import Fraction 
import os 
import json

class TestBase(unittest.TestCase):

    def _fract_to_dec(self, fract):
        if isinstance(fract, np.ndarray):
            if fract.dtype.type is np.str_:
                tmp = []
                for x in fract:
                    tmp.append(self._fract_to_dec(str(x)))
                val = np.array(tmp)
            else:
                val = fract

            val = np.around(val, Parameters.DECIMAL_PRECISION)
        else:
            if type(fract) == str:
                val = Fraction(fract)
                val = val.numerator / val.denominator
            else:
                val = fract

            val = round(val, Parameters.DECIMAL_PRECISION)
        return val

    def _get_base_dir(self):
        return os.path.join(os.path.dirname(__file__))

    def _test_simplex_problem_correctness(self, p):
        self.assertTrue(isinstance(p, SimplexProblem))

        self.assertTrue(isinstance(p.c, np.ndarray))
        self.assertTrue(isinstance(p.A, np.ndarray))
        self.assertTrue(isinstance(p.b, np.ndarray))
        self.assertTrue(isinstance(p.in_basis, np.ndarray))
        self.assertTrue(isinstance(p.out_basis, np.ndarray))
        self._test_carry_correctness(p)

    def _test_carry_correctness(self, p):
        self.assertTrue(isinstance(p.carry_matrix, np.ndarray))
        self.assertTrue(isinstance(p.get_y(), np.ndarray))
        #self.assertTrue(isinstance(carry.z, np.ndarray)) TODO: Check if scalar
        self.assertTrue(isinstance(p.get_inverse_matrix(), np.ndarray))
        self.assertTrue(isinstance(p.get_xb(), np.ndarray))

        self.assertEqual(p.carry_matrix[0,:-1], p.get_y())
        self.assertEqual(p.carry_matrix[0,-1], p.get_z())
        self.assertEqual(p.carry_matrix[1:,:-1] , p.get_inverse_matrix())
        self.assertEqual(p.carry_matrix[1:,-1], p.get_xb())

    def _create_problem(self, shape, A=None, b=None, c=None):
        constraints, vars = shape

        if A is None:
            A = np.zeros(shape)
        else:
            A = np.array(A)
        
        if b is None:
            b = np.zeros(constraints)
        else:
            b = np.array(b)

        if c is None:
            c = np.zeros(vars)
        else:
            c = np.array(c)

        return SimplexProblem(c, A, b)

    def _load_problems(self, problem_type):
        problems = {
            'integer': [],
            'decimal': []
        }
        for p in self._get_problem_files():
            with open(p) as json_file:
                problem = json.load(json_file)
                if problem.get('integer', False):
                    problems['integer'].append((DomainProblem.from_json(p), problem['solution']))
                else:
                    problems['decimal'].append((DomainProblem.from_json(p), problem['solution']))

        return problems[problem_type]

    def _get_problem_files(self):
        return [self._get_base_dir()+'/res/problem'+str(i)+'.json' for i in range(1, 16)]