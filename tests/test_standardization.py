import unittest
import os 
import numpy as np

from lib.utility import deserialize_problem, get_standard_form

class TestStandardization(unittest.TestCase):

    base_dir = os.path.join(os.path.dirname(__file__))

    def test_deserialization(self):
        for p in self.__get_problem_files():
            try:
                deserialize_problem(p)
            except Exception:
                self.fail("deserialize_problem raised Exception on " + p)

    def test_standardization(self):
        for p in self.__get_problem_files():
            problem, A, b, c = deserialize_problem(p)

            if 'standard' in problem['solution']:
                std_problem, chg = get_standard_form(problem, A, b, c)
                std_real = np.array(problem['solution']['standard']['form'])
                self.assertEqual(std_problem.shape, std_real.shape)

                if std_problem.shape == std_real.shape:
                    self.assertTrue((std_problem == std_real).all())

    def __get_problem_files(self):
        return [self.base_dir+'/res/problem'+str(i)+'.json' for i in range(1, 8)]