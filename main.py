from lib.simplex import SimplexProblem

A = [
    [1, 1, 1, -1, 0, 0],
    [2, 0, -1, 1, 1, 0],
    [3, 0, 1, 2, 0, 1]
]

c = [2, -3, 1, -4, 1, 0]

b = [4, 2, 1]

problem = SimplexProblem(c, A, b)
solution = problem.start_simplex()
print(solution)