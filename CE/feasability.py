from load_instance import *

import numpy as np 

#@@@@@@@@@@@@@@@@@@ HELPER FUNCTIONS #@@@@@@@@@@@@@@@@@@
def length_route(solution, route_idx): 
    succ = solution[0] 
    RI = solution[2]

    length = 0

    vertex = RI[route_idx][0]
    length += dist[0, vertex]
    while vertex != 2*n+1:
        length += dist[vertex, succ[vertex-1]]
        vertex = succ[vertex-1]

    return length

def length_solution(solution):
    RI = solution[2]
    total = 0 

    for route_idx in range(len(RI)):
        total += length_route(solution, route_idx)

    total += (len(RI)-K)*100

    return total 

def calculate_ads(route, start):
    D = np.zeros(len(route)) #Departure time at vertex i 
    A = np.zeros(len(route)) #Arrival time at vertex i 
    B = np.zeros(len(route)) #Beginning of service at vertex i 
    W = np.zeros(len(route)) #Wait time before starting service at vertex i 
    Load = np.zeros(len(route)) #cummulative laod after leaving vertex i 
    RT = np.zeros(len(route)) #ride time, only specified for pickup vertices else 0 

    D[0] = start #initialize 

    for idx in range(1,len(route)):
        A[idx] = D[idx-1] + dist[route[idx-1], route[idx]]
        B[idx] = max(A[idx], e[route[idx]])
        W[idx] = B[idx] - A[idx]
        D[idx] = B[idx] + s[route[idx]]
        
        if route[idx] <= n:
            Load[idx] = Load[idx-1] + 1
        elif route[idx] == 2*n+1: 
            Load[idx] = Load[idx-1]
        else:
            Load[idx] = Load[idx-1] - 1

    for idx in range(1,len(route)-1):
        if route[idx] <= n:
            RT[idx] = 0 
        else: 
            idx2 = np.where(route == route[idx]-n)[0][0] #np.where returns an array we should always get arrays with only one element so we can just take the first one 
            RT[idx] = B[idx] - D[idx2]
            
    return A, B, W, D, Load, RT


#@@@@@@@@@@@@@@@@@@ PARTIAL CHECKS #@@@@@@@@@@@@@@@@@@
def check_tw(route, B):
    valid = True
    for i in range(len(route)):
        if B[i] > l[route[i]]:
            valid = False
            break 
    return valid 

def check_cap(route, Load):
    valid = True 
    for i in range(len(route)):
        if Load[i] > Q:
            valid = False 
            break 
    return valid 

def check_ridetime(route, RT): 
    valid = True 
    for i in range(len(route)): 
        if RT[i] > L:
            valid = False 
            break 
    return valid 

def check_routeduration(route, B):
    duration = B[-1] - B[0]
    if duration > T: 
        return False
    else:
        return True 

#@@@@@@@@@@@@@@@@@@ FORWARD TIME SLACK #@@@@@@@@@@@@@@@@@@
def calc_Fi(i, route, W, B, RT):
    slacks = np.full(len(route)-i, np.inf)
    idx = 0 
    for j in range(i, len(route)): 
        term1 = sum(W[i:j+1])
        if route[j] <= n: 
            term2 = max(0, l[route[j]]-B[j]) 
        else: 
            term2 = max(0, min(l[route[j]]-B[j], L - RT[j])) #or RT[j] equal to zero if j-n not visited before i 
        slack = term1 + term2
        slacks[idx] = slack
        idx += 1

    Fi = min(slacks)

    return Fi


#@@@@@@@@@@@@@@@@@@ FULL CHECK #@@@@@@@@@@@@@@@@@@
def eight_step(route): 
    start = e[route[0]]
    A, B, W, D, Load, RT = calculate_ads(route, start = start )

    if not check_tw(route, B):
        return False

    if not check_cap(route, Load):
        return False

    F0 = calc_Fi(0, route, W, B, RT)
    Wp = sum(W[:len(route)])
    start_time = e[route[0]] + min(F0, Wp)
    A, B, W, D, Load, RT = calculate_ads(route, start = start_time)

    if check_ridetime(route, RT): 
        if check_routeduration(route, B):
            return True #here all ride times ar feasible and we just need to check route duration 
        #No in this case we acutally still need to check route duration 

    #Some more adaptations for possibly solving ridetime violations 
    for i in range(len(route)): 
        if route[i] <= n: 
            Fi = calc_Fi(i, route, W, B, RT)
            Wp = sum(W[i+1:len(route)]) #i or i+1 
            
            W[i] += min(Fi, Wp)
            B[i] = A[i] + W[i]
            D[i] = B[i] + s[route[i]]

            for j in range(i+1, len(route)):
                A[j] = D[j-1] + dist[route[j-1], route[j]]
                B[j] = max(A[j], e[route[j]])
                W[j] = B[j] - A[j]
                D[j] = B[j] + s[route[j]]

                if j < len(route)-1 and route[j] > n:
                    idx2 = np.where(route == route[j]-n)[0][0] 
                    RT[j] = B[j] - D[idx2]
                
                #check whether the drive time is respected for all dropoff vertices after i, if so the route is feasible 
                if check_ridetime(route, RT):
                    if check_routeduration(route, B):
                        return True #also here we need to check route duration 
                         
    else: 
        return False
