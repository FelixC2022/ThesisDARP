from load_instance import *
from feasability import *
from route_gen import *
from repair_routes import *
from local_search import *

import numpy as np 
import time
import pandas as pd
from tqdm import tqdm

import matplotlib.pyplot as plt
import pandas as pd


def main(iterations, iters_ls,  N, num_elite, alpha):

    start_time = time.time()

    #Initialization 
    best_score = np.inf

    costs_main = np.zeros(iterations)

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


    for i in range(iterations):
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


        #Stops the Ce loop if the solution doesn't improve after 10 iterations 
        # costs_main[i] = best_score
        # if i > 10 and costs_main[i] - costs_main[i-10] < 1.5:
        #     break


        #Update the Pij matrix
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
    costs = np.zeros(iters_ls)
    for j in range(iters_ls):
        solution = repair_sol(solution)
        solution = relocate(solution)
        solution = route_exchange(solution)
        solution = zero_split(solution)
        costs[j] = length_solution(solution)
        if j > 10 and costs[j] - costs[j-10] < 1.5: 
            break 

    if len(solution[2]) > K: #too many routes in final solution
        final_cost = np.inf 

    else: 
        final_cost = length_solution(solution)

    time_elapsed = time.time() - start_time

    return final_cost, time_elapsed


if __name__ == '__main__':

    results = []

    for i in tqdm(np.arange(1, 500, step=20)):#tqdm(np.arange(50,1050, step=50, dtype=int)):
        # cost, time_elap = main(i, 100, 10, 5, 0.5)

        cost = np.inf
        time_elap = np.inf 

        for _ in range(3):
            cost_i, time_elap_i = main(iterations=i, iters_ls=100, N=50, num_elite=15, alpha=0.3)
            if cost_i < cost:
                cost = cost_i
                time_elap = time_elap_i

        results.append([i, cost, time_elap])

    results = pd.DataFrame((results), columns=['sim_num', 'cost', 'time'])

    print(results)



    fig, axs = plt.subplots(2, 1)

    axs[0].scatter(results.sim_num, results.cost)
    axs[1].scatter(results.sim_num, results.time, c="orange")


    axs[0].set_xlabel('sim_num')    
    axs[1].set_xlabel('sim_num')    

    axs[0].set_ylabel('cost')
    axs[1].set_ylabel('time')

    plt.show()

