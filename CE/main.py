from route_gen import *
from feasability import *
from repair_routes import *

import numpy as np 
import time
from tqdm import tqdm

start_time = time.time()

#Initialization
best = np.inf
N = 10 #num of solutions to generate
K = 3 #num of elite solutions to select 

P = np.full((n+2, n+2), 1/((n+2)*(n+2))) #uniform initialization of P 

for i in tqdm(range(15)):
    # Generate N solutions & select the K best solutions 
    
    solutions_all = gen_N_solutions(N, P)

    solutions_all = [repair_sol(sol) for sol in solutions_all]

    scores = np.zeros(len(solutions_all))
    for i in range(len(solutions_all)): 
        scores[i] = length_solution(solutions_all[i])
    
    best_score = min(scores)
    idx = np.argmin(scores)
    best_solution = solutions_all[idx]

    indices_selected = np.argpartition(scores, K)
    solutions_elite = []
    for i in indices_selected[:K]:
        solutions_elite.append(solutions_all[i])

    solutions_elite = np.array(solutions_elite, dtype=object) #necessary? 
    # routes_elite = np.concatenate(solutions_elite)


    #Perform Local Search on the x best solution 

    #Update the Pij matrix 
    alpha = 0.4 #between 0.4 and 0.9
    P_new = np.zeros((n+2, n+2))
    total_routes = 0

    for solution in solutions_elite:
        for route in solution:
            total_routes += 1
            masked_route = np.append(route[route <= n], 2*n+1)
            for i in range(len(masked_route)-1):
                if masked_route[i+1] == 2*n+1:
                    P_new[masked_route[i],n+1] += 1
                else: 
                    P_new[masked_route[i], masked_route[i+1]] += 1

    P_new[0] = P[0]/total_routes
    P_new[1:] = P[1:]/len(solutions_elite)

    P = alpha*P + (1-alpha)*P_new #smoothing of pij updates 

print(best_score)
print(best_solution)

print("--- %s seconds ---" % (time.time() - start_time))

