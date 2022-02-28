import numpy as np 

from preprocess import load_data, get_depot_co


#READING IN & PREPROCESSING INSTANCE DATA 
path = 'data/a9-72hetIUY.txt'

num_vehs, num_reqs, route_duration, Q, x_co, y_co, s, L, q, e, l, R = load_data(path)

depot_co = get_depot_co(num_vehs)


#HELPER FUNCTIONS 
def dist(k,i,j):
    end_depot = 2*num_reqs+1
    if i == 0 and j == end_depot: 
        arc_length = 0 
    elif (i == 0) or (i == end_depot):
        arc_length = np.linalg.norm((depot_co[k]) - (np.array((x_co[j],y_co[j]))))
    elif (j == 0) or (j == end_depot):
        arc_length = np.linalg.norm((depot_co[k]) - (np.array((x_co[i],y_co[i]))))        
    else: 
        arc_length = np.linalg.norm((np.array((x_co[i],y_co[i])) - (np.array((x_co[j],y_co[j])))))  
    return arc_length 


def compute_costincrease(k,a,tour,i,j): 
    n = num_vehs
    if i == j: #j after i, one arc deleted, three new arcs introduced 
        arc_del1 = dist(k, tour[i-1], tour[i])
        arc_new1 = dist(k, tour[i-1], a)
        arc_new2 = dist(k, a, a+n)
        arc_new3 = dist(k, a+n, tour[i])
        cost_increase = arc_new1 + arc_new2 + arc_new3 - arc_del1
        
    else: #j not immediately after i, 2 arcs deleted, 4 new arcs introduced 
        arc_del1 = dist(k, tour[i-1], tour[i])
        arc_new1 = dist(k, tour[i-1], a)
        arc_new2 = dist(k, a, tour[i])
        
        arc_del2 = dist(k, tour[j-1], tour[j])
        arc_new3 = dist(k, tour[j-1], a+n)
        arc_new4 = dist(k, a+n, tour[j])
        cost_increase = arc_new1 + arc_new2 + arc_new3 + arc_new4 - arc_del1 - arc_del2
    
    return cost_increase

def length_tour(tour,k):
    dist_total = sum([dist(k, tour[i], tour[i+1]) for i in range(len(tour)-1)])
    return dist_total       

def length_total(state): 
    n = num_reqs
    succ = state[0]
    RI = state[2]
    
    total_length = 0 

    for k in range(len(RI)): 
        tour = [0]
        vertex = RI[k][0]
        if vertex != None: 
            while vertex != (2*n+1):
                tour.append(vertex)
                vertex = succ[vertex-1]
            tour.append(2*n+1)
            total_length += length_tour(tour, k)
    
    return total_length

def get_legal_actions(state): 
    unserved_requests= []
    succ = state[0] #state[0] is succ array
    for i in range(num_reqs):
        if succ[i]==None:
            unserved_requests.append(i+1) #i+1 because the element with index i in succ corresponds to user vertex i+1, python is 0-indexed users start from 1 
    return unserved_requests

def is_game_over(state):
    full_solution = True
    for i in range(num_reqs): 
        if state[0][i]==None:
            full_solution=False
            break
    return full_solution

def display_routes(state):
    #assumes full routes 
    n = num_reqs
    succ = state[0]
    RI = state[2]
    
    routes = list()

    for k in range(len(RI)): 
        tour = [0]
        vertex = RI[k][0]
        if vertex != None: 
            while vertex != (2*n+1):
                tour.append(vertex)
                vertex = succ[vertex-1]
            tour.append(2*n+1) 

        routes.append(tour)
    
    return routes

#Set for the game_result function  
best_score = np.inf
best_state = None 
            
def game_result(state):
    global best_score, best_state
    
    score = length_total(state)
    
    if score < best_score:
        best_score = score
        best_state = state 
        return 1
    if best_score < score < 2*best_score: 
        return (2-score/best_score) #linear inner function 
    else: #tie 
        return 0

def initialize_state():
    succ1=[None]*(2*num_reqs)
    pre1=[None]*(2*num_reqs)
    RI1=[[None,None] for v in range(num_vehs)]
    earliest1=e
    latest1=l
    
    cap1=[[0 for i in range(2*num_reqs +2)] for r in range(len(R))]
    
    for i in range(len(R)):
        cap1[i][0]=0
        cap1[i][2*num_reqs+1]=0

    succ=np.array(succ1)
    pre=np.array(pre1)
    RI=np.array(RI1)
    earliest=np.array(earliest1)
    latest=np.array(latest1)
    cap=np.array(cap1)
    state = [pre1, succ1, RI1, earliest1, latest1, cap1]
    return state
