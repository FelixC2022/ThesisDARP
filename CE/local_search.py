#%%
from route_gen import *
from feasability import *
from repair_routes import *

import numpy as np 
import time 
import random

P = np.full((n+2, n+2), 1/((n+2)*(n+2))) #uniform initialization of P 
sol = gen_solution(P)
sol = repair_sol(sol)

start_time = time.time()

#RELOCATE
#The route exchange: exchange two segments of two routes if they are feasible & have cost savings 
def add_all(seq):
    for i in seq: #can cause doubles if both vertices are already in the solution, but this doesn't cause problems 
        if i <= n: 
            seq = np.append(seq, i+n)
        else: 
            seq = np.append(seq, i-n)
    return seq

def empty_route(route, seq):
    for i in seq: 
        route = np.delete(route, np.where(route == i))
    return route

#we now want to insert seq1 into route2_empty
def insert_seq(route, seq):
    to_insert = seq[seq <= n] #maybe reshuffle this to add randomization

    for user in to_insert:
        combis = get_insertions_all(route)
        insertion_found = False
        shortest = np.inf
        for i in range(len(combis)):
            new_route = gen_newroute(route, user, combis[i])
            check = eight_step(new_route)
            length = length_route(new_route)
            if check and length < shortest: 
                insertion_found = True
                shortest = length
                chosen_route = new_route

        if insertion_found:
            route = chosen_route
        else:
            print(f"No insertion found for user {user}") #what do we do if we cannot insert the user?? 

    return route

def route_exchange(solution, k_max): 
    #select two random routes
    selected_routes = random.sample(range(len(solution)), 2)
    route1 = sol[selected_routes[0]]
    route2 = sol[selected_routes[1]]

    #select lenght sequence
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
    cost_old = (length_route(route1) + length_route(route2))
    cost_new = (length_route(new_route1) + length_route(new_route2))
    cost_saving = cost_old - cost_new #so if negative old is better 

    return cost_saving, new_route1, new_route2

saving, route1, route2 = route_exchange(sol, 3)

print(saving)

print("--- %s seconds ---" % (time.time() - start_time))