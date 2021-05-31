from tests.test_base import TestBase
import unittest
import numpy as np 
from fractions import Fraction
import os
import json

from lib.simplex import *
from lib.domain import DomainProblem

class TestBaseProblem(TestBase):

    def test_getters(self):
        pass #TODO (+ get_Aj)

    def test_setters(self):
        pass #TODO

    def test_check_basis(self):
        pass #TODO

    def test_find_initial_basis(self):
        ps = [
            self._create_problem((4,4), A=[
                [0, 0, 1], 
                [1, 0, 0], 
                [0, 1, 0]
            ]),
            self._create_problem((4,4), A=[
                [7, 0, 0], 
                [0, 0, 1], 
                [0, 1, 0]
            ]),
            self._create_problem((4,4), A=[
                [0, 0, 0], 
                [0, 0, 0], 
                [1, 1, 1]
            ]),
            self._create_problem((4,4), A=[
                [22, 0, -2, 1, 4], 
                [3, 0, 4, 0, 3], 
                [54, 1, 2, 0, 2]
            ]),
        ]

        sols = [
            [2, 0, 1], [-1, 2, 1], [-1, -1, 0], [3, -1, 1]
        ]

        for p, sol in zip(ps, sols):
            sol = np.array(sol)
            p.find_initial_basis()
            self.assertEqual(p.in_basis.shape, sol.shape)

            if p.in_basis.shape == sol.shape:
                self.assertTrue((p.in_basis == sol).all())

    def test_init_carry(self):
        pass #TODO

    def test_compute_out_of_base(self):
        ps = [
            self._create_problem((4,4), A=[
                [0, 0, 1], 
                [1, 0, 0], 
                [0, 1, 0]
            ]),
            self._create_problem((4,4), A=[
                [7, 0, 0], 
                [0, 0, 1], 
                [0, 1, 0]
            ]),
            self._create_problem((4,4), A=[
                [0, 0, 0], 
                [0, 0, 0], 
                [1, 1, 1]
            ]),
            self._create_problem((4,4), A=[
                [22, 0, -2, 1, 4], 
                [3, 0, 4, 0, 3], 
                [54, 1, 2, 0, 2]
            ]),
        ]

        sols = [
            [], [0], [1, 2], [0, 2, 4]
        ]

        for p, sol in zip(ps, sols):
            sol = np.array(sol)
            p.find_initial_basis()
            p.compute_out_of_base()
            self.assertEqual(p.out_basis.shape, sol.shape)

            if p.out_basis.shape == sol.shape:
                self.assertTrue((p.out_basis == sol).all())
        
    def test_swap_vars(self):
        pass #TODO

    def test_determine_entering_var(self):
        # p.determine_entering_var()
        pass #TODO

    def test_determine_exiting_var(self):
        # p.determine_exiting_var(ent_var)
        pass #TODO

    def test_update_carry(self):
        pass #TODO

class TestArtificialSimplexProblem(TestBase):
    def test_find_initial_basis(self):
        pass #TODO

    def test_check_basis(self):
        pass #TODO

    def test_substitute_artificial_vars(self):
        pass #TODO

class TestBaseFunctions(TestBase):

    def test_define_artificial_problem(self):
        for i in range(10):
            p = self._create_problem((4,4))
            p.find_initial_basis()
            p.set_inverse_matrix()
            c,A,b,art_vars = define_artificial_problem(p)

            #create object 
            ap = SimplexArtificialProblem(c,A,b,art_vars,p.in_basis.copy())
            
            #self._test_simplex_problem_correctness(ap)
            #self.assertFalse((ap.in_basis == -1).any())
            # TODO ap should have more coefficients than
    
    def test_domain_problem_solve(self):
        for dp, solution in self._load_problems('decimal'):
            #print("Solving problem:", dp.optimization_type, "z ="," + ".join([str(x) + "x" + str(i+1) for i, x in enumerate(dp.costs)]))
            ret, opt, sol = dp.solve()

            self.assertEqual(ret.value, solution['type'])

            if ret is SimplexSolution.FINITE:
                arr = self._fract_to_dec(np.array(solution['values']))

                self.assertEqual(sol.shape, arr.shape)
                if sol.shape == arr.shape:
                    self.assertTrue((sol == arr).all())

                self.assertEqual(opt, self._fract_to_dec(solution['optimum']))
                
    def test_from_p1_to_p2(self):
        pass #TODO
          
    def test_phase1(self):
        pass #TODO

    def test_phase2(self):
        pass #TODO