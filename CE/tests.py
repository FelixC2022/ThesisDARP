from route_gen import *
from feasability import *
from load_instance import * 
from local_search import * 
from repair_routes import * 

from tqdm import tqdm
import numpy as np 

P = np.full((n+2, n+2), 1)
P[0,-1] = 0 #from depot to depot 
for i in range(len(P)): 
    P[i,i] = 0 #to itself 
    P[i, -1] = 0 #from a pickup to end_depot 
    P[-1, i] = 0 #fr


for _ in range(5):
    solution = gen_solution(P)
    solution = repair_sol(solution)

    print(length_solution(solution))

    iters = 100
    costs = np.zeros(iters)
    for i in tqdm(range(iters)):
        solution = repair_sol(solution)
        solution = relocate(solution)
        solution = route_exchange(solution)
        solution = zero_split(solution)
        costs[i] = length_solution(solution)
        if i > 10 and costs[i-10] - costs[i] < 1.5: 
            break 

    print(length_solution(solution))