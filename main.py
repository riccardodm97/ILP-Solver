from lib.temp import simplex_algorithm

A = [
    [1, 1, 1, -1, 0, 0],
    [2, 0, -1, 1, 1, 0],
    [3, 0, 1, 2, 0, 1]
]

c = [2, -3, 1, -4, 1, 0]

b = [4, 2, 1]

simplex_algorithm(c, A, b)
