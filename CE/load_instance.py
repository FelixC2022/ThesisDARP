import pandas as pd 
import numpy as np

path = 'CE/data/a2-16.txt'


#@@@@@@@@@@@@@@@@@@ LOAD INSTANCE DATA #@@@@@@@@@@@@@@@@@@

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

    return K, n, T, Q, L, x_co, y_co, s, cap, e, l 

K, n, T, Q, L, x_co, y_co, s, cap, e, l  = load_instance(path)


#@@@@@@@@@@@@@@@@@@ DISTANCES #@@@@@@@@@@@@@@@@@@
def distance(i,j): 
    return np.linalg.norm((np.array((x_co[i],y_co[i])) - (np.array((x_co[j],y_co[j])))))  


dist = np.full((2*n+2,2*n+2), np.inf) #2n+2 because 2n users and 2 depots
for i in range(2*n+2):  #we could avoid some computations still. However, I think the effect will be minimal 
    for j in range(2*n+2): 
        dist[i,j] = distance(i, j)


#@@@@@@@@@@@@@@@@@@ Tighten time windows #@@@@@@@@@@@@@@@@@@
H = 1440 #lenght planning horizon 
for vert in range(2*n+1): #last index not included so +1 
    if l[vert] - e[vert] == H: #tw is not tight 
        #outbound request
        if vert <= n:
            e[vert] = max(0, e[vert+n]-L-s[vert])
            l[vert] = min(l[vert+n]-dist[vert,vert+n]-s[vert], H)
        #inbound request 
        else: 
            e[vert] = e[vert-n] + s[vert-n] + dist[vert-n, vert]
            l[vert] = min(l[vert-n]+s[vert-n]+L, H)