from feasability import *
from load_instance import *

import numpy as np
from tqdm import tqdm
import random
# import asyncio

def get_unserved_solution(solution):
    unserved = np.arange(1,n+1, dtype=int)
    for route in solution:
        for vertex in route[0]: 
            if vertex <= n: 
                unserved = np.delete(unserved, np.where(unserved == vertex))
    return unserved

def get_unserved_route(route):
    unserved = np.arange(1, n+1, dtype=int)
    for vertex in route: 
        if vertex <= n:
            unserved = np.delete(unserved, np.where(unserved==vertex))

#Return the possible insertion combinations of a new user in a route; only considering everything after the last pickup vertex
def get_insertions(route):  
    #The insertion index indicates the index before which the new user will be inserted referring to the orginal tour 
    insertion_combis = np.array([], dtype=int)
    last_pickup = int(max((np.argwhere(route <= n))))
    for i in range(last_pickup+1, len(route)):
        for j in range(i, len(route)):
            tupl = [i, j]
            insertion_combis = np.append(insertion_combis, tupl)
    insertion_combis = np.reshape(insertion_combis, (int(len(insertion_combis)/2),2))
    return insertion_combis

def gen_newroute(route, user, indices): #indices = array with index for pickup and index for delivery, both refer to the original tour 
    new_route = np.insert(route, indices[0], user)
    new_route = np.insert(new_route, indices[1]+1, user+n)
    return new_route

def get_feasible_users(route, insertions_pos, unserved):
    feasible_users = np.array([], int)
    for user in unserved: 
        for indices in insertions_pos:  
            new_tour = gen_newroute(route, user, indices)
            feasible = eight_step(new_tour)
            if feasible:
                feasible_users = np.append(feasible_users, user)
                break 
    return feasible_users

def gen_solution(P):
    solution = []
    unserved = get_unserved_solution(solution)

    while len(unserved) != 0:
        route = np.array([ 0, 2*n+1], dtype=int) #np.array([0, 5, 5+n, 2*n+1], dtype=int)
        insertions_pos = get_insertions(route)
        feasible_users = get_feasible_users(route, insertions_pos, unserved)

        while len(feasible_users) != 0: 
            epsilon = random.random()

            if epsilon <= 0.1:
                new_user = np.random.choice(feasible_users)

            else: 
                last_pickup = int(max((np.argwhere(route <= n))))
                prob = P[last_pickup, feasible_users]
                prob_norm = [i/sum(prob) for i in prob]
                new_user = random.choices(feasible_users, weights = prob_norm) 

            # Look for the best possible insertion and choose this one
            shortest = np.inf
            for i in range(len(insertions_pos)):
                new_route = gen_newroute(route, new_user, insertions_pos[i])
                check = eight_step(new_route)
                length = length_route(new_route)
                if check and length < shortest: 
                    shortest = length
                    route = new_route

            insertions_pos = get_insertions(route)
            unserved = np.delete(unserved, np.where(unserved == new_user))
            feasible_users = get_feasible_users(route, insertions_pos, unserved)

        # solution = np.append(solution, route)
        solution.append(route)

    solution = np.array(solution, dtype=object)
    
    return solution

def gen_N_solutions(N, P):
    # tasks = []
    # for i in range(N):
    #     task = asyncio.create_task(gen_solution())
    #     tasks.append(task)

    # solutions_all = await asyncio.gather(*tasks)

    solutions_all = []
    for i in range(N):
        solution = gen_solution(P) 
        solutions_all.append(solution)

    return solutions_all