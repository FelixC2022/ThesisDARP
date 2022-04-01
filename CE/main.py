from route_gen import *
from feasability import *

import numpy as np 

import time
start_time = time.time()

solution = []
unserved = get_unserved_solution(solution)

while len(unserved) != 0:
    route = np.array([ 0, 33], dtype=int) #np.array([0, 5, 5+n, 2*n+1], dtype=int)
    insertions_pos = get_insertions(route)
    feasible_users = get_feasible_users(route, insertions_pos, unserved)

    while len(feasible_users) != 0: 

        new_user = np.random.choice(feasible_users) #select from feasible users according to Pij, need to implement this 
        # Look for the best possible insertion and choose this one
        results = np.empty((len(insertions_pos), 3))

<<<<<<< HEAD
        shortest = np.inf
=======
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
>>>>>>> da59cb5a0508ab1bd908918cb4fe2c4ad2906dc4

        for i in range(len(insertions_pos)):
            new_route = gen_newroute(route, new_user, insertions_pos[i])
            check, B = eight_step(new_route)
            length = B[-1] - B[1]
            if check and length < shortest: 
                shortest = length
                route = new_route

        insertions_pos = get_insertions(route)
        unserved = np.delete(unserved, np.where(unserved == new_user))
        feasible_users = get_feasible_users(route, insertions_pos, unserved)

    solution.append([route, shortest])

cost = 0
for i in solution: 
    cost += i[1]
    print(i[0])

print(cost)


print("--- %s seconds ---" % (time.time() - start_time))
