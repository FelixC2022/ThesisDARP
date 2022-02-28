import copy 
import numpy as np
from tqdm import tqdm
import pandas as pd
np.random.seed(123) #same random results (reproducable only for development)

from utils import get_legal_actions, is_game_over, game_result
from move import move, move_allroutes


#CLASS FOR NODES
class MonteCarloTreeSearchNode():
    def __init__(self, state, parent=None, parent_action=None):
        self.state= state 
        self.parent = parent 
        self.parent_action = parent_action 
        self.children = [] 
        self._number_of_visits = 0 
        self._results = 0 #make it the sum of scores according to eval. fct 8 step eval. scheme!; (Score of a node=results/number_of_visits)
            
        self._untried_actions = None 
        self._untried_actions = self.untried_actions()
        return

    def untried_actions(self):
        #OLD WITHOUT RESHUFFLE 
        # self._untried_actions = get_legal_actions(self.state) 
        # return self._untried_actions

        actions = get_legal_actions(self.state) 
        np.random.shuffle(actions) #Reshuffle otherwise customers represented by higher integers are expanded more often 
        return actions
    
    def best_action(self, sim_num):
        #sim_num a hyperparameter 
        for i in range(sim_num):
            v = self._tree_policy() 
            reward = v.rollout()
            v.backpropagate(reward)
        return self.best_child(c_param=0.) 

    def _tree_policy(self):
        #Selects node to run rollout.
        current_node = self
        while not current_node.is_terminal_node():
        
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node

    def is_terminal_node(self):
        return is_game_over(self.state)

    def is_fully_expanded(self):
        return len(self._untried_actions) == 0

    def expand(self):
        action = self._untried_actions.pop()

        next_state = move_allroutes(self.state, action)

        child_node = MonteCarloTreeSearchNode(next_state, parent=self, parent_action=action)

        self.children.append(child_node)
        return child_node 

    def best_child(self, c_param=np.sqrt(2)):
        #c_param is a hyperparameter to tune, sqrt(2) is a good value to start with according to the literature 
        choices_weights = [(c._results)/(c._number_of_visits) + (c_param * np.sqrt((np.log(self._number_of_visits))/c._number_of_visits)) for c in self.children]
        return self.children[np.argmax(choices_weights)]

    def rollout(self):
        
        valid_check = True 

        current_rollout_state=self.state
    
        while not is_game_over(current_rollout_state):
        
            possible_moves = get_legal_actions(current_rollout_state)
        
            action = self.rollout_policy(possible_moves)

            possible_moves.remove(action)

            intermediary_state = move(state=current_rollout_state, a=action)
    
            while intermediary_state == None: 
                if len(possible_moves)==0:
                    valid_check = False
                    break
                action = self.rollout_policy(possible_moves)
                possible_moves.remove(action)
                intermediary_state = move(current_rollout_state, action)

            current_rollout_state = intermediary_state

            if valid_check == False: 
                break #removed actions in the code above will not be included in a final solution of the rollout

        #if rollout is totally blocked and no possible insertion is found 
        if current_rollout_state == None:
            return 0     
    
        return game_result(current_rollout_state)
    
    def rollout_policy(self, possible_moves):
    
        return possible_moves[np.random.randint(len(possible_moves))]
        #Randomly selects a move out of possible moves. This is an example of random playout.

    def backpropagate(self, result):
        self._number_of_visits += 1
        self._results += result
        if self.parent:
            self.parent.backpropagate(result)


                                               









