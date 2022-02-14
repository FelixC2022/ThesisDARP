
import copy 
import numpy as np
from tqdm import tqdm
import pandas as pd
np.random.seed(123) #same random results (reproducable only for development)

#READING IN & PREPROCESSING INSTANCE DATA 

instance_dim = pd.read_csv('data/a15-120hetIUY.txt', sep=" ", header=None, nrows=1)
num_vehs=instance_dim.iat[0,0]
num_reqs= instance_dim.iat[0,1]

instance_vehicles= pd.read_csv('data/a15-120hetIUY.txt', sep=" ", header=None,skiprows=1, nrows=num_vehs) 


instance_vertices= pd.read_csv('data/a15-120hetIUY.txt', sep='\t', header=None,skiprows=num_vehs+1) 
instance_vertices.columns= ['id', 'x_coord', 'y_coord', 'service_time', 'max_ride_time', 'demand_resource_1', 'demand_resource_2', 'demand_resource_3', 'demand_resource_4', 'earliest_tw', 'latest_tw']
instance_vertices.drop('id', inplace=True, axis=1)
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

#Set for the game_result function  
best_score = np.inf
best_state = None 

#ADJUSTING THE DEPOTS COORDINATES FOR EACH VEHICLE 
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
    pre = state[0] #state[0] is succ array
    for i in range(num_reqs):
        if pre[i]==None:
            unserved_requests.append(i+1) #i+1 because the element with index i in succ corresponds to user vertex i+1!
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

