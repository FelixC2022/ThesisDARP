from feasability import *
from load_instance import *

import numpy as np

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
            feasible, B = eight_step(new_tour)
            if feasible:
                feasible_users = np.append(feasible_users, user)
                break 
    return feasible_users

# def check_feasibles(ls): #ls is a list with the routes 
#     feasible = np.zeros(len(ls))
#     for i in range(len(ls)):
#         feasible[i] =  eight_step(ls[i])
#         return feasible

#Testing 

# In total there are 16 users which need to be served 
# route_intial = [0, 1, 2, 1+n, 2+n, 2*n+1]

# We define a move as inserting a customer (both pickup & dropoff) after the last pickup vertex in the route 

# Let's say we want to add customer 3 (with vertices 3 and 3+n) to the route we have the following options

# We need a function to generate all these and check them (maybe we can parallelize this) as soon as one feasible insertion is found move on to the nex customer 

# 1 new_route = [0, 1, 2, 3, 3+n, 1+n, 2+n, 2*n+1]

# 2 new_route = [0, 1, 2, 3, 1+n, 3+n, 2+n, 2*n+1]

# 3 new_route = [0, 1, 2, 3, 1+n, 2+n, 3+n, 2*n+1]

# 3 new_route = [0, 1, 2, 1+n, 3, 3+n, 2+n, 2*n+1]

# 4 new_route = [0, 1, 2, 1+n, 3, 2+n, 3+n, 2*n+1]

# 5 new_route = [0, 1, 2, 1+n, 2+n, 3, 3+n, 2*n+1]

# new_route = [[0, 1, 2, 3, 3+n, 1+n, 2+n, 2*n+1],
# [0, 1, 2, 3, 1+n, 3+n, 2+n, 2*n+1],
# [0, 1, 2, 3, 1+n, 2+n, 3+n, 2*n+1],
# [0, 1, 2, 1+n, 3, 3+n, 2+n, 2*n+1],
# [0, 1, 2, 1+n, 3, 2+n, 3+n, 2*n+1],
# [0, 1, 2, 1+n, 2+n, 3, 3+n, 2*n+1]]