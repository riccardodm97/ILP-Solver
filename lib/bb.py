from lib import logger
import math
from collections import deque
import numpy as np
from typing import Tuple

from lib.utils import SimplexSolution, DomainOptimizationType
from lib.simplex import simplex_algorithm

from sortedcontainers import SortedList

class BBNode:
    def __init__(self, std_problem, variables, coefficients, val, slack_coeff, var_chg_map, node_name, opt_type: DomainOptimizationType):
        self.std_problem = std_problem.copy()
        self.var_chg_map = var_chg_map
        self.node_name = node_name
        self.opt_type = opt_type
        self.child_left, self.child_right = None, None
        self.sol = None
        self.opt = None
        self.ret_type = None

        if variables is not None:
            rows, cols = self.std_problem.shape
            new_row = np.zeros(cols+1)
            new_row[variables] = coefficients
            new_row[-1] = val
            new_row[-2] = slack_coeff

            self.std_problem = np.c_[self.std_problem[:,:-1], np.zeros(rows), self.std_problem[:,-1]]
            self.std_problem = np.r_[self.std_problem, [new_row]]

    def solve(self):
        ret, std_opt, std_sol = simplex_algorithm(self.std_problem[0,:-1], self.std_problem[1:,:-1], self.std_problem[1:,-1])
        logger.write("The problem is "+ret.name)
        
        if ret is SimplexSolution.FINITE:
            self.sol = np.array([sum([factor['coeff'] * std_sol[factor['var']] for factor in factors]) for factors in self.var_chg_map.values()])
            self.opt = std_opt if self.opt_type is DomainOptimizationType.MIN else -1 * std_opt
            logger.write("The variables values are", self.sol, "with optimum value", self.opt,"\n")

        else :
            self.opt = np.inf if self.opt_type is DomainOptimizationType.MIN else np.NINF
        
        self.ret_type = ret

    def is_int(self):
        return np.all(np.mod(self.sol, 1) == 0)
    
    def __lt__(self, other):
        if self.opt_type is DomainOptimizationType.MAX:
            return self.opt > other.opt      
        else :
            return self.opt < other.opt       
    
    def __repr__(self):
        return str(self)+"("+str(self.opt)+")"                
    
    def __str__(self):
        return 'P'+str(self.node_name)                                 


class BBTree:
    def __init__(self, std_problem, var_chg_map, optimization_type):
        self.std_problem = std_problem
        self.var_chg_map = var_chg_map
        self.optimization_type = optimization_type

        self.generated_nodes = 0
        self.root = BBNode(self.std_problem, None, None, None, None, self.var_chg_map,self.generated_nodes,self.optimization_type)
        self.best_node = None

        self.working_memory = deque([self.root])

    def solve(self) -> Tuple[SimplexSolution,BBNode] :
        logger.write("Solving root node "+str(self.root))
        self.root.solve()

        while self.working_memory:

            logger.write("\nCurrent nodes stack: ",str(self.working_memory))

            node = self.select_next()
            logger.write("Considering node "+str(node))
            
            if node.ret_type is SimplexSolution.UNLIMITED:
                return node.ret_type, None

            if node.ret_type is SimplexSolution.IMPOSSIBLE:
                logger.write("The problem associated with node "+str(node)+" is impossible - Pruning by infeasibility")
            elif self.is_worse(node): 
                logger.write("The solution associated with node "+str(node)+" is worse than the current best one - Pruning by bound")
            else:
                if node.is_int():
                    logger.write("The solution associated with node "+str(node)+" is integer (",node.sol,") - Pruning by integrality")
                    if self.best_node == None :
                        assert isinstance(self.working_memory,deque), 'working memory should have been a deque til this point'
                        self.working_memory = SortedList(self.working_memory)
                    self.best_node = node # Pruned by integrality
                else:
                    logger.write("The solution associated with node "+str(node)+" is not integer - Branching the tree")
                    self.branch(node) # Branch

        return SimplexSolution.FINITE if self.best_node is not None else SimplexSolution.IMPOSSIBLE, self.best_node

    def is_worse(self, node : BBNode) -> bool:
        if self.best_node is None:
            return False
        return node.opt <= self.best_node.opt if self.optimization_type is DomainOptimizationType.MAX else node.opt >= self.best_node.opt 

    def branch(self, node : BBNode):
        idx=np.argmax(node.sol-np.trunc(node.sol))
        val = node.sol[idx]

        variables = [d['var'] for d in self.var_chg_map[idx]]
        coefficients = [d['coeff'] for d in self.var_chg_map[idx]]

        logger.write("Branch on variable X"+str(idx))
        logger.write("Adding new costraints : X"+str(idx)+" <= "+str(math.floor(val))+" for left node and X"+str(idx)+" >= "+str(math.ceil(val))+" for right node\n")
        node.child_left = BBNode(node.std_problem, variables, coefficients, math.floor(val), 1, self.var_chg_map,self.incr_generated_nodes(),self.optimization_type)
        node.child_right = BBNode(node.std_problem, variables, coefficients, math.ceil(val), -1, self.var_chg_map,self.incr_generated_nodes(),self.optimization_type)
        
        #solve it already 
        logger.write("Solving left node "+str(node.child_left))
        node.child_left.solve()
        logger.write("Solving right node "+str(node.child_right))
        node.child_right.solve()

        self.add_childs_to_memory(node.child_left, node.child_right)
    
    def select_next(self) -> BBNode :
        if isinstance(self.working_memory,deque): 
            node = self.working_memory.popleft()
        else :
            node = self.working_memory.pop(0)
        return node 

    def add_childs_to_memory(self, ch_left : BBNode, ch_right : BBNode ) :
        if self.best_node is None :
            self.working_memory.appendleft(ch_right)
            self.working_memory.appendleft(ch_left)
        else :
            self.working_memory.add(ch_right)
            self.working_memory.add(ch_left)
        
    def incr_generated_nodes(self) -> int:
        self.generated_nodes+=1
        return self.generated_nodes


def bb_algorithm(std_problem, var_chg_map, optimization_type):
    logger.write("\nStarting Branch and Bound algorithm\n")
    tree = BBTree(std_problem, var_chg_map, optimization_type)
    ret, best_node = tree.solve()

    if ret is SimplexSolution.FINITE:
        return ret, best_node.opt, best_node.sol
    else: 
        return ret, None, None