def move(state, a):
    n=num_reqs
    succ=copy.deepcopy(state[0]) 
    pre=copy.deepcopy(state[1])
    RI=copy.deepcopy(state[2])
    earliest=copy.deepcopy(state[3])
    latest=copy.deepcopy(state[4])
    cap=copy.deepcopy(state[5])
    
    current_best = None
    current_best_score = np.inf
    
    #loop over vehicles/routes 
    vehicles = list(range(len(RI)))
    np.random.shuffle(vehicles) 

    for k in vehicles:
        if current_best != None: 
            break

        #k = np.random.choice(vehicles)
        valid1 = True
        #Checks whether empty vehicle has sufficient cap to serve customer 

        for r in R:
            if q[a][r]>Q[k][r]:
                valid1 = False
                break
        if valid1==False:
            continue
            
        #Constructs tour start_depot-user1-user2-...-end_depot
        tour=list()
        tour.append(0)
        if RI[k][0]!= None:
            vertex=RI[k][0]
            while vertex!= (241): #end_depot
                tour.append(vertex)
                vertex=succ[vertex-1]
            tour.append(241) #end_depot
        else: 
            tour.append(241)

        #looping through all possible insertion positions for pickup vertex a
        for i in range(1, len(tour)): 
            # #earliest_i is the local variable that will be updated incrementally.
            # if i==1:
            #     earliest_i = max(e[a], earliest[tour[i-1]] + s[tour[i-1]] + dist(k,a)) 
            #     #dist(k,a) to incorparate distance from depot 
            # else:
            #     earliest_i = max(e[a], earliest[tour[i-1]] + s[tour[i-1]] + t[tour[i-1]][a]) 

            earliest_i = max(e[a], earliest[tour[i-1]] + s[tour[i-1]] + dist(k,tour[i-1],a))

            if earliest_i > l[a]:
                break 
                
            cap_r = [0]*len(R) 
            valid2 = True
            for r in R:
                cap_r[r]= cap[r][tour[i-1]] + q[a][r]
                if cap_r[r] > Q[k][r]:
                    valid2 = False
                    break
            if valid2==False:
                continue #
            
            #Insertion of pickup immediately after delivery 
            #earliest_a_Plus_n = max(e[a+n], earliest_i + s[a] + t[a][a+n])
            earliest_a_Plus_n = max(e[a+n], earliest_i + s[a] + dist(k, a, a+n))

            if earliest_a_Plus_n > l[a+n]:
                break
                    
            # if tour[i]!= (2*num_reqs +1):
            #     earliest_succ_a = max(e[tour[i]], earliest_a_Plus_n + s[a+n] + t[a+n][tour[i]])

            # else:
            #     earliest_succ_a = max(e[tour[i]], earliest_a_Plus_n + s[a+n] + dist(k,a+n))

            earliest_succ_a = max(e[tour[i]], earliest_a_Plus_n + s[a+n] + dist(k, a+n, tour[i]))


            if earliest_succ_a <= latest[tour[i]]: #here <= instead of > !!!!


                costIncrease= compute_costincrease(k,a,tour,i,i) 
                if costIncrease < current_best_score:
                    current_best=copy.deepcopy([k,tour, i, i])#copy.deepcopy needed or not? FC: better safe than sorry...
                    current_best_score = costIncrease
                    
            #Now we will consider insertion positions for delivery vertex a+n later in the tour k under consideration
            for j in range(i+1, len(tour)): #NOTE: in case route k is empty, len([0,2n+1])=2 -> if i==1, this j loop will
                                            #not be executed and hence, the only insertion combination considered will be 
                                            #the one in which a is inserted right after start depot 0, and a+n directly 
                                            #after a, and hence right before artificial end depot 2n+1! Good!
                                            #ALSO NOTE: if tour[i]=2n+1, then the only option is to insert a+n directly
                                            #after a, and hence i+1>len(tour) and then this loop will also not be executed. 
                
                #TEST WHETHER FIRST VERTEX AFTER A (VERTEX I) CAN BE REACHED IN TIME                       
                #earliest_j= max(e[tour[i]], earliest_i + s[a] + t[a][tour[i]])
                earliest_j = max(e[tour[i]], earliest_i + s[a] + dist(k, a, tour[i]))  

                if earliest_j > l[tour[i]]:
                    break #if inserting j at position i+1 causes route[i] (the successor of pickup vertex a) not to be visited
                            #in time, inserting a+n at positions further in the tour will also violate the time windows of tour[i].
                
                #TEST WHETHER VEHICLE HAS SUFFICIENT CAP TO SERVICE FIRST VERTEX AFTER A (VERTEX I)                             
                cap_rj=[0]*len(R) #defining a new local array cap_rj so that local array cap_r can be reused for other insertion
                                    #positions of a+n.
                valid3=True
                for r in R:
                    cap_rj[r]= cap_r[r]+q[tour[i]][r] #i is now after a; cap_r includes cap utilization including vertex a 
                    if cap_rj[r] > Q[k][r]:
                        valid3=False
                        break
                if valid3==False:
                    break  
                                        
                #TEST TIME WINDOWS + CAP FOR OTHER VERTICES BETWEEN A AND A+N (EXCEPT THE FIRST ONE)                       
                for p in range(i+1, j):
                    # if tour[p]!=(2*num_reqs + 1):
                    #     earliest_j=max( e[tour[p]], earliest_j + s[tour[p-1]] + t[tour[p-1]][tour[p]])
                    #     #unnesecary as j can max be 2*n+1 and the end index is not included 
                    # else:
                    #     earliest_j=max( e[tour[p]], earliest_j + s[tour[p-1]] + dist(k, tour[p-1]))
                    
                    earliest_j=max( e[tour[p]], earliest_j + s[tour[p-1]] + dist(k, tour[p-1], tour[p]))  
                    
                    valid4 = True
                    if earliest_j > l[tour[p]]:
                        valid4=False
                        break 
                                        
                    for r in R:
                        cap_rj[r] += q[tour[p]][r]
                        if cap_rj[r]>Q[k][r]:
                            valid4=False
                            break
                    if valid4 == False:
                        break 
                
                                        
                #Now we will check the time window feasibility for vertex a+n and the vertex that comes after
                #a+n, i.e. the vertex (tour[j]) that is located at position j in the current partial tour k and 
                #that will be shifted to the right when inserting a+n at position j. Note
                #that, given that no capacity violations have occurred at the previous vertices between a and a+n,
                #there also won't be a capacity violation at vertex a+n and its successor, since at delivery vertex a+n, 
                #the additional load compared to the current partial solution (tour k) is unloaded at a+n
                                        
                #earliest_j = max(e[a+n], earliest_j + s[tour[j-1]] + t[tour[j-1]][a+n]) 
                #incremental update earliest for vertex  #a+n, if inserted at location j.

                earliest_j = max(e[a+n], earliest_j + s[tour[j-1]] + dist(k, tour[j-1],[a+n])) 

                if earliest_j > l[a+n]:
                    break
                                        
                # if tour[j]!=(2*num_reqs + 1):
                #     earliest_j = max(e[tour[j]], earliest_j + s[a+n] + t[a+n][tour[j]])

                # else:
                #     earliest_j = max(e[tour[j]], earliest_j + s[a+n] + dist(k,a+n))


                earliest_j = max(e[tour[j]], earliest_j + s[a+n] + dist(k, a+n, tour[j]))

                if earliest_j>latest[tour[j]]: #FC: why latest ??? 
                    break
                #note, latest is not a local variable but one of the variables stored in each
                #node of the search tree for each vertex.
                    
                                        
                #if we reached this line of the code, than it means that the insertion combination
                #of inserting user pickup vertex a at position i and user delivery vertex
                #a+n at position j, is valid with regard to capacity and time window constraints.
                #Hence, now we'll compute the cost increase and check whether it's the best insertion
                #for request a so far. 
                                        
                costIncrease = compute_costincrease(k,a,tour, i,j)
                if costIncrease < current_best_score:
                    current_best=copy.deepcopy([k, tour, i, j])#copy.deepcopy needed or not? 
                    current_best_score= costIncrease

    if current_best != None: 
        #May only go through if current_best != None (i.e. feasable insertion is found )
        succ_child=copy.deepcopy(succ)
        pre_child=copy.deepcopy(pre)
        RI_child=copy.deepcopy(RI)
        #current_best=[k, tour, i, j]
                                        
        k=current_best[0]
        tour=current_best[1]
        i=current_best[2]
        j=current_best[3]
        pre_child[a-1]=tour[i-1]
        succ_child[a+n-1]=tour[j]
                                        
        if tour[j]== (2*n + 1):
            RI_child[k][1]=a+n
        else:
            pre_child[tour[j]-1]=a+n
        if tour[i-1]==0:
            RI_child[k][0]=a
        else:
            succ_child[tour[i-1]-1]=a
        if i==j: #that's the case when a+n would be inserted DIRECTLY after a!
            pre_child[a+n-1]=a
            succ_child[a-1]=a+n
        else:
            pre_child[tour[i]-1]=a
            pre_child[a+n-1]=tour[j-1]
            succ_child[a-1]=tour[i]
            succ_child[tour[j-1]-1]=a+n

        #Now we are going to recompute earliest, latest and cap for the new (partial solution). earliest and cap are computed 
        #by a forward loop starting from vertex a, until the end of the route in which request a has been inserted. latest is 
        #computed by a backward loop, starting from vertex a+n, until the beginning of the route in which req. a has been inserted.

        #earliest_child=[None]*len(V)
        #latest_child=[None]*len(V)
        #cap_child=[[None for v in range(len(V))] for r in range(len(R))]#initializes a 2D list of |R| lists with length |V|
                                        
        earliest_child=copy.deepcopy(earliest)
        latest_child=copy.deepcopy(latest)
        cap_child=copy.deepcopy(cap)
                                        
        #earliest_child[a]=max(e[a],earliest[pre_child[a-1]] + s[pre_child[a-1]] + t[pre_child[a-1]][a]) 
        earliest_child[a]=max(e[a],earliest[pre_child[a-1]] + s[pre_child[a-1]] + dist(k,pre_child[a-1], a)) 
        #what if a is the first one in the route 
                                        
        for r in R: 
            cap_child[r][a]=cap[r][pre_child[a-1]] + q[a][r]
                                        
        #latest_child[a+n]=min(l[a+n], latest[succ_child[a+n-1]] - s[a+n] - t[a+n][succ_child[a+n-1]]) 
        latest_child[a+n]=min(l[a+n], latest[succ_child[a+n-1]] - s[a+n] - dist(k, a+n, succ_child[a+n-1])) 

        vtx1=a
        vtx2=a+n  

        while vtx1 != 2*n+1: #can be 2*n+1 (end_depot)
            vtx1 = succ_child[vtx1-1]
            if vtx1 != 2*n+1: 
                earliest_child[vtx1] = max(e[vtx1],earliest_child[pre_child[vtx1-1]] + s[pre_child[vtx1-1]] + dist(k, pre_child[vtx1-1],vtx1 ))

                for r in R: 
                    cap_child[r][vtx1] = cap[r][pre_child[vtx1-1]] + q[vtx1][r]
            else: 
                earliest_child[vtx1] = max(e[vtx1], earliest_child[RI_child[k][1]] + s[RI_child[k][1]] + dist(k, RI_child[k][1], vtx1))

                cap_child[r][vtx1] = cap[r][RI_child[k][1]] + q[vtx1][r]    
        
        while vtx2 != pre_child[RI_child[k][0]-1]:
            vtx2=pre_child[vtx2-1]
            if vtx2 != 0: #startdepot 
                latest_child[vtx2]=min(l[vtx2], latest_child[succ_child[vtx2-1]] - s[vtx2] - dist(k, vtx2, succ_child[vtx2-1]))

            else: #in case vtx2 has become the start depot 
                latest_child[vtx2] = min(l[vtx2], latest_child[RI_child[k][0]] - s[vtx2] - dist(k, vtx2 ,RI_child[k][0]))

        new_state = [succ_child, pre_child, RI_child, earliest_child, latest_child, cap_child]

    #Should go back and select a new action; 
    else:
        #print("Given the state and action no possible insertion found; old state is returned")
        return None

