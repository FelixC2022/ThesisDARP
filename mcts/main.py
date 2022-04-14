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


#EXECUTION ALGORITHM 
def main(sim_num, truncate=n):
    succ = np.full(2*n, 999, dtype=int)
    pre = np.full(2*n, 999, dtype=int)
    RI = []
    root = np.array([succ, pre, RI], dtype=object)
    current_node = MonteCarloTreeSearchNode(root)

    for i in tqdm(range(n)):
        current_node=current_node.best_action(sim_num, truncate)

    return current_node


if __name__ == '__main__':

    start = time.time()


    mcts = main(sim_num=500, truncate=int(n/3))

    solution = mcts.state

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


    cost = length_solution(solution)

    print('\n')
    print(cost)
    print(is_game_over(solution))
    for i in range(len(solution[2])):
        print(gen_route(solution, i))


    print(f'it took {time.time()-start} seconds')

