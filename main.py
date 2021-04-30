from lib.simplex import simplex_algorithm

A = [
    [1, -1, 3, 2],
    [2, 1, -3, 3],
    [3, 0, 0, 5]
]

c = [-1, 1, -2, 3]

b = [4,6,10]

simplex_algorithm(c, A, b)
