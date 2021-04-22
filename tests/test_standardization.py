import unittest

from lib.utility import deserialize_problem, get_standard_form

import os 

class TestStandardization(unittest.TestCase):

    base_dir = os.path.join(os.path.dirname(__file__))
    problem_files = [base_dir+'/res/problem1.json', base_dir+'/res/problem2.json']

    def test_deserialization(self):
        for p in self.problem_files:
            try:
                deserialize_problem(p)
            except Exception:
                self.fail("deserialize_problem raised Exception on " + p)

    def test_standardization(self):
        for p in self.problem_files:
            problem, A, b, c = deserialize_problem(p)

            if 'standard' in problem:
                std_problem = get_standard_form(problem, A, b, c)
                self.assertTrue((std_problem == problem['standard']).all())