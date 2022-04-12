from feasability import *
from load_instance import *

import numpy as np
import random
import copy
import concurrent.futures


def get_unserved_solution(solution):
    succ = solution[0]
    unserved = []
    for i in range(len(succ)): 
        if succ[i] == 999 and i < n: #not <= python is zero index meaning index n-1 equals user n 
            unserved.append(i+1)
    return unserved

#Return the possible insertion combinations of a new user in a route; only considering everything after the last pickup vertex
def get_insertions(solution, route_idx):  
    #The insertion index indicates the index before which the new user will be inserted referring to the orginal tour 
    combis = []
    after_pickup = []

    pre = solution[1]
    RI = solution[2]

    num_routes = len(RI)

    if (num_routes-1) < route_idx: #start new route // num_routes-1 as python is zero indexed 
        combis.append([999,999]) #both pickup & delivery immediately after depot 

    else: 
        vertex = RI[route_idx][1]
        after_pickup.append(vertex)
        while vertex > n: #loop will always execute as last vertex in route is always > n or empty route 
            vertex = pre[vertex-1]
            after_pickup.append(vertex)
        after_pickup.reverse()
        for i in range(len(after_pickup)):
            for j in range(i, len(after_pickup)):
                combis.append([after_pickup[i],after_pickup[j]])
                
    return combis


def insert_consecutive(solution, user, indices, route_idx):
    succ = copy.deepcopy(solution[0])
    pre = copy.deepcopy(solution[1])
    RI = copy.deepcopy(solution[2])

    pickup_after = indices[0]
    dropoff_after = indices[1] #should be the same 

    if pickup_after == 0: 
        old_succesor = RI[route_idx][0].copy()
        RI[route_idx][0] = user

        succ[user-1] = user+n
        succ[user+n-1] = old_succesor

        if old_succesor == 2*n+1: #if else block not (strictly) necessary 
            RI[route_idx][1] = user+n
        else: 
            pre[old_succesor-1] = user+n
        pre[user+n-1] = user
        pre[user-1] = 0 

    else: 
        old_succesor = succ[pickup_after-1].copy()

        succ[pickup_after-1] = user
        succ[user-1] = user+n
        succ[user+n-1] = old_succesor 

        if old_succesor == 2*n+1:
            RI[route_idx][1] = user+n
        else: 
            pre[old_succesor-1] = user+n

        pre[user+n-1] = user 
        pre[user-1] = pickup_after
    
    RI[route_idx][2] += 1 #add one to length of route 
    
    solution = np.array([succ, pre, RI], dtype=object)

    return solution

def insert_not_consecutive(solution, user, indices, route_idx):
    succ = copy.deepcopy(solution[0])
    pre = copy.deepcopy(solution[1])
    RI = copy.deepcopy(solution[2])

    pickup_after = indices[0]
    dropoff_after = indices[1] #should be the same 

    if pickup_after == 0: 
        old_succesor_pickup = RI[route_idx][0].copy()
        RI[route_idx][0] = user

        old_succesor_dropoff = succ[dropoff_after-1].copy()

        succ[user-1] = old_succesor_pickup

        succ[dropoff_after-1] = user+n
        succ[user+n-1] = old_succesor_dropoff

        if old_succesor_dropoff == 2*n+1: #if else block not (strictly) necessary 
            RI[route_idx][1] = user+n
        else: 
            pre[old_succesor_dropoff-1] = user+n

        pre[user+n-1] = dropoff_after
        pre[user-1] = 0 

    else: 
        old_succesor_pickup = succ[pickup_after-1].copy()
        old_succesor_dropoff = succ[dropoff_after-1].copy()

        succ[pickup_after-1] = user
        succ[user-1] = old_succesor_pickup

        succ[dropoff_after-1] = user+n
        succ[user+n-1] = old_succesor_dropoff 

        if old_succesor_dropoff == 2*n+1:
            RI[route_idx][1] = user+n
        else: 
            pre[old_succesor_dropoff-1] = user+n

        pre[user+n-1] = dropoff_after 
        pre[user-1] = pickup_after


    RI[route_idx][2] += 1 #add one to length of route 
    
    solution = np.array([succ, pre, RI], dtype=object)

    return solution


