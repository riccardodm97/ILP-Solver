import unittest
import numpy as np 
from fractions import Fraction
import os

from lib.simplex import *
from lib.utility import deserialize_problem, get_original_problem_sol, get_standard_form

class TestSimplex(unittest.TestCase):
        
    def _fract_to_dec(self, fract):
        if isinstance(fract, np.ndarray):
            if fract.dtype.type is np.str_:
                tmp = []
                for x in fract:
                    tmp.append(self._fract_to_dec(str(x)))
                val = np.array(tmp)
            else:
                val = fract

            val = np.around(val, SimplexProblem.DECIMAL_PRECISION)
        else:
            if type(fract) == str:
                val = Fraction(fract)
                val = val.numerator / val.denominator
            else:
                val = fract

            val = round(val, SimplexProblem.DECIMAL_PRECISION)
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


    def _load_problems(self):
        problems = []
        for p in [self._get_base_dir()+'/res/problem'+str(i)+'.json' for i in range(1, 16)]:
            if p in [self._get_base_dir()+'/res/problem'+str(i)+'.json' for i in [9, 11, 13, 15]]:
                x = 1 #TODO Fix
                continue
            problem, A, b, c = deserialize_problem(p)
            std_problem, var_chg_map = get_standard_form(problem, A, b, c)
            problems.append((problem, std_problem[1:,:-1], std_problem[1:,-1], std_problem[0,0:-1], var_chg_map))

        return problems

class TestSimplexProblem(TestSimplex):

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

class TestArtificialSimplexProblem(TestSimplex):
    def test_find_initial_basis(self):
        pass #TODO

    def test_check_basis(self):
        pass #TODO

    def test_substitute_artificial_vars(self):
        pass #TODO

class TestSimplexFunctions(TestSimplex):

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
    
    def test_simplex_algorithm(self):
        problems = self._load_problems()
        for p, A, b, c, var_chg_map in problems:
            print("Solving problem:", p['objective']['optimization'], "z ="," + ".join([str(x) + "x" + str(i+1) for i, x in enumerate(p['objective']['costs'])]))
            ret, opt, sol = simplex_algorithm(c, A, b)

            if 'type' in p['solution']:
                self.assertEqual(ret.value, p['solution']['type'])
            else:
                print("Value not specified")

            if ret is SimplexSolution.FINITE:
                if 'values' in p['solution']['standard']:
                    arr = self._fract_to_dec(np.array(p['solution']['standard']['values']))
                    
                    self.assertEqual(sol.shape, arr.shape)
                    if sol.shape == arr.shape:
                        self.assertTrue((sol == arr).all())
                else:
                    print("Value not specified")

                if 'values' in p['solution']:
                    sol = get_original_problem_sol(sol, var_chg_map)
                    arr = self._fract_to_dec(np.array(p['solution']['values']))

                    self.assertEqual(sol.shape, arr.shape)
                    if sol.shape == arr.shape:
                        self.assertTrue((sol == arr).all())
                else:
                    print("Value not specified")


                if 'optimum' in p['solution']['standard']:
                    self.assertEqual(opt, self._fract_to_dec(p['solution']['standard']['optimum']))
                else:
                    print("Value not specified")

                if 'optimum' in p['solution'] and False:
                    #TODO: -opt if max problem
                    self.assertEqual(opt, self._fract_to_dec(p['solution']['optimum']))
                else:
                    print("Value not specified")
                
    def test_from_p1_to_p2(self):
        pass #TODO
          
    def test_phase1(self):
        pass #TODO

    def test_phase2(self):
        pass #TODO