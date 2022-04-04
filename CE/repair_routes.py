from route_gen import *
from feasability import *

import numpy as np 
import time
from tqdm import tqdm


# print(len(sol), length_solution(sol))
def routes_users_again(sol):
    max_users = np.array([0,0], dtype=int)
    max_users_ind = np.array([0]*K, dtype=int)
    for i in range(len(sol)): 
        users = (len(sol[i])-2)/2
        if users > min(max_users):
            idx = np.argmin(max_users)
            max_users[idx] = users
            max_users_ind[idx] = i

    routes_selected = []
    for i in max_users_ind:
        routes_selected.append(sol[i])
    
    again = np.array([], dtype=int)
    for i in range(len(sol)):
        if i not in max_users_ind:
            for user in sol[i]: 
                if 0 < user <= n: 
                    again = np.append(again, user)

    return routes_selected, again 


def get_insertions_all(route):  
    #The insertion index indicates the index before which the new user will be inserted referring to the orginal tour 
    insertion_combis = np.array([], dtype=int)
    for i in range(1, len(route)):
        for j in range(i, len(route)):
            tupl = [i, j]
            insertion_combis = np.append(insertion_combis, tupl)
    insertion_combis = np.reshape(insertion_combis, (int(len(insertion_combis)/2),2))
    return insertion_combis


def repair_sol(sol):
    routes_selected, again = routes_users_again(sol)

    for user in again:
        insertion_found = False
        shortest = np.inf
        for j in range(len(routes_selected)): 
            route = routes_selected[j]
            combis = get_insertions_all(route)

            for i in range(len(combis)):
                new_route = gen_newroute(route, user, combis[i])
                check = eight_step(new_route)
                length = length_route(new_route)
                if check and length < shortest: 
                    insertion_found = True 
                    shortest = length
                    chosen_route = new_route
                    chosen_route_idx = j 

        if insertion_found:
            routes_selected[chosen_route_idx] = chosen_route
        else:
            chosen_route = np.array([0, user, user+n, 2*n+1],dtype=int)
            routes_selected.append(chosen_route)
    
    return routes_selected


