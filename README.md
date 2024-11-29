## Introduction:
Game of life has a subproblem called "still-life problem" which is fulfilled if and only if the board state at time $t$ is identical to the board state at $t+1$. If, additionally to that, amount of living cell is maximized, `Maximum density still life` problem is alive.

## Denotion:
We are essentially only encoding the rules and SAT solver should return some certain amount of solutions that satisfy this rule, for instance empty board is qualified candidate. We are interested only in the specific one which has the number of ones maximized. The second part has nothing really to do with SAT solver whatsoever, but the formula encoding does, here is a brief explanation;


### We have 3 rules
1. if a cell has exactly three living neighbours at time $t$, it is alive at time $t+1$
2. if a cell has exactly two living neighbours at time $t$ it is in the same state at time $t+1$ as it was at time $t$
3. otherwise, the cell is dead at time $t+1$

Could be denoted as for some cell at $C_{i,j}$ position we are trying out every combination of its dead and alive neighbors as follows (for simplicity lets assume neighbors are labeled $a..h$ and $-a$ means first neighbor is dead (dimacs syntax)), for 3 alive neighbors these are vaible combinations we ought to denote, alltogether there are 56 = C(8,3) options: $\\$
a b c -d -e -f -g -h $\\$
-a -b -c d e -f -g h $\\$
etc... $\\$

Likewise for dead cells. Here is the code snippet, it is rewritten to CNF as $a \implies b$ is the same as $-a ∨ b$:
```py
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
```

The rest of the code is pretty straighforward, refer to the comments and explanations provided in `sat.py` file.


## Optimization:
There is a lemma that holds true (please refer to [this](https://www.sciencedirect.com/science/article/pii/S0004370212000124) academic paper for a proof), which states that maximum density of live cells in the infinite case $n = ∞$ converges to $1/2$.

In the very same academic paper I am refering to, are furthermore optimizationm such as the problem can be rephrased as finding minimial wastage as it occurs mainly in the corners and around the boder limits due to lack of neighbors located nearby - some certain behaviour is extorted.

Additionally, luckily, there is a reoccuring pattern that starts to rule at around n=200
and the computational workolod gets signigicantly reduced as DP (Dynammic Programming) gets hands on board. Remodeling this whole problem to not being exponentional in time complexity and rather having closed form.

SAT solver isnt an optimal tool rather than quick efficient enough as people dont have time to spend enormous time and effort optimizing and researching.

Regarding the clause encoding - there is no other better way to do it as rules are straighforward.

## Inputs

- Technically every board has solution something within $O(n^2)$ using DP. Sticking to SAT only then think of $n=200$ and how big number $O(2^{{200}^{2}})$ is. $\\$
- Something that can be analyzed trivially is 2x2 as it is a board full of ones, refer to [this](https://www.csplib.org/Problems/prob032/) webpage for two more examples .


## Last words
This project has some certain flaw that I wasnt able to find even after 40hours of debugging and refactoring, 2meetings with lectors and studying on the internet. $\\$
Logic (or the sketch of it) is obviously good - there is clearly some mistake I am not aware of and as this is isnt a semestral project I had to move on to pursue study in different lectures aswell. I am not proud that I didnt finish this problem, but I dont have enough time to ponder around.
$\\$

It was nice to get hands on such problem, it is time exhausting as I am not so skilled. I am probably going to pursue this field of study.