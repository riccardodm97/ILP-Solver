from lib.utils import ProblemSolution
from lib.bb import bb_algorithm
from tests.test_base import TestBase
import numpy as np


class TestBranchAndBound(TestBase):
    
    def test_get_problem_sol(self):
        for p, solution in self._load_problems('integer'):
            std_problem, chg = p.get_standard_form()
            ret_type, opt, sol = bb_algorithm(std_problem, chg, p.optimization_type)
            self.assertEqual(ret_type.value, solution['type'])

            if ret_type is ProblemSolution.FINITE:
                self.assertEqual(opt, self._fract_to_dec(solution['optimum']))
                # self.assertTrue((sol == self._fract_to_dec(np.array(solution['values']))).all())
