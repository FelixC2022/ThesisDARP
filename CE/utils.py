import numpy as np 

#Helper function 
def distance(i,j): 
    return np.linalg.norm((np.array((x_co[i],y_co[i])) - (np.array((x_co[j],y_co[j])))))  


dist = np.full((2*n+2,2*n+2), np.inf) #2n+2 because 2n users and 2 depots
for i in range(2*n+2):  #we could avoid some computations still. However, I think the effect will be minimal 
    for j in range(2*n+2): 
        dist[i,j] = distance(i, j)

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