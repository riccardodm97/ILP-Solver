from lib import logger
import math
from collections import deque
import numpy as np
from typing import Tuple

from lib.utils import SimplexSolution, DomainOptimizationType
from lib.simplex import simplex_algorithm

class BBNode:
    def __init__(self, std_problem, variables, coefficients, val, slack_coeff, var_chg_map):
        self.std_problem = std_problem.copy()
        self.var_chg_map = var_chg_map
        self.child_left, self.child_right = None, None
        self.sol = None
        self.opt = None

        if variables is not None:
            rows, cols = self.std_problem.shape
            new_row = np.zeros(cols+1)
            new_row[variables] = coefficients
            new_row[-1] = val
            new_row[-2] = slack_coeff

            self.std_problem = np.c_[self.std_problem[:,:-1], np.zeros(rows), self.std_problem[:,-1]]
            self.std_problem = np.r_[self.std_problem, [new_row]]

    def solve(self, optimization_type):
        ret, std_opt, std_sol = simplex_algorithm(self.std_problem[0,:-1], self.std_problem[1:,:-1], self.std_problem[1:,-1])
        
        if ret is SimplexSolution.FINITE:
            self.sol = np.array([sum([factor['coeff'] * std_sol[factor['var']] for factor in factors]) for factors in self.var_chg_map.values()])
            self.opt = std_opt if optimization_type == DomainOptimizationType.MIN else -1 * std_opt
        return ret

    def is_int(self):
        return np.all(np.mod(self.sol, 1) == 0)

class BBTree:
    def __init__(self, std_problem, var_chg_map, optimization_type):
        self.std_problem = std_problem
        self.var_chg_map = var_chg_map
        self.optimization_type = optimization_type
        
        self.working_memory = deque([BBNode(self.std_problem, None, None, None, None, self.var_chg_map)])

        self.best_node = None

    def solve(self) -> Tuple[SimplexSolution,BBNode] :
        logger.write("Solving original problem")
        while self.working_memory:
            node = self.working_memory.popleft()
            ret_type = node.solve(self.optimization_type)
            #TODO: BFS / DFS (working_memory ordering)

            if ret_type is SimplexSolution.UNLIMITED:
                return ret_type, None

            if ret_type is SimplexSolution.IMPOSSIBLE:
                logger.write("The problem is impossible - Pruning by infeasibility")
            elif self.is_worse(node): 
                logger.write("The found solution is worse than the best one - Pruning by bound")
            else:
                if node.is_int():
                    logger.write("Integer solution found:", node.sol, " - Pruning by integrality")
                    self.best_node = node # Pruned by integrality
                else:
                    logger.write("Branching tree")
                    self.branch(node) # Branch

        return SimplexSolution.FINITE if self.best_node is not None else SimplexSolution.IMPOSSIBLE, self.best_node

    def is_worse(self, node : BBNode) -> bool:
        if self.best_node is None:
            return False
        return node.opt <= self.best_node.opt if self.optimization_type == DomainOptimizationType.MAX else node.opt >= self.best_node.opt 

    def branch(self, node : BBNode):
        idx=np.argmax(node.sol-np.trunc(node.sol))
        val = node.sol[idx]

        variables = [d['var'] for d in self.var_chg_map[idx]]
        coefficients = [d['coeff'] for d in self.var_chg_map[idx]]

        logger.write(str(idx) + " variable chosen for branching")
        logger.write("Adding ", idx, "<= ", math.floor(val), "and", idx, ">= ", math.ceil(val), " constraints")
        node.child_left = BBNode(node.std_problem, variables, coefficients, math.floor(val), 1, self.var_chg_map)
        node.child_right = BBNode(node.std_problem, variables, coefficients, math.ceil(val), -1, self.var_chg_map)
        self.working_memory.append(node.child_left)
        self.working_memory.append(node.child_right)

def bb_algorithm(std_problem, var_chg_map, optimization_type):
    logger.write("\nStarting Branch and Bound algorithm")
    tree = BBTree(std_problem, var_chg_map, optimization_type)
    ret, best_node = tree.solve()

    if ret is SimplexSolution.FINITE:
        logger.write("Optimal integer solution found: ", best_node.sol)
        return ret, best_node.opt, best_node.sol
    else: 
        logger.write("The problem is unlimited" if ret is SimplexSolution.UNLIMITED else "The problem is unsatisfiable")
        return ret, None, None
