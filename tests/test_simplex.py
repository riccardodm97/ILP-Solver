from fractions import Fraction
import os
import unittest
import numpy as np 

from lib.simplex import find_initial_basis, compute_out_of_base, create_artificial_problem, \
    determine_entering_var, determine_exiting_var, determine_exiting_var, init_carry, \
    change_basis, start_simplex, phase1, phase2, SupportData, Carry
from utility import deserialize_problem, get_standard_form

class TestSimplex(unittest.TestCase):

    base_dir = os.path.join(os.path.dirname(__file__))

    def test_find_initial_basis(self):
        self.assertEqual(find_initial_basis(np.array([
            [0, 0, 1], 
            [1, 0, 0], 
            [0, 1, 0]
        ])), [2, 0, 1])

        self.assertEqual(find_initial_basis(np.array([
            [7, 0, 0], 
            [0, 0, 1], 
            [0, 1, 0]
        ])), [-1, 2, 1])

        self.assertEqual(find_initial_basis(np.array([
            [0, 0, 0], 
            [0, 0, 0], 
            [1, 1, 1]
        ])), [-1, -1, 0])

        self.assertEqual(find_initial_basis(np.array([
            [22, 0, -2, 1, 4], 
            [3, 0, 4, 0, 3], 
            [54, 1, 2, 0, 2]
        ])), [3, -1, 1])
        
    def test_compute_out_of_base(self):
        ps = [
            self.__create_random_data((4,4), A=[
                [0, 0, 1], 
                [1, 0, 0], 
                [0, 1, 0]
            ]),
            self.__create_random_data((4,4), A=[
                [7, 0, 0], 
                [0, 0, 1], 
                [0, 1, 0]
            ]),
            self.__create_random_data((4,4), A=[
                [0, 0, 0], 
                [0, 0, 0], 
                [1, 1, 1]
            ]),
            self.__create_random_data((4,4), A=[
                [22, 0, -2, 1, 4], 
                [3, 0, 4, 0, 3], 
                [54, 1, 2, 0, 2]
            ]),
        ]

        sols = [
            [], [0], [1, 2], [0, 2]
        ]

        for p, sol in zip(ps, sols):
            p.in_base = find_initial_basis(p.A)
            compute_out_of_base(p)
            self.assertTrue((np.array(p.out_base) == np.array(sol)).all())
        
    def test_create_artificial_problem(self):
        for i in range(10):
            p = self.__create_random_data((4,4))
            ap = create_artificial_problem(p)
            
            self.__test_support_data_correctness(ap)
            self.assertFalse((ap.in_base == -1).any())
            # TODO ap should have more coefficients than
        
    def test_from_p1_to_p2(self):
        pass
        # from_p1_to_p2(ap, p) TODO
        
    def test_determine_entering_var(self):
        p = self.__create_random_data((3,3), A=[
            
        ], b=[], c=[])
        determine_entering_var(p)
        
    def test_determine_exiting_var(self):
        pass
        # determine_exiting_var(data, Aj) TODO 
        
    def test_init_carry(self):
        p = self.__create_random_data((3, 4))
        init_carry(p)
        self.__test_carry_correctness(p.carry)

    def test_change_basis(self):
        
        change_basis(data, h, Aj, cost)
        
    def test_start_simplex(self):
        problems = self.__load_problems()
        for p, A, b, c in problems:
            data = SupportData(c, A, b)
            sol = start_simplex(data)

            if 'value' in p['solution']:
                if type(p['solution']['value']) == str:
                    sol_real = Fraction(p['solution']['value'])
                    sol_real = sol_real.numerator / sol_real.denominator
                else:
                    sol_real = p['solution']['value']
                self.assertEqual(sol, sol_real)

    def test_phase1(self):
        phase1(data)

    def test_phase2(self):
        phase2(data)

    def __test_support_data_correctness(self, p):
        self.assertTrue(isinstance(p, SupportData))

        self.assertTrue(isinstance(p.c, np.array))
        self.assertTrue(isinstance(p.A, np.array))
        self.assertTrue(isinstance(p.b, np.array))
        self.assertTrue(isinstance(p.in_base, np.array))
        self.assertTrue(isinstance(p.out_base, np.array))
        self.assertTrue(isinstance(p.carry, Carry))

        self.__test_carry_correctness(p.carry)

    def __test_carry_correctness(self, carry):
        self.assertTrue(isinstance(carry, Carry))

        self.assertTrue(isinstance(carry.matrix, np.array))
        self.assertTrue(isinstance(carry.y, np.array))
        #self.assertTrue(isinstance(carry.z, np.array)) TODO: Check if scalar
        self.assertTrue(isinstance(carry.inverse_matrix, np.array))
        self.assertTrue(isinstance(carry.xb, np.array))

        self.assertEqual(carry.matrix[0,:-1], carry.y)
        self.assertEqual(carry.matrix[0,-1], carry.z)
        self.assertEqual(carry.matrix[1:,:-1] , carry.inverse_matrix)
        self.assertEqual(carry.matrix[1:,-1], carry.xb)

    def __create_random_data(self, shape, A=None, b=None, c=None):
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

        return SupportData(c, A, b)


    def __load_problems(self):
        problems = []
        for p in [self.base_dir+'/res/problem'+str(i)+'.json' for i in range(1, 8)]:
            problem, A, b, c = deserialize_problem(p)
            std_problem = get_standard_form(problem, A, b, c)
            problems.append((problem, std_problem[1:,:-1], std_problem[1:,-1], std_problem[0,0:-1]))

        return problems