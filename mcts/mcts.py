from preprocess import *
from feasability import *
from utils import *

import pandas as pd
import numpy as np
from tqdm import tqdm
import copy 

#np.random.seed(123) #same random results (reproducable only for development)

#CLASS FOR NODES
class MonteCarloTreeSearchNode():
    def __init__(self, state, parent=None, parent_action=None):
        self.state= state 
        self.parent = parent 
        self.parent_action = parent_action 
        self.children = [] 
        self._number_of_visits = 0 
        self._results = 0 
        # self._untried_actions = None 
        self._untried_actions = get_legal_actions(state)
        
    def best_action(self, sim_num, truncate):
        #sim_num a hyperparameter 
        for i in range(sim_num):
            v = self._tree_policy() 
            reward = v.rollout(truncate)
            v.backpropagate(reward)
        
        return self.best_child(c_param=0.) 

    def _tree_policy(self):
        #Selects node to run rollout.
        current_node = self

        while not is_game_over(current_node.state): #current_node.is_terminal_node():
        
            if not current_node.is_fully_expanded():
                return current_node.expand()

            else:
                current_node = current_node.best_child()

        return current_node

    def is_fully_expanded(self):
        return len(self._untried_actions) == 0

    def expand(self):
        action = self._untried_actions.pop() #deletes the selected item 

        next_state = move(self.state, action) # next_state = move_allroutes(self.state, action)

        child_node = MonteCarloTreeSearchNode(next_state, parent=self, parent_action=action)

        self.children.append(child_node)

        return child_node 

    def best_child(self, c_param=np.sqrt(2)):
        #c_param is a hyperparameter to tune, sqrt(2) is a good value to start with according to the literature 
        choices_weights = [(c._results)/(c._number_of_visits) + (c_param * np.sqrt((np.log(self._number_of_visits))/c._number_of_visits)) for c in self.children]
        return self.children[np.argmax(choices_weights)]

    def rollout(self, truncate): #turncate = n by default full rollouts 
        
        current_rollout_state=self.state

        for i in range(truncate):

            if is_game_over(current_rollout_state):
                break
            
            else: 

                possible_moves = get_legal_actions(current_rollout_state)
            
                action = self.rollout_policy(possible_moves)

                possible_moves.remove(action)

                current_rollout_state = move(current_rollout_state, action)
 

        return game_result(current_rollout_state)
      
    def rollout_policy(self, possible_moves):
    
        return possible_moves[np.random.randint(len(possible_moves))]
        #Randomly selects a move out of possible moves. This is an example of random playout.

    def backpropagate(self, result):
        self._number_of_visits += 1
        self._results += result
        if self.parent:
            self.parent.backpropagate(result)


                                               









