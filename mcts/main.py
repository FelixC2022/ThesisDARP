from preprocess import *
from feasability import *
from utils import *
from mcts import *
from repair import *
from local_search import * 


import pandas as pd
import numpy as np
import copy 
from tqdm import tqdm
import time

import matplotlib.pyplot as plt


#EXECUTION ALGORITHM 
def main(sim_num, truncate=n, iters=100):

    start = time.time()

    succ = np.full(2*n, 999, dtype=int)
    pre = np.full(2*n, 999, dtype=int)
    RI = []
    root = np.array([succ, pre, RI], dtype=object)
    current_node = MonteCarloTreeSearchNode(root)

    for i in range(n):
        current_node=current_node.best_action(sim_num, truncate)

    solution = current_node.state

    solution = repair_sol(solution)


    costs = np.zeros(iters)
    for i in range(iters):
        solution = repair_sol(solution)
        solution = relocate(solution)
        solution = route_exchange(solution)
        solution = zero_split(solution)
        solution = repair_sol(solution)
        costs[i] = length_solution(solution)
        if i > 10 and costs[i-10] - costs[i] < 1.5: 
            break 

    cost = length_solution(solution)

    time_elapsed = time.time()-start

    if is_game_over(solution):
        return cost, time_elapsed

    else: 
        return np.nan, time_elapsed


if __name__ == '__main__':

    results = []

    for i in tqdm(np.arange(10, 100, step=3)):#tqdm(np.arange(50,1050, step=50, dtype=int)):

        cost = np.inf
        time_elap = np.inf 

        for _ in range(1):
            cost_i, time_elap_i = main(i, truncate=n, iters=0)
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






# if __name__ == '__main__':

#     results = []

#     for i in tqdm(range(5)):#tqdm(np.arange(50,1050, step=50, dtype=int)):
#         cost, time_elap = main(sim_num=250, iters=100)
#         cost = float(cost)
#         time_elap = float(time_elap)
#         print(cost, time_elap)
#         results.append([i, cost, time_elap])

#     results = pd.DataFrame((results), columns=['sim_num', 'cost', 'time'])
#     print(results)

#     fig, axs = plt.subplots(2, 1)

#     axs[0].plot(results.sim_num, results.cost)
#     axs[1].plot(results.sim_num, results.time, c="orange")


#     axs[0].set_xlabel('sim_num')    
#     axs[1].set_xlabel('sim_num')    

#     axs[0].set_ylabel('cost')
#     axs[1].set_ylabel('time')

#     plt.show()

