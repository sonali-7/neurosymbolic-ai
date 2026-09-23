from z3 import Int, Solver, Distinct, sat

def solve_sudoku(grid):
    s = Solver()

    X = [[Int(f"x_{r}_{c}") for c in range(9)] for r in range(9)]

    for i in range(9):
        for j in range(9):
            s.add(X[i][j] >= 1, X[i][j] <= 9)

    for i in range(9):
        s.add(Distinct(X[i]))
        s.add(Distinct([X[r][i] for r in range(9)]))

    for i in range(3):
        for j in range(3):
            s.add(Distinct([X[r][c] for r in range(i*3, i*3 + 3) for c in range(j*3, j*3 + 3)]))

    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                s.add(X[i][j] == grid[i][j])

    if s.check() == sat:
        m = s.model()
        for i in range(9):
            for j in range(9):
                X[i][j] = m[X[i][j]].as_long()
        return X
    return None

puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

solved = solve_sudoku(puzzle)

if solved:
    for row in solved:
        print(row)
else:
    print("Unsolvable!")