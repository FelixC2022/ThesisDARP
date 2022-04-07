from route_gen import *
from feasability import *
from repair_routes import *

import numpy as np 
import time
from tqdm import tqdm

if __name__ == '__main__':

    start_time = time.time()

    #Initialization
    best_score = np.inf
    N = 20 #num of solutions to generate
    num_elite = 5 #num of elite solutions to select 

    P = np.full((n+2, n+2), 1/((n+2)*(n+2))) #uniform initialization of P, CORRECT TO DO infeasible transitions should be 0 

    for i in tqdm(range(25)):
        # Generate N solutions & select the K best solutions 
        
        #Sequential 
        # solutions_all = gen_N_solutions(N, P)
        # solutions_all = repair_N_solutions(solutions_all)

        #Parallel 
        solutions_all = gen_N_solutions_multiprocess(N, P)
        solutions_all = repair_N_solutions_multiprocess(solutions_all)
        solutions_all = list(solutions_all)

        scores = np.zeros(N)
        for j in range(len(solutions_all)): 
            sol = solutions_all[j]
            score = length_solution(sol)
            scores[j] = score
            
            #Keep track of best found solution thus far 
            if score < best_score: 
                best_score = score
                best_solution = sol

            #Keep track of the K most elite solutions 
            solutions_elite = []
            solutions_elite_scores = np.full(num_elite, np.inf)
            if len(solutions_elite) <= num_elite: 
                solutions_elite.append(sol)
                solutions_elite_scores[len(solutions_elite)-1] = score
            else:
                if score < min(solutions_elite_scores): 
                    idx = np.argmin(solutions_elite_scores)
                    solutions_elite_scores[idx] = score
                    solutions_elite[idx] = sol 

        # indices_selected = np.argpartition(scores, K)
        # solutions_elite = []
        # for i in indices_selected[:K]:
        #     solutions_elite.append(solutions_all[i])

        solutions_elite = np.array(solutions_elite, dtype=object) #necessary? 

        #Perform Local Search on the x best solution 

        #Update the Pij matrix
        alpha = 0.4 #between 0.4 and 0.9
        P_new = np.zeros((n+2, n+2))
        total_routes = 0

        for sol in solutions_elite:
            for i in range(len(sol[2])):
                total_routes += 1
                route = gen_route(sol, i)
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