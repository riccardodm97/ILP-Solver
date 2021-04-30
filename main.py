from lib.temp import simplex_algorithm

A = [
    [1, -1, 3, 2],
    [2, 1, -3, 3],
]

c = [-1, 1, -1, 3]

b = [4,6]

simplex_algorithm(c, A, b)
