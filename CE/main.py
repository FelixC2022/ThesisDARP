from route_gen import *
from feasability import *

import numpy as np 

users = np.arange(1,n+1)

route = np.array([0, 5, 5+n, 2*n+1], dtype=int)

insertions_pos = get_insertions(route)
feasible_users = get_feasible_users(route, insertions_pos)

print(feasible_users) #[ 3  4  9 11 13 14 15 16]

new_user = 11 #select from feasible users according to Pij, need to implement this 

#Look for the best possible insertion and choose this one 
print(insertions_pos)
for i in range(len(insertions_pos)):
    results = []
    new_route = gen_newroute(route, new_user, insertions_pos[i])
    check, B = eight_step(route)
    print(B)
    check, B = eight_step(new_route)
    print(B)
    length = B[-1] - B[1]
    results.append([new_route, check, length])

#Somthing goes wrong here. If you change new_user the B' arrays seem to stay the same which is weird... maybe this has something to do with pointers in memory... 