from load_instnace import load_instance

import numpy as np 
import time
#from numba import njit

path = 'CE/data/a2-16.txt'
K, n, T, Q, L, x_co, y_co, s, cap, e, l  = load_instance(path)

#Helper function 
def dist(i,j): 
    return np.linalg.norm((np.array((x_co[i],y_co[i])) - (np.array((x_co[j],y_co[j])))))  

def length_tour(tour): 
    """
    THIS IS NOT CORRECT AS DOES NOT TAKE INTO ACCOUNT WAITING TIMES

    THE CORRECT FORMULA IS B2n+1 - B0 where Bi is the beginning of service at vertex i 
    
    """
    dist_total = sum([dist(tour[i], tour[i+1]) for i in range(len(tour)-1)])
    return dist_total  

def f_function(tour, alpha, beta, gamma, tau):
    f = length_tour(tour) + alpha*load_vio+ beta*duration_vio + gamma*timewindow_vio + tua*ridtime_vio
    return f 

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

route = np.array([0, 1, 2, 3, 3+n, 1+n, 2+n, 2*n+1], dtype=int)#the route under consideration 

def calculate_ads(route, start=e[route[0]]):
    D = np.zeros(len(route)) #Departure time at vertex i 
    A = np.zeros(len(route)) #Arrival time at vertex i 
    B = np.zeros(len(route)) #Beginning of service at vertex i 
    W = np.zeros(len(route)) #Wait time before starting service at vertex i 
    Load = np.zeros(len(route)) #cummulative laod after leaving vertex i 
    RT = np.zeros(len(route)) #ride time, only specified for pickup vertices else 0 

    D[0] = start #initialize 

    for idx in range(1,len(route)):
        A[idx] = D[idx-1] + dist(route[idx-1], route[idx]) 
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

#Eight step evaluation procedure:
#new_route = [0, 1, 2, 3, 3+n, 1+n, 2+n, 2*n+1]

#Check TW and Cap if invalid calculate f(route)
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

#Calculate F0
def calc_Fi(i, route, W, B, RT):
    slacks = []
    for j in range(i, len(route)): 
        term1 = sum(W[:j+1])
        term2 = max(0, min(l[route[j]]-B[j], L - RT[j]))
        slack = term1 + term2
        slacks.append(slack)
    Fi = min(slacks)
    return Fi

def eight_step(route): 
    A, B, W, D, Load, RT = calculate_ads(route)

    if not check_tw(route, B):
        return False 

    if not check_cap(route, Load):
        return False 

    F0 = calc_Fi(0, route, W, B, RT)
    Wp = sum(W[:len(route)])
    start_time = e[route[0]] + min(F0, Wp)
    A, B, W, D, Load, RT = calculate_ads(route, start = start_time)

    if check_ridetime(route, RT):
        return True

    #Some more adaptations for possibly solving ridetime violations 
    for i in range(len(route)): 
        if route[i] <= n: 
            Fi = calc_Fi(i, route, W, B, RT)
            Wp = sum(W[:len(route)])
            
            W[i] += min(Fi, Wp)
            B[i] = A[i] + W[i]
            D[i] = B[i] + s[route[i]]

            for j in range(i+1, len(route)):
                A[j] = D[j-1] + dist(route[j-1], route[j]) 
                B[j] = max(A[j], e[route[j]])
                W[j] = B[j] - A[j]
                D[j] = B[j] + s[route[j]]

                if route[j] > n:
                    idx2 = np.where(route == route[idx]-n)[0][0] 
                    RT[j] = B[j] - D[idx2]
                
                #check whether the drive time is respected for all dropoff vertices after i, if so the route is feasible 
                pass 
                         

    if not check_routeduration(route, B):
         return False 

    else: 
        return True 


route = np.array([0, 1, 17, 2, 5, 8, 2+n, 9, 8+n, 9+n, 33], dtype=int)
route2 = np.array([0, 2, 2+n, 8, 5, 8+n, 5+n, 9, 9+n, 33], dtype=int)


start_time = time.time()
test = eight_step(route2)
print("--- %s seconds ---" % (time.time() - start_time))