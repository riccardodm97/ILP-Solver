from lib.domain import DomainProblem
from lib.simplex import simplex_algorithm

# A1 = [
#     [1,  1,  1, -1,  0,  0],
#     [2,  0, -1,  1,  1,  0],
#     [3,  0,  1,  2,  0,  1]
# ]

# c1 = [2, -3, 1, -4, 1, 0]

# b1 = [4,2,1]

# ret = simplex_algorithm(c1, A1, b1)
# print(ret)


# A2 = [
#     [1, -1, 3, 2],
#     [2, 1, -3, 3],
#     [3, 0, 0, 5]
# ]

# c2 = [-1, 1, -2, 3]

# b2 = [4,6,10]

# ret = simplex_algorithm(c2, A2, b2)
# print(ret)

A3 = [
    [2, 4, 1, 0, 0],
    [1, 0, 0, 1, 0],
    [0, 2, 0, 0, 1]
]

c3 = [-3, -5, 0, 0, 0]

b3 = [25, 8, 10]

# ret = simplex_algorithm(c3, A3, b3)
# print(ret)

dp = DomainProblem.from_abc(A3,b3,c3,non_negatives=[0,1,2,3,4],is_integer=True)
dp.solve()