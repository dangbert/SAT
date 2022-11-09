import numpy as np

def encode_puzzle(sudoku):
    '''Encodes puzzle in DIMACS format.'''

    # determine number of variables
    vars = int(np.sqrt(len(sudoku)))

    clauses = []
    for i, s in enumerate(sudoku):
        if not s == 0:
            y, x, n = i//vars + 1, (i+1) % vars, s
            if x == 0:
                x = vars
            clauses.append([y, x, n])

    # print header of DIMACS rep
    print(f'p cnf {vars} {len(clauses)}')

    # print clauses
    for clause in clauses:
        print(''.join([str(c) for c in clause]) + ' 0')

example = [0,0,0,3,0,0,4,1,1,4,0,0,3,0,0,0]
encode_puzzle(example)

# still to do:
# read examples from dataset with dot format into 0 format (as displayed in example)
# maybe: add disjunctions of all possibilities? or maybe not necessary since rules imply the same?
