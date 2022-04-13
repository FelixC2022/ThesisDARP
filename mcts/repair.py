from preprocess import *
from feasability import *
from utils import *

import numpy as np 
import concurrent.futures
import copy 



#@@@@@@@@@@@@@@@@@@ HELPER #@@@@@@@@@@@@@@@@@@
def get_insertions_all(solution, route_idx):  
    #The insertion index indicates the index before which the new user will be inserted referring to the orginal tour 
    combis = []
    RI = solution[2]
    num_routes = len(RI)

    if (num_routes-1) < route_idx:
        combis.append([999,999])

    else: 
        route = gen_route(solution, route_idx)

        for i in range(len(route[:-1])):
            for j in range(i, len(route[:-1])):
                combis.append([route[i],route[j]])
        
    return combis

#@@@@@@@@@@@@@@@@@@ PREPROCESS #@@@@@@@@@@@@@@@@@@
def preprocess_repair(sol):
    succ = copy.deepcopy(sol[0])
    pre = copy.deepcopy(sol[1])
    RI = copy.deepcopy(sol[2])

    route_len = np.zeros(K, dtype=int)
    route_idx = np.zeros(K, dtype=int)

    for i in range(len(RI)):
        if RI[i][2] > min(route_len):
            idx = np.argmin(route_len)
            route_len[idx] = RI[i][2]
            route_idx[idx] = i 

    again = []
    for i in range(len(RI)): 
        if i not in route_idx: 

            vertex = RI[i][0]
            while vertex != 2*n+1: 
                again.append(vertex)#assaign vertex to new route 
                vertex_old = vertex.copy()
                vertex = succ[vertex-1]
                succ[vertex_old-1] = 999

            vertex = RI[i][1]
            while vertex != 0: 
                vertex_old = vertex.copy()
                vertex = pre[vertex-1]
                pre[vertex_old-1] = 999

    
    again = np.array(again, dtype=int)
    again = again[again <= n] 
        
    RI = [RI[i] for i in route_idx]

    empty_sol = np.array([succ, pre, RI], dtype=object)

    return route_idx, again, empty_sol


#@@@@@@@@@@@@@@@@@@ FULL REPAIR #@@@@@@@@@@@@@@@@@@

def repair_sol(solution):
    routes_selected, again, sol = preprocess_repair(solution) #routes_selected is not used but needs to be assigned otherwihse error

    sol = copy.deepcopy(sol)

    for user in again: 
        insertion_found = False

        shortest = np.inf
        route_idx = 0 

        while not insertion_found: 

            combis = get_insertions_all(sol, route_idx)

            for i in combis: 
                new_sol = gen_new_solution(sol, user, i, route_idx)
                new_route = gen_route(new_sol, route_idx)
                check = eight_step(new_route)
                lenght = length_route(new_sol, route_idx)
                if check and lenght < shortest: 
                    insertion_found = True
                    shortest = lenght
                    current_best_sol = new_sol
                    break #as soon as insertion is found go to the next 
            
            if insertion_found:   
                sol = current_best_sol #if no insertion return the old sol 
                
            route_idx += 1

    return sol
