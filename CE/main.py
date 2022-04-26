from load_instance import *
from feasability import *
from route_gen import *
from repair_routes import *
from local_search import *

import numpy as np 
import time
from tqdm import tqdm


if __name__ == '__main__':


    for i in range(4):
        start_time = time.time()

        #Initialization 
        best_score = np.inf
        N = 10 #num of solutions to generate
        num_elite = 3 #num of elite solutions to select 

        #Generate P start 
        P = np.full((n+2, n+2), 1)
        P[0,-1] = 0 #from depot to depot 
        for i in range(len(P)): 
            P[i,i] = 0 #to itself 
            P[i, -1] = 0 #from a pickup to end_depot 
            P[-1, i] = 0 #from end_depot to a pickup 

        total = 0 
        for row in P: 
            total += sum(row)
        P = P/total  #normalize


        for i in tqdm((range(50))):
            # Generate N solutions & select the K best solutions 
            solutions_all = gen_N_solutions_multiprocess(N, P)
            # solutions_all = repair_N_solutions_multiprocess(solutions_all) #PLACE AFTER THE SELECTION OF THE ELITES 
            solutions_all = list(solutions_all)

            scores = [length_solution(sol) for sol in solutions_all]

            idx_elite = np.argpartition(scores, num_elite)
            solutions_elite = [solutions_all[i] for i in idx_elite[:num_elite]]   

            #Perform Local Search on the x best solution 
            solutions_elite = repair_N_solutions_multiprocess(solutions_elite)
            # solutions_elite = relocate_N_multiprocess(solutions_elite)
            # solutions_elite = zero_split_N_multiprocess(solutions_elite)
            # solutions_elite = route_exchange_N_multiprocess(solutions_elite)
            solutions_elite = list(solutions_elite)

            #Take the shortest sol and save if better than current best 
            for sol in solutions_elite: 
                score = length_solution(sol)
                if score < best_score: 
                    best_score = score
                    best_solution = sol

            #Update the Pij matrix
            alpha = 0.3 #between 0.4 and 0.9
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


        solution = best_solution
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
        
        print("--- %s seconds ---" % (time.time() - start_time))