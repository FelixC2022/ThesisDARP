import numpy as np 
import copy
import random


from preprocess import *
from feasability import *

#@@@@@@@@@@@@@@@@@@ LENGTH ROUTE IN LIST FORMAT #@@@@@@@@@@@@@@@@@@

def length_route_list(route): 
    total = 0 
    for i in range(len(route)-1):
        total += dist[route[i], route[i+1]]
    return total

#@@@@@@@@@@@@@@@@@@ GENARATE SOLUTION FROM ROUTE #@@@@@@@@@@@@@@@@@@

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

#new route after inserting user 
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

#@@@@@@@@@@@@@@@@@@ GENARATE A NEW SOLUTION AFTER INSERTING USER #@@@@@@@@@@@@@@@@@@

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

#@@@@@@@@@@@@@@@@@@ GET LEGAL ACTIONS #@@@@@@@@@@@@@@@@@@

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

def get_legal_actions(solution):
    succ = solution[0]
    unserved = []
    for i in range(len(succ)): 
        if succ[i] == 999 and i < n: #not <= python is zero index meaning index n-1 equals user n 
            unserved.append(i+1)

    random.shuffle(unserved)

    return unserved

#@@@@@@@@@@@@@@@@@@ MOVE #@@@@@@@@@@@@@@@@@@

def move(solution, action):
    user = action

    insertion_found = False 

    route_idx = 0

    while not insertion_found:

        insertions = get_insertions(solution, route_idx) #only after last pickup vertex in the route 

        shortest = np.inf
        for combi in insertions:
            new_sol = gen_new_solution(solution, user, combi, route_idx)
            new_route = gen_route(new_sol, route_idx)
            check = eight_step(new_route)
            length = length_route_list(new_route)
            if check and length < shortest: 
                insertion_found = True
                shortest = length
                chosen_sol = new_sol
                #break #dont look for best insertion in route
        
        route_idx += 1 
    
    return chosen_sol

#@@@@@@@@@@@@@@@@@@ CHECK IF SOLUTION IS COMPLETE#@@@@@@@@@@@@@@@@@@

def is_game_over(solution):
    succ = solution[0]
    for i in range(len(succ)): 
        if succ[i]==999:
            return False
    return True

#@@@@@@@@@@@@@@@@@@ SCORES SIMULATION #@@@@@@@@@@@@@@@@@@
#Set for the game_result function  
best_std_score = np.inf
best_state = None 

def game_result(state):
    global best_std_score, best_state
    
    RI = state[2]
    users_served = 0
    for row in RI:
        users_served += row[2]

    score = length_solution(state)
    std_score = score/users_served
    
    if std_score < best_std_score:
        best_std_score = std_score
        best_state = state 
        return 1

    if best_std_score < std_score < 1.25*best_std_score: #2 TOO LARGE ?????? 
        return (2-std_score/best_std_score) #linear inner function 

    else: #tie 
        return 0


