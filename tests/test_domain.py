from lib.simplex import simplex_algorithm
from lib.utils import ProblemSolution
from lib.domain import DomainProblem
from tests.test_base import TestBase
import numpy as np

class TestDomainProblem(TestBase):

    def test_static_from_matrix(self):
        #(matrix, type=DomainOptimizationType.MIN, non_negatives=[], non_positives=[], is_integer=False)
        pass #TODO

    def test_static_from_abc(self):
        #(A, b, c, type=DomainOptimizationType.MIN, non_negatives=[], non_positives=[], is_integer=False)
        pass #TODO

    def test_static_from_json(self):
        for p in self._get_problem_files():
            try:
                DomainProblem.from_json(p)
            except Exception:
                self.fail("deserialize_problem raised Exception on " + p)

    def test_get_constraint_array(self):
        pass #TODO

    def test_get_constants_array(self):
        pass #TODO

    def test_get_standard_form(self):
        for p, solution in self._load_problems('decimal'):
            std_problem, chg = p.get_standard_form()
            std_real = np.array(solution['standard']['form'])
            self.assertEqual(std_problem.shape, std_real.shape)

            if std_problem.shape == std_real.shape:
                self.assertTrue((std_problem == std_real).all())
    
    def test_get_problem_sol(self):
        #(self, optimum, standard_sol, var_chg_map):
        for p, solution in self._load_problems('decimal'):
            std_problem, chg = p.get_standard_form()
            ret_type, std_opt, std_sol = simplex_algorithm(std_problem[0,:-1], std_problem[1:,:-1], std_problem[1:,-1])

            self.assertEqual(ret_type.value, solution['type'])

            if ret_type is ProblemSolution.FINITE:
                opt, sol = p.get_problem_sol(std_opt, std_sol, chg)
                self.assertEqual(opt, self._fract_to_dec(solution['optimum']))
                self.assertTrue((sol == self._fract_to_dec(np.array(solution['values']))).all())

    def test_solve(self):
        pass #TODO
