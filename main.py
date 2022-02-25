import pandas as pd
import copy 
import numpy as np
from tqdm import tqdm

from utils import initialize_state, length_total, is_game_over, display_routes, num_vehs, num_reqs, route_duration, Q, x_co, y_co, s, L, q, e, l, R
from mcts import MonteCarloTreeSearchNode


#EXECUTION ALGORITHM 
def main(sim_num):
    state_root = initialize_state()
    node_root = MonteCarloTreeSearchNode(state_root)

    current_node = node_root
    for i in tqdm(range(num_reqs)):
        current_node=current_node.best_action(sim_num)

    final_node = current_node

    return final_node


if __name__ == '__main__':

    final_node = main(sim_num=1)

    cost_solution= length_total(final_node.state)

    print([final_node.state[0], final_node.state[1], final_node.state[2]]) #
    print('\n')
    print(cost_solution)
    print('\n')
    print(is_game_over(final_node.state))
    print('\n')
    print(display_routes(final_node.state))
    #print(length_total(selected_node.state)  
