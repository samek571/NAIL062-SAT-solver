import itertools
import subprocess
import sys
import os


'''giving each cell a unique variable on board in time t (=base)'''
def cell_var(base, i, j, n):
    return base + i * n + j + 1

def encode_game_of_life(n):
    clauses = []
    tmp = []
    for i in range(n):
        for j in range(n):
            cell = cell_var(0, i, j, n)
            tmp.append(cell)
            # 8 neighbors
            neighbors = []
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0: continue

                    ni, nj = i + di, j + dj
                    if 0 <= ni < n and 0 <= nj < n:
                        neighbors.append(cell_var(0, ni, nj, n))


            '''game of life rules are quite straight forawrd:
                - if a cell has exactly three living neighbours at time t, it is alive at time t+1
                - if a cell has exactly two living neighbours at time t it is in the same state at time t+1 as it was at time t
                - otherwise, the cell is dead at time t+1
                '''
            for k in range(3, 3+1):  # Exactly 3 neighbors become alive
                for live_neighbors in itertools.combinations(neighbors, k):
                    clause = [cell]
                    clause += [n for n in neighbors if n not in live_neighbors] #dead neighbors
                    clause += [-n for n in live_neighbors] #alive neighbors
                    clauses.append(clause)

            for k in range(0, len(neighbors) + 1): #if it isnt 2 nor 3 neigbors the cell dies
                if k not in {2, 3}:
                    for live_neighbors in itertools.combinations(neighbors, k):
                        clause = [-cell]
                        clause += [n for n in neighbors if n not in live_neighbors] #dead neighbors
                        clause += [-n for n in live_neighbors] #alive neigbors
                        clauses.append(clause)
    #testing
    # clauses = []
    clauses.append(tmp)
    # print(tmp)

    return clauses


'''encoding the clauses into a DIMACS format'''
def write_dimacs(clauses, cnf_filename):
    with open(cnf_filename, 'w') as f:
        num_vars = max([abs(lit) for clause in clauses for lit in clause])
        f.write(f"p cnf {num_vars} {len(clauses)}\n")
        for clause in clauses:
            f.write(' '.join(map(str, clause)) + ' 0\n')


'''convert given SAT output back to board '''
def sat_to_board(sat_output, n, base):
    board = [[0 for _ in range(n)] for _ in range(n)]

    for line in sat_output.strip().split('\n'):
        if line.startswith('v'):
            variables = line.strip().split()[1:]  # parsing purposes only
            for var in variables:
                v = int(var)
                if v > 0:
                    v_index = v - base - 1
                    i = v_index // n
                    j = v_index % n
                    if 0 <= i < n and 0 <= j < n:
                        board[i][j] = 1
    return board


'''Call Glucose SAT solver on the given CNF file.'''
def call_glucose(cnf_filename):
    try:
        result = subprocess.run(
            ['glucose', '-model', cnf_filename],
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            capture_output=True,
            text=True
        )
        return result.stdout

    except FileNotFoundError:
        print("error: SAT-solver is not installed or bad PATH config")
        sys.exit(1)


"""blocking clause generator - so we can iterate via other options easily"""
def blocking_clause_gen(sat_output):
    blocking_clause = []
    for line in sat_output.splitlines():
        if line.startswith('v'):
            for var in map(int, line.split()[1:]):
                blocking_clause.append(-var if var > 0 else var)
            break
    return blocking_clause #this weird syntax so the function strictly returns something


"""finds all solutions by iteration"""
def find_all_solutions(n, cnf_filename):
    clauses = encode_game_of_life(n)
    write_dimacs(clauses, cnf_filename)

    all_solutions = []
    seen_solutions = set()
    while True:
        sat_output = call_glucose(cnf_filename)
        if "UNSAT" in sat_output: break

        sol = sat_to_board(sat_output, n, base=0)
        solution_tuple = tuple(map(tuple, sol))

        if solution_tuple not in seen_solutions:
            all_solutions.append(sol)
            seen_solutions.add(solution_tuple)

            blocking_clause = blocking_clause_gen(sat_output)
            with open(cnf_filename, 'a') as f:
                f.write(' '.join(map(str, blocking_clause)) + ' 0\n')

    return all_solutions, sat_output


if __name__ == "__main__":
    n = 3
    cnf_filename = "game_of_life.cnf"
    solutions, _sat_info = find_all_solutions(n, cnf_filename)
    do_remove_cnf_file = False
    print_sat_info = True

    if print_sat_info: print(_sat_info)

    if solutions:
        max_ones_solution = None
        max_ones_count = 0

        '''optionally uncomment for greater details'''
        #print("\nAll solutions:")
        for idx, sol in enumerate(solutions):
            #print(f"Solution {idx + 1}:")
            #for row in sol:
            #    print(row)

            ones_count = sum(sum(row) for row in sol)
            if ones_count > max_ones_count:
                max_ones_count = ones_count
                max_ones_solution = sol

        print("\nMaximum density solution:")
        for row in max_ones_solution:
            print(row)

    if do_remove_cnf_file: os.remove(cnf_filename)