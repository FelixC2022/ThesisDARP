import numpy as np
import pandas as pd


def load_data(path): 
    instance_dim = pd.read_csv(path, sep=" ", header=None, nrows=1)
    num_vehs=instance_dim.iat[0,0]
    num_reqs= instance_dim.iat[0,1]

    instance_vertices= pd.read_csv(path, sep='\t', header=None,skiprows=num_vehs+1) 
    instance_vertices.columns= ['id', 'x_coord', 'y_coord', 'service_time', 'max_ride_time', 'demand_resource_1', 'demand_resource_2', 'demand_resource_3', 'demand_resource_4', 'earliest_tw', 'latest_tw']
    instance_vertices.drop('id', inplace=True, axis=1)
    
    instance_vehicles= pd.read_csv(path, sep=" ", header=None,skiprows=1, nrows=num_vehs) 
    instance_vehicles.columns=['route_duration', 'capacity_resource_1', 'capacity_resource_2', 'capacity_resource_3', 'capacity_resource_4']

    instance_vehicles2=instance_vehicles.to_numpy()
    route_duration= instance_vehicles2[:,0]  
    Q=instance_vehicles2[:,1:5] 

    instance_vertices2= instance_vertices.to_numpy()
    x_co=instance_vertices2[:,0] 
    y_co=instance_vertices2[:,1] 
    s= instance_vertices2[:,2] 
    L=instance_vertices2[:,3] 
    q=instance_vertices2[:,4:8] 
    e=instance_vertices2[:,8] 
    l=instance_vertices2[:,9] 
    R = [0,1,2,3] 

    return num_vehs, num_reqs, route_duration, Q, x_co, y_co, s, L, q, e, l, R


def get_depot_co(num_vehs):
    depot_co = np.zeros((num_vehs,2))

    depots = {
        0 : [-5,-5],
        1 : [5,5],
        2 : [-5,5],
        3 : [5,-5],
    }

    counter = 0
    for i in range(num_vehs):
        if counter < len(depots):
            depot_co[i]=depots[counter]
            counter += 1
        else: 
            counter = 0
            depot_co[i] = depots[counter]
        counter += 1
    
    return depot_co