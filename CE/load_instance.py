import pandas as pd 
import numpy as np

path = 'CE/data/a2-16.txt'

def load_instance(path):
    settings = pd.read_csv(path, sep=" ", header=None, nrows=1)

    K = settings.loc[0,0] #num vehicles 
    n = settings.loc[0,1] #num users 
    T = settings.loc[0,2] #max route duration 
    Q = settings.loc[0,3] #vehicle cap 
    L = settings.loc[0,4] #max user ride time 


    columns = ['id', 'x_coord', 'y_coord', 'service_time', 'cap', 'earliest_tw', 'latest_tw']
    vertices = pd.read_csv(path,  delim_whitespace=True, skiprows=1, header=None, names=columns)
    vertices.drop('id', axis=1, inplace=True)
    vertices = vertices.to_numpy()

    x_co = vertices[:,0]
    y_co = vertices[:,1]
    s = vertices[:,2]
    s = np.array(s, dtype=int)
    cap = vertices[:,3]
    cap = np.array(cap, dtype=int)
    e = vertices[:,4]
    e = np.array(e, dtype=int)
    l = vertices[:,5]
    l = np.array(l, dtype=int)
    
    #Here tighten time windows



    return K, n, T, Q, L, x_co, y_co, s, cap, e, l 


K, n, T, Q, L, x_co, y_co, s, cap, e, l  = load_instance(path)