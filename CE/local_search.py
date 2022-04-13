from load_instance import *
from feasability import *
from route_gen import *
from repair_routes import *


import numpy as np 
import time 
import random
import copy
import concurrent.futures


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
        

    return True, route #old_route

#@@@@@@@@@@@@@@@@@@ ROUTE EXCHANGE #@@@@@@@@@@@@@@@@@@

def route_exchange(solution): 
    RI = solution[2]

    for _ in range(5):
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

        for _ in range(5): 
            random.shuffle(seq1)
            check1, new_route2 = insert_seq(route2_empty, seq1)
            if check1:
                break
        
        if check1 == False: 
            #return 0, solution #return old solution 
            continue

        for _ in range(5):
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
        
            return new_solution

    return solution

def route_exchange_N(solutions_all):
    result = [route_exchange(sol) for sol in solutions_all]
    return result

def route_exchange_N_multiprocess(solutions_all):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        result = executor.map(route_exchange, solutions_all)
    return result


# #@@@@@@@@@@@@@@@@@@ TEST INSTANCE #@@@@@@@@@@@@@@@@@@ 

# #gen test instance
# P = np.full((n+2, n+2), 1)
# P[0,-1] = 0 #from depot to depot 
# for i in range(len(P)): 
#     P[i,i] = 0 #to itself 
#     P[i, -1] = 0 #from a pickup to end_depot 
#     P[-1, i] = 0 #from end_depot to a pickup 

# total = 0 
# for row in P: 
#     total += sum(row)
# P = P/total  #normalize

# sol = gen_solution(P)
# sol = repair_sol(sol)


# #@@@@@@@@@@@@@@@@@@ CROSS EXCHANGE #@@@@@@@@@@@@@@@@@@ 

# #gen all the routes 
# routes = [gen_route(sol, idx) for idx in range(len(sol[2]))]
# idx_select = random.sample(range(len(routes)), 2)
# route1 = routes[routes[idx_select[0]]]
# route2 = routes[routes[idx_select[1]]]

# # Select lenght of sequence and num routes involved
# k_max = 3
# k = random.choice(range(1,k_max+1)) 

# while k >= min(len(route1)):
#     k = random.choice(range(1,k_max+1)) 

# if len(route1)-k == 1: 
#     start1 = 1
    
# else:
#     start1 = random.choice(range(1, len(route1)-k)) 
#     start2 = random.choice(range(1, len(route2)-k))


# #generate the first sequence 
# seq1 = route1[start1:start1+k] 
# seq1 = add_all(seq1) #add the other vertices 
# route1 = empty_route(route1, seq1)

# route2 = insert_seq(route2, seq1)


#@@@@@@@@@@@@@@@@@@ ZERO SPLIT #@@@@@@@@@@@@@@@@@@ 
def gen_load(route):
    Load = np.zeros(len(route), dtype=int)
    for i in range(1,len(route)):
        if route[i] <= n:
            Load[i] = Load[i-1] + 1
        elif route[i] == 2*n+1: 
            Load[i] = Load[i-1]
        else:
            Load[i] = Load[i-1] - 1
    return Load 

def gen_naturals(route):
    Load = gen_load(route)

    naturals = []
    for i in range(len(Load)): 
        
        if Load[i-1]==0 and Load[i] == 1:
            seq = []
            for j in range(i, len(route)):
                seq.append(route[j])
                if Load[j] == 0: 
                    break  
            #append 
            naturals.append(seq)
            
    return naturals

def zero_split(solution):
    routes = [gen_route(solution, idx) for idx in range(len(solution[2]))]
    
    size = 2 
    while size == 2: #empty route 
        idx = random.choice(range(len(routes)))
        route1 = routes[idx]
        size = len(route1)

    #Select one of the
    nats = gen_naturals(route1)
    seq = random.choice(nats)
    seq = np.array(seq, dtype=int)
    route1_new = empty_route(route1, seq)
    routes[idx] = route1_new

    #Select a new route
    routes_idx = np.delete(np.arange(len(routes), dtype=int), idx)
    random.shuffle(routes_idx)
    routes_idx = np.append(routes_idx, idx) #try original route if no insertion can bou found in the other routes 

    for idx2 in routes_idx:

        route2 = routes[idx2]

        #Try to insert the seq in the selected route 
        check = False
        for _ in range(3): 
            check, route2_new = insert_seq(route2, seq)
            random.shuffle(seq)
            if check:
                break

        if check == False: 
            continue #move on to next route in for loop 

        else: 
            cost_old = length_route_list(route1) + length_route_list(route2)
            cost_new = length_route_list(route1_new) + length_route_list(route2_new)

            if cost_new < cost_old: 
                routes[idx2] = route2_new
                new_solution = gen_solution_routes(routes)
                
                return new_solution 

         
    return solution

def zero_split_N_multiprocess(solutions_all): 
    with concurrent.futures.ProcessPoolExecutor() as executor:
        result = executor.map(zero_split, solutions_all)
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

def relocate(solution):

    cost_old = length_solution(solution)

    #Display the routes 
    routes = []
    for i in range(len(solution[2])):
        routes.append(gen_route(solution, i))

    #select users to insert again (based on distance to Lg)
    again = np.zeros(len(routes), dtype=int)
    for i in range(len(routes)):
        route = routes[i] 
        dists = dist_Lg_all(route)
        vert = route[np.where(dists == max(dists))]
        if vert > n: 
            vert = vert-n
        again[i] = vert

    #clear the routes 
    for i in range(len(again)):
        user = again[i] 

        i1 = np.where(routes[i] == user)
        routes[i] = np.delete(routes[i], i1)

        i2 = np.where(routes[i] == user+n)
        routes[i] = np.delete(routes[i], i2)

    routes_old = copy.deepcopy(routes)


    #insert the users again in a random rooute & try 5 times to get an improving solution 
    for _ in range(5):
        routes = copy.deepcopy(routes_old)

        for i in range(len(again)):
            user = again[i]  #i is the original route of the user
            routes_idx = np.delete(np.arange(len(routes), dtype=int), i)
            random.shuffle(routes_idx)
            routes_idx = np.append(routes_idx, i) #try original route if no insertion can bou found in the other routes 

            insertion_found = False
            for idx in routes_idx:

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
                    break #as soon as an insertion is found in a route don't look to the other routes 
        
        cost_new = 0 
        for i in routes: 
            cost_new += length_route_list(i)
        
        if cost_old > cost_new: 
            new_sol = gen_solution_routes(routes)
            #print(f'improvement: {cost_old-cost_new}')
            return new_sol
    
    return solution #if after the 5 iterations no improving solutino is found return original solution

def relocate_N_multiprocess(solutions_all):
    with concurrent.futures.ProcessPoolExecutor() as executor: 
        result = executor.map(relocate, solutions_all)
    return result

#@@@@@@@@@@@@@@@@@@ TEST INSTANCE #@@@@@@@@@@@@@@@@@@
# P = np.full((n+2, n+2), 1)
# P[0,-1] = 0 #from depot to depot 
# for i in range(len(P)): 
#     P[i,i] = 0 #to itself 
#     P[i, -1] = 0 #from a pickup to end_depot 
#     P[-1, i] = 0 #from end_depot to a pickup 

# total = 0 
# for row in P: 
#     total += sum(row)
# P = P/total  #normalize

# sol = gen_solution(P)
# sol = repair_sol(sol)


# start = time.time()

# new_sol = relocate(sol)


# print(f'took {time.time()-start} secs to finish')