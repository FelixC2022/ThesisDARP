from load_instance import *
from feasability import *
from route_gen import *
from repair_routes import *


import numpy as np 
import time 
import random
import concurrent.futures

#@@@@@@@@@@@@@@@@@@ TEST INSTANCE #@@@@@@@@@@@@@@@@@@
P = np.full((n+2, n+2), 1)
P[0,-1] = 0 #from depot to depot 
for i in range(len(P)): 
    P[i,i] = 0 #to itself 
    P[i, -1] = 0 #from a pickup to end_depot 
    P[-1, i] = 0 #from end_depot to a pickup 

total = 0 
for row in P: 
    total += sum(row)
P = P/total  #normalize


sol = gen_solution(P)
sol = repair_sol(sol)

cost_initial = length_solution(sol)

#Display the routes 
routes = []
for i in range(len(sol[2])):
    routes.append(gen_route(sol, i))

#@@@@@@@@@@@@@@@@@@ UTILS #@@@@@@@@@@@@@@@@@@

def get_insertions_all_route(route):
    combis = []
    for i in range(len(route)-1):
        for j in range(i, len(route)-1):
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
        

#@@@@@@@@@@@@@@@@@@ ROUTE EXCHANGE #@@@@@@@@@@@@@@@@@@
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

        if not insertion_found:
            return False, route #if a user can't be inserted stop and try in different order
        
        else: 
            route = chosen_route
        

    return True, chosen_route #old_route

def route_exchange(solution): 
    RI = solution[2]

    for i in range(5):
        selected_routes = random.sample(range(len(RI)), 2)
        route1_idx = selected_routes[0]
        route2_idx = selected_routes[1]

        #routes 
        route1 = gen_route(solution, route1_idx)
        route2 = gen_route(solution, route2_idx)

        #select lenght sequence
        k_max = 4
        k = random.choice(range(1,k_max+1)) 
        while k >= min(len(route1), len(route2)):
            k = random.choice(range(1,k_max+1)) 

        if len(route1)-k == len(route2)-k == 1: 
            start1 = 1
            start2 = 1 

        elif len(route1)-k == 1: 
            start1 = 1
            start2 = random.choice(range(1, len(route2)-k))

        elif len(route2)-k ==1: 
            start1 = random.choice(range(1, len(route1)-k))
            start2 = 1
            
        else:
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

        for i in range(5): 
            random.shuffle(seq1)
            check1, new_route2 = insert_seq(route2_empty, seq1)
            if check1:
                break
        
        if check1 == False: 
            #return 0, solution #return old solution 
            continue

        for i in range(5):
            random.shuffle(seq2)
            check2, new_route1 = insert_seq(route1_empty, seq2)
            if check2:
                break

        if check2 == False:
            continue
            #return 0, solution #return old solution 

        #calculate savings
        cost_old = (length_route_list(route1) + length_route_list(route2))
        cost_new = (length_route_list(new_route1) + length_route_list(new_route2))
        cost_saving = cost_old - cost_new #so if negative old is better 

        if cost_saving > 0: 
            #generate new solution with all routes  
            routes = [new_route1, new_route2]
            for i in range(len(RI)): 
                if i not in selected_routes: 
                    route = gen_route(solution, i)
                    routes.append(route) 
        
            new_solution = gen_solution_routes(routes) #make the new succ/pre/ri based on the new route 
        
            return cost_saving, new_solution
        
        else: 
            continue

    else: 
        return 0, solution

def route_exchange_N(solutions_all):
    result = [route_exchange(sol) for sol in solutions_all]
    return result

def route_exchange_N_multiprocess(solutions_all):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        result = executor.map(route_exchange, solutions_all)
    return result

#@@@@@@@@@@@@@@@@@@ RELOCATE #@@@@@@@@@@@@@@@@@@

def calc_G(route):
    G = np.zeros(2)
    for i in route[:-1]: #only consider depot once 
        G[0] += x_co[i]
        G[1] += y_co[i]
    G[0] = G[0]/len(route[:-1])
    G[1] = G[1]/len(route[:-1])
    return G 

#Calculated distance between p3 and Lg (line between G and depot)
def dist_Lg(G, depot, p3):
    dist = np.abs(np.linalg.norm(np.cross(G-depot,p3-depot))/np.linalg.norm(G-depot))
    return dist 

def dist_Lg_all(route):
    depot = np.array([x_co[0], y_co[0]])
    G = calc_G(route)

    dist = np.zeros(len(route))
    dist[0] = 0
    dist[-1] = 0 
    i = 1
    for vert in route[1:-1]: #no start and end depot 
        p3 = np.array(x_co[vert], y_co[vert]) 
        dist[i] = dist_Lg(G, depot, p3) 
        i += 1 

    return dist


# print(routes)

start = time.time()

again = np.zeros(len(routes), dtype=int)
for i in range(len(routes)):
    route = routes[i] 
    dists = dist_Lg_all(route)
    vert = route[np.where(dists == max(dists))]
    if vert > n: 
        vert = vert-n
    again[i] = vert

# print(again)

for i in range(len(again)):
    user = again[i] 

    i1 = np.where(routes[i] == user)
    routes[i] = np.delete(routes[i], i1)

    i2 = np.where(routes[i] == user+n)
    routes[i] = np.delete(routes[i], i2)


for i in range(len(again)):
    user = again[i]  #i is the original route of the user
    routes_idx = np.delete(np.arange(len(routes), dtype=int), i)

    insertion_found = False
    while insertion_found == False: #if all routes have been tried and no insertion is found this will loop forever 

        if len(routes_idx) == 0: 
            print('no insertion was found')
            break 

        idx = random.choice(routes_idx)
        routes_idx = np.delete(routes_idx, np.where(routes_idx == idx))

        route = routes[idx]
        combis = get_insertions_all_route(route)

        shortest = np.inf 
        for combi in combis:
            new_route = gen_new_route(route, user, combi)
            check = eight_step(new_route)
            length = length_route_list(new_route)
            if check and length < shortest: 
                insertion_found = True
                shortest = length
                chosen_route = new_route
        
        if insertion_found: 
            routes[idx] = chosen_route
        

# print(routes)

cost_new = 0 
for i in routes: 
    cost_new += length_route_list(i)

print(cost_initial)
print(cost_initial-cost_new)


print(f'took {time.time()-start} secs to finish')