from route_gen import *
from feasability import *

import numpy as np 

import time
from tqdm import tqdm

start_time = time.time()

#Generate N solutions 
N = 10
def gen_N_solutions(N):
    solutions_all = []
    for i in tqdm(range(N)):
        solution = gen_solution() 
        solutions_all.append(solution)
    return solutions_all

solutions_all = gen_N_solutions(N)

#Perform Local Search on the x best solution 

#Update the Pij matrix 



print("--- %s seconds ---" % (time.time() - start_time))
