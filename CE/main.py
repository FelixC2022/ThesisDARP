from route_gen import *
from feasability import *

import numpy as np 

import time

start_time = time.time()

#Generate N solutions 
N = 40
solutions_all = gen_N_solutions(N)

minimal = np.inf
for solution in solutions_all:
    cost = length_solution(solution)
    if cost < minimal:
        minimal = cost
        best = solution

print(best)
print(minimal)

#Perform Local Search on the x best solution 

#Update the Pij matrix 


print("--- %s seconds ---" % (time.time() - start_time))