def gen_new_solution(solution, user, indices, route_idx): #indices = list containing vertices after which to insert pickup and resp. dropoff
    succ = copy.deepcopy(solution[0])
    pre = copy.deepcopy(solution[1])
    RI = copy.deepcopy(solution[2])

    if indices == [999,999]: #start new route 
        succ[user-1] = user+n
        succ[user+n-1] = 2*n+1 #end-depot 
        pre[user+n-1] = user
        pre[user-1] = 0 

        RI.append(np.array([user, user+n, 1], dtype=int))
        
        new_solution = np.array([succ, pre, RI], dtype=object)


    else: 
        pickup_after = indices[0]
        dropoff_after = indices[1]

        #dropoff straight after pickup 
        if pickup_after == dropoff_after: 

            new_solution = insert_consecutive(solution, user, indices, route_idx)
        
        else: 
            new_solution = insert_not_consecutive(solution, user, indices, route_idx)


    return new_solution


def gen_route(solution, route_idx): 
    succ = solution[0]
    RI = solution[2]
    len_route = RI[route_idx][2]

    route = np.zeros(2*len_route+2, dtype=int)

    route[0] = 0
    route[-1] = 2*n+1
    vertex = RI[route_idx][0]
    i = 1
    while vertex != 2*n+1: 
        route[i] = vertex
        vertex = succ[vertex-1]
        i += 1

    return route

def get_feasible_users(solution, insertions_pos, unserved, route_idx):
    feasible_users = []
    for user in unserved: 
        for indices in insertions_pos:  
            new_sol = gen_new_solution(solution, user, indices, route_idx)
            route = gen_route(new_sol, route_idx)
            feasible = eight_step(route) #CHANGE 
            if feasible:
                feasible_users.append(user)
                break 
    return feasible_users

def gen_solution(P):

    succ = np.full(2*n, 999, dtype=int)
    pre = np.full(2*n, 999, dtype=int)
    RI = []
    solution = np.array([succ, pre, RI], dtype=object)

    route_idx = 0

    unserved = np.arange(1,n+1, dtype=int)

    while len(unserved) != 0:

        insertions_pos = get_insertions(solution, route_idx)
        feasible_users = get_feasible_users(solution, insertions_pos, unserved, route_idx)

        while len(feasible_users) != 0: 
            epsilon = random.random()

            if epsilon <= 0.1:
                new_user = np.random.choice(feasible_users)

            else: 
                if len(RI) == 0: 
                    last_pickup = 0
                else: 
                    vertex = solution[2][route_idx][1]
                    while vertex > n:
                        vertex = pre[vertex-1]
                    last_pickup = vertex

                prob = P[last_pickup, feasible_users]
                prob_norm = [i/sum(prob) for i in prob]
                new_user = random.choices(feasible_users, weights = prob_norm, k=1) 
                new_user = int(new_user[0])

            # Look for the best possible insertion and choose this one
            shortest = np.inf
            for indices in insertions_pos:
                new_sol = gen_new_solution(solution, new_user, indices, route_idx)
                new_route = gen_route(new_sol, route_idx)
                check = eight_step(new_route)
                length = length_route(new_sol, route_idx) 
                if check and length < shortest: 
                    shortest = length
                    chosen_sol = new_sol
            
            solution = chosen_sol

            insertions_pos = get_insertions(solution, route_idx)
            unserved = np.delete(unserved, np.where(unserved == new_user))
            feasible_users = get_feasible_users(solution, insertions_pos, unserved, route_idx)

        route_idx += 1

    solution = np.array(solution, dtype=object)
    
    return solution


def gen_N_solutions(N, P):
    solutions_all = [gen_solution(P) for _ in range(N)]
    return solutions_all

def gen_N_solutions_multiprocess(N,P):
    P_list = [P for _ in range(N)]
    with concurrent.futures.ProcessPoolExecutor() as executor: 
        results = executor.map(gen_solution, P_list)
    return results
