from preprocess import *
from feasability import *
from utils import *
from mcts import *
from repair import *


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


    mcts = main(sim_num=1000)

    solution = mcts.state
    solution = repair_sol(solution)
    cost = length_solution(solution)

    print(cost)
    print('\n')
    print(is_game_over(solution))
    print('\n')
    print(len(solution[2]))
    for i in range(len(solution[2])):
        print(gen_route(solution, i))


    print(f'it took {time.time()-start} seconds')