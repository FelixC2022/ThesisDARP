from route_gen import *
from feasability import *
from repair_routes import *

import numpy as np 
import time 
import random

#ROUTE EXCHANGE
def add_all(seq):
    for i in seq:
        if (i <= n) and (i+n not in seq): 
            seq = np.append(seq, i+n)
        elif (i > n) and (i-n not in seq): 
            seq = np.append(seq, i-n)
    return seq


def empty_route(route, seq):
    for i in seq: 
        route = np.delete(route, np.where(route == i))
    return route


def get_insertions_all_route(route):
    combis = []
    for i in range(len(route)-1):
        for j in range(len(route)-1):
            combis.append([route[i], route[j]])
    return combis 

def gen_new_route(route, user, combi):
    new_route = np.zeros(len(route)+2, dtype=int)

    pickup_after = combi[0]
    dropoff_after = combi[1]

    i = 0 
    for vert in route: 
        new_route[i] = vert
        i += 1
        if vert == pickup_after: 
            new_route[i] = user
            i += 1
            if pickup_after == dropoff_after: 
                new_route[i] = user+n
                i += 1
        elif vert == dropoff_after: 
            new_route[i] = user+n
            i += 1
    return new_route


def length_route_list(route): 
    total = 0 
    for i in range(len(route)-1):
        total += dist[route[i], route[i+1]]
    return total


#we now want to insert seq1 into route2_empty
def insert_seq(route, seq):
    to_insert = seq[seq <= n] #maybe reshuffle this to add randomization

    for user in to_insert:
        combis = get_insertions_all_route(route)

        insertion_found = False
        shortest = np.inf
        for i in range(len(combis)):
            new_route = gen_new_route(route, user, combis[i])
            check = eight_step(new_route)
            length = length_route_list(new_route)
            if check and length < shortest: 
                insertion_found = True
                shortest = length
                chosen_route = new_route

        if insertion_found:
            route = chosen_route
        else:
            print(f"No insertion found for user {user}") #what do we do if we cannot insert the user?? 

    return route


def gen_solution_routes(routes):
    succ = np.full(2*n, 999, dtype=int)
    pre = np.full(2*n, 999, dtype=int)
    RI = np.full((len(routes), 3), 999, dtype=int)

    for i in range(len(routes)):
        route = routes[i]

        RI[i][0] = route[1] #first is 0
        RI[i][1] = route[-2] #last is 2n+1
        RI[i][2] = (len(route)-2)/2

        for i in range(1, len(route)-1): 
            succ[route[i]-1] = route[i+1] 
            pre[route[i]-1] = route[i-1]

    solution = np.array([succ, pre, RI], dtype=object)

    return solution
        

def route_exchange(solution, k_max): 
    RI = solution[2]

    selected_routes = random.sample(range(len(RI)), 2)
    route1_idx = selected_routes[0]
    route2_idx = selected_routes[1]

    #routes 
    route1 = gen_route(sol, route1_idx)
    route2 = gen_route(sol, route2_idx)

    #select lenght sequence
    k = random.choice(range(1,k_max+1)) 
    while k >= min(len(route1), len(route2)):
        k = random.choice(range(1,k_max+1)) 

    #select random start
    start1 = random.choice(range(1, len(route1)-k)) 
    start2 = random.choice(range(1, len(route2)-k))


    #generate the sequences
    seq1 = route1[start1:start1+k]
    seq2 = route2[start2:start2+k]
    seq1 = add_all(seq1) #add pickup/dropoff
    seq2 = add_all(seq2) #add pickup/dropoff

    #generate the new routes
    route1_empty = empty_route(route1, seq1)
    route2_empty = empty_route(route2, seq2)

    new_route2 = insert_seq(route2_empty, seq1)
    new_route1 = insert_seq(route1_empty, seq2)

    #calculate savings
    cost_old = (length_route_list(route1) + length_route_list(route2))
    cost_new = (length_route_list(new_route1) + length_route_list(new_route2))
    cost_saving = cost_old - cost_new #so if negative old is better 

    #generate new solution with all routes  
    routes = [new_route1, new_route2]
    for i in range(len(RI)): 
        if i not in selected_routes: 
            route = gen_route(solution, i)
            routes.append(route)
            
    #Insert the vertices that could not be inserted into their assigned route

    if cost_saving > 0: 
        new_solution = gen_solution_routes(routes) #make the new succ/pre/ri based on the new route 

    else: 
        new_solution = solution 

    
    return cost_saving, new_solution


#TESTING 

P = np.full((n+2, n+2), 1/((n+2)*(n+2))) #uniform initialization of P 
sol = gen_solution(P)
sol = repair_sol(sol)

print(length_solution(sol))

start_time = time.time()

saving, new_solution = route_exchange(sol, 4)


print("--- %s seconds ---" % (time.time() - start_time))


print(saving)

print(new_solution)

print(length_solution(new_solution))
