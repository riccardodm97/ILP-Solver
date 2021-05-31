from enum import Enum

class Parameters:
    DECIMAL_PRECISION = 13
    

class SimplexSolution(Enum):
    FINITE = 1
    UNLIMITED = 2
    IMPOSSIBLE = 3
    #TODO: MAX_ITERATIONS_REACHED = 4 ?

class DomainConstraintType(Enum):
    LESS_EQUAL = 1
    GREAT_EQUAL = 2
    EQUAL = 3

class DomainOptimizationType(Enum):
    MAX = 1
    MIN = 2