def initialize_state():
    succ1=[None]*(2*num_reqs)
    pre1=[None]*(2*num_reqs)
    RI1=[[None,None] for v in range(num_vehs)]
    earliest1=e
    latest1=l
    
    cap1=[[0 for i in range(2*num_reqs +2)] for r in range(len(R))]
    #FC: Cap needs to be first ressources then vertex, else algorithm breaks 
    
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

#CLASS FOR NODE 

class MonteCarloTreeSearchNode():
    def __init__(self, state, parent=None, parent_action=None):
        self.state= state 
        self.parent = parent 
        self.parent_action = parent_action 
        self.children = [] 
        self._number_of_visits = 0 
        self._results = 0 #make it the sum of scores according to eval. fct 8 step eval. scheme!; (Score of a node=results/number_of_visits)
            
        self._untried_actions = None 
        self._untried_actions = self.untried_actions()
        return

    def untried_actions(self):
        # self._untried_actions = get_legal_actions(self.state) 
        # return self._untried_actions
        actions = get_legal_actions(self.state) 
        np.random.shuffle(actions)
        self._untried_actions = actions
        return self._untried_actions
    
    def best_action(self):
        #sim_num a hyperparameter initialized when reading in all the global variables
        simulation_no = sim_num 
        for i in range(simulation_no):
            v = self._tree_policy() 
            reward = v.rollout()
            v.backpropagate(reward)
        return self.best_child(c_param=0.) 

    #Selects node to run rollout.
    def _tree_policy(self):

        current_node = self
        while not current_node.is_terminal_node():
        
            if not current_node.is_fully_expanded():
                return current_node.expand()#when a node is not fully expanded, it expands the node (expand method underneath)
                                        #and returns that newly expanded node as the node to start the rollout.
            else:
                current_node = current_node.best_child()#When a node is fully expanded, it keeps selecting the best_child according
                                                    #to the tree policy (function best_child()), until a node which is not
                                                    #fully expanded is reached. Then it adds a child and that will be the 
                                                    #node to start the rollout. 
        return current_node

    def is_terminal_node(self):
        return is_game_over(self.state)


    def is_fully_expanded(self):
        return len(self._untried_actions) == 0


    #Just do a full expansion, hence incorporate a while loop!! No works perfeclty without it!
    def expand(self):
        action = self._untried_actions.pop()#pop returns the element with the index stated between the brackets. Default = -1 ->
                                        #last element is returned. Once returned, it discards the element from the list!
        intermediary_state = move(self.state,action) 

        while intermediary_state == None: 
            action = self._untried_actions.pop()
            intermediary_state = move(self.state, action)

        next_state = intermediary_state

        child_node = MonteCarloTreeSearchNode(next_state, parent=self, parent_action=action)
        self.children.append(child_node)
        return child_node 
    #From the present state, next state is generated depending on the action which is carried out. In this step all the possible
    #child nodes corresponding to generated states are appended to the children array and the child_node is returned. The states
    #which are possible from the present state are all generated by initializing the child_node and the child_node corresponding
    #to this generated state is returned.

    #tree policy with UCB action selection, this balances exploration and exploitation. NOTE: c_param is a hyperparameter to tune. 
    #sqrt(2) (=1.41) is a good value to start with.
    def best_child(self, c_param=np.sqrt(2)):
        choices_weights = [(c._results)/(c._number_of_visits) + (c_param * np.sqrt((np.log(self._number_of_visits))/c._number_of_visits)) for c in self.children]
        return self.children[np.argmax(choices_weights)]

    #From the current state, entire solution is simulated till there are no more unserved requests.
    # If the entire game is randomly simulated, that is at each turn the move is randomly selected out of set of possible moves, 
    #it is called light playout. Hence next steps thesis could include rollouts that are not completely random!

    def rollout(self):
        
        valid_check = True 

        current_rollout_state=self.state
    
        while not is_game_over(current_rollout_state):
        
            possible_moves = get_legal_actions(current_rollout_state)
        
            action = self.rollout_policy(possible_moves)

            possible_moves.remove(action)

            intermediary_state = move(state=current_rollout_state, a=action)
    
            while intermediary_state == None: 
                if len(possible_moves)==0:
                    valid_check = False
                    break
                action = self.rollout_policy(possible_moves)
                possible_moves.remove(action)
                intermediary_state = move(current_rollout_state, action)

            current_rollout_state = intermediary_state

            if valid_check == False: 
                break #removed actions in the code above will not be included in a final solution of the rollout

        #if rollout is totally blocked and no possible insertion is found 
        if current_rollout_state == None:
            return 0     
    
        return game_result(current_rollout_state)
    
    def rollout_policy(self, possible_moves):
    
        return possible_moves[np.random.randint(len(possible_moves))]
    #Randomly selects a move out of possible moves. This is an example of random playout.

    def backpropagate(self, result):
        self._number_of_visits += 1
        self._results += result
        if self.parent:
            self.parent.backpropagate(result)


if __name__ == '__main__': 
    #GENERATING THE ROOT STATE 
    #state=[suc,pre,RI,earliest,latest,cap]
    def initialize_state():
        succ1=[None]*(2*num_reqs)
        pre1=[None]*(2*num_reqs)
        RI1=[[None,None] for v in range(num_vehs)]
        earliest1=e
        latest1=l
        
        cap1=[[0 for i in range(2*num_reqs +2)] for r in range(len(R))]#initializes a 2D list of |R| lists with length |V|
        #FC: Cap needs to be first ressources then vertex, else algorithm breaks 
        
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

    sim_num = 1 #set 

    state_root = initialize_state()

    node_root = MonteCarloTreeSearchNode(state_root)

    current_node = node_root
    for i in tqdm(range(num_reqs)):
        current_node=current_node.best_action()

    cost_solution= length_total(current_node.state)

    print([current_node.state[0], current_node.state[1], current_node.state[2]]) #
    print('\n')
    print(cost_solution)
    print('\n')
    print(is_game_over(current_node.state))

    #print(length_total(selected_node.state))                                                 
    #print(is_game_over(selected_node.state))

           