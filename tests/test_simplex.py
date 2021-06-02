from tests.test_base import TestBase
import unittest
import numpy as np 
from fractions import Fraction
import os
import json

from lib.simplex import *
from lib.domain import DomainProblem

class TestBaseProblem(TestBase):

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

class TestBaseFunctions(TestBase):
    
    def test_domain_problem_solve(self):
        for dp, solution in self._load_problems('decimal'):
            #print("Solving problem:", dp.optimization_type, "z ="," + ".join([str(x) + "x" + str(i+1) for i, x in enumerate(dp.costs)]))
            ret, opt, sol = dp.solve()

            self.assertEqual(ret.value, solution['type'])

            if ret is ProblemSolution.FINITE:
                arr = self._fract_to_dec(np.array(solution['values']))

                self.assertEqual(sol.shape, arr.shape)
                if sol.shape == arr.shape:
                    self.assertTrue((sol == arr).all())

                self.assertEqual(opt, self._fract_to_dec(solution['optimum']))
                