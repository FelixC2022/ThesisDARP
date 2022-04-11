from route_gen import *
from feasability import *
from repair_routes import *

import numpy as np 
import time 
import random


#Gen solution
P = np.full((n+2, n+2), 1/((n+2)*(n+2))) 
sol = gen_solution(P)
sol = repair_sol(sol)
RI = sol[2]
succ = sol[0]
pre = sol[1]

#select routes for seq swap 
selected_routes = random.sample(range(len(RI)), 2)
route1_idx = selected_routes[0]
route2_idx = selected_routes[1]

#lengths routes
len_route1 = (2*RI[route1_idx][2])+2
len_route2 = (2*RI[route2_idx][2])+2


#routes 
route1 = gen_route(sol, route1_idx)
route2 = gen_route(sol, route2_idx)

#select length seq
k_max = 3
k = random.choice(range(1,k_max+1)) 

#select random start
start1 = random.choice(range(1, len_route1-k)) 
start2 = random.choice(range(1, len_route2-k))


#Generate seq to delete 
to_del1 = np.array(route1[start1:start1+k], dtype=int)
to_del2 = np.array(route2[start2:start2+k], dtype=int)

to_del1_comp = []
to_del21_comp = []

for vertex in to_del1: 
    if vertex <= n and vertex+n not in to_del1:
        to_del1_comp.append(vertex+n)
    elif vertex > n and vertex-n not in to_del1:
        to_del1_comp.append(vertex-n)

print(route1)
print(to_del1)
print(to_del1_comp)

first_vert = pre[to_del1[0]-1]
last_vert = succ[to_del1[-1]-1]

succ[fist_vert-1] =  last_vert
pre[last_vert-1] = first_vert

for vert in to_del1: 
    succ[vert-1] = 999
    pre[vert-1] = 999 

# #insepect vertices to delete 
# print(f'k is {k}')
# print(route1, start1)
# print(to_del1)
# print(route2, start2)
# print(to_del2)


def add_all(seq):
    for i in seq: #can cause doubles if both vertices are already in the solution, but this doesn't cause problems 
        if i <= n: 
            seq = np.append(seq, i+n)
        else: 
            seq = np.append(seq, i-n)
    return seq


start_time = time.time()


# route1 = gen_route(sol, route1_idx)
# print(route1)
# print(start1)


print("--- %s seconds ---" % (time.time() - start_time))




    






# for i in range(1,len_route1-1): #no depots 
#     if start1 <= i < start1+k:

#         if i == start1: 
#             previous_idx = np.where(succ == vertex)
#             succ[previous_idx] = 999 #not -1 as it is the exact index 

#         vertex_old = vertex.copy()
#         vertex = succ[vertex-1]
#         succ[vertex_old-1] = 999





# print("OLD SUCC & PRE & RI")
# print(RI[route1_idx])
# print(succ)
# print(pre)

