# import copy 
# import numpy as np 

# # from utils import num_vehs, num_reqs, route_duration, Q, x_co, y_co, s, L, q, e, l, R, dist, compute_costincrease
# from utils import *

# def move(state, a):
#     n=num_reqs
#     succ=copy.deepcopy(state[0]) 
#     pre=copy.deepcopy(state[1])
#     RI=copy.deepcopy(state[2])
#     earliest=copy.deepcopy(state[3])
#     latest=copy.deepcopy(state[4])
#     cap=copy.deepcopy(state[5])
    
#     current_best = None
#     current_best_score = np.inf
    
#     #loop over vehicles/routes 
#     vehicles = list(range(len(RI)))
#     np.random.shuffle(vehicles) 

#     for k in vehicles:
#         if current_best != None: 
#             break

#         valid1 = True
#         #Checks whether empty vehicle has sufficient cap to serve customer 
#         for r in R:
#             if q[a][r]>Q[k][r]:
#                 valid1 = False
#                 break
#         if valid1==False:
#             continue
            
#         #Constructs tour start_depot-user1-user2-...-end_depot
#         tour=list()
#         tour.append(0)
#         if RI[k][0]!= None:
#             vertex=RI[k][0]
#             while vertex!= (241): #end_depot
#                 tour.append(vertex)
#                 vertex=succ[vertex-1]
#             tour.append(241) #end_depot
#         else: 
#             tour.append(241)

#         #looping through all possible insertion positions for pickup vertex a
#         for i in range(1, len(tour)): 
#             # #earliest_i is the local variable that will be updated incrementally.
#             # if i==1:
#             #     earliest_i = max(e[a], earliest[tour[i-1]] + s[tour[i-1]] + dist(k,a)) 
#             #     #dist(k,a) to incorparate distance from depot 
#             # else:
#             #     earliest_i = max(e[a], earliest[tour[i-1]] + s[tour[i-1]] + t[tour[i-1]][a]) 

#             earliest_i = max(e[a], earliest[tour[i-1]] + s[tour[i-1]] + dist(k,tour[i-1],a))

#             if earliest_i > l[a]:
#                 break 
                
#             cap_r = [0]*len(R) 
#             valid2 = True
#             for r in R:
#                 cap_r[r]= cap[r][tour[i-1]] + q[a][r]
#                 if cap_r[r] > Q[k][r]:
#                     valid2 = False
#                     break
#             if valid2==False:
#                 continue #
            
#             #Insertion of pickup immediately after delivery 
#             #earliest_a_Plus_n = max(e[a+n], earliest_i + s[a] + t[a][a+n])
#             earliest_a_Plus_n = max(e[a+n], earliest_i + s[a] + dist(k, a, a+n))

#             if earliest_a_Plus_n > l[a+n]:
#                 break
                    
#             # if tour[i]!= (2*num_reqs +1):
#             #     earliest_succ_a = max(e[tour[i]], earliest_a_Plus_n + s[a+n] + t[a+n][tour[i]])

#             # else:
#             #     earliest_succ_a = max(e[tour[i]], earliest_a_Plus_n + s[a+n] + dist(k,a+n))

#             earliest_succ_a = max(e[tour[i]], earliest_a_Plus_n + s[a+n] + dist(k, a+n, tour[i]))


#             if earliest_succ_a <= latest[tour[i]]: #here <= instead of > !!!!


#                 costIncrease= compute_costincrease(k,a,tour,i,i) 
#                 if costIncrease < current_best_score:
#                     current_best=copy.deepcopy([k,tour, i, i])#copy.deepcopy needed or not? FC: better safe than sorry...
#                     current_best_score = costIncrease
                    
#             #Now we will consider insertion positions for delivery vertex a+n later in the tour k under consideration
#             for j in range(i+1, len(tour)): #NOTE: in case route k is empty, len([0,2n+1])=2 -> if i==1, this j loop will
#                                             #not be executed and hence, the only insertion combination considered will be 
#                                             #the one in which a is inserted right after start depot 0, and a+n directly 
#                                             #after a, and hence right before artificial end depot 2n+1! Good!
#                                             #ALSO NOTE: if tour[i]=2n+1, then the only option is to insert a+n directly
#                                             #after a, and hence i+1>len(tour) and then this loop will also not be executed. 
                
#                 #TEST WHETHER FIRST VERTEX AFTER A (VERTEX I) CAN BE REACHED IN TIME                       
#                 #earliest_j= max(e[tour[i]], earliest_i + s[a] + t[a][tour[i]])
#                 earliest_j = max(e[tour[i]], earliest_i + s[a] + dist(k, a, tour[i]))  

#                 if earliest_j > l[tour[i]]:
#                     break #if inserting j at position i+1 causes route[i] (the successor of pickup vertex a) not to be visited
#                             #in time, inserting a+n at positions further in the tour will also violate the time windows of tour[i].
                
#                 #TEST WHETHER VEHICLE HAS SUFFICIENT CAP TO SERVICE FIRST VERTEX AFTER A (VERTEX I)                             
#                 cap_rj=[0]*len(R) #defining a new local array cap_rj so that local array cap_r can be reused for other insertion
#                                     #positions of a+n.
#                 valid3=True
#                 for r in R:
#                     cap_rj[r]= cap_r[r]+q[tour[i]][r] #i is now after a; cap_r includes cap utilization including vertex a 
#                     if cap_rj[r] > Q[k][r]:
#                         valid3=False
#                         break
#                 if valid3==False:
#                     break  
                                        
#                 #TEST TIME WINDOWS + CAP FOR OTHER VERTICES BETWEEN A AND A+N (EXCEPT THE FIRST ONE)                       
#                 for p in range(i+1, j):
#                     # if tour[p]!=(2*num_reqs + 1):
#                     #     earliest_j=max( e[tour[p]], earliest_j + s[tour[p-1]] + t[tour[p-1]][tour[p]])
#                     #     #unnesecary as j can max be 2*n+1 and the end index is not included 
#                     # else:
#                     #     earliest_j=max( e[tour[p]], earliest_j + s[tour[p-1]] + dist(k, tour[p-1]))
                    
#                     earliest_j=max( e[tour[p]], earliest_j + s[tour[p-1]] + dist(k, tour[p-1], tour[p]))  
                    
#                     valid4 = True
#                     if earliest_j > l[tour[p]]:
#                         valid4=False
#                         break 
                                        
#                     for r in R:
#                         cap_rj[r] += q[tour[p]][r]
#                         if cap_rj[r]>Q[k][r]:
#                             valid4=False
#                             break
#                     if valid4 == False:
#                         break 
                
                                        
#                 #Now we will check the time window feasibility for vertex a+n and the vertex that comes after
#                 #a+n, i.e. the vertex (tour[j]) that is located at position j in the current partial tour k and 
#                 #that will be shifted to the right when inserting a+n at position j. Note
#                 #that, given that no capacity violations have occurred at the previous vertices between a and a+n,
#                 #there also won't be a capacity violation at vertex a+n and its successor, since at delivery vertex a+n, 
#                 #the additional load compared to the current partial solution (tour k) is unloaded at a+n
                                        
#                 #earliest_j = max(e[a+n], earliest_j + s[tour[j-1]] + t[tour[j-1]][a+n]) 
#                 #incremental update earliest for vertex  #a+n, if inserted at location j.

#                 earliest_j = max(e[a+n], earliest_j + s[tour[j-1]] + dist(k, tour[j-1],[a+n])) 

#                 if earliest_j > l[a+n]:
#                     break
                                        
#                 # if tour[j]!=(2*num_reqs + 1):
#                 #     earliest_j = max(e[tour[j]], earliest_j + s[a+n] + t[a+n][tour[j]])

#                 # else:
#                 #     earliest_j = max(e[tour[j]], earliest_j + s[a+n] + dist(k,a+n))


#                 earliest_j = max(e[tour[j]], earliest_j + s[a+n] + dist(k, a+n, tour[j]))

#                 if earliest_j>latest[tour[j]]: #FC: why latest ??? 
#                     break
#                 #note, latest is not a local variable but one of the variables stored in each
#                 #node of the search tree for each vertex.
                    
                                        
#                 #if we reached this line of the code, than it means that the insertion combination
#                 #of inserting user pickup vertex a at position i and user delivery vertex
#                 #a+n at position j, is valid with regard to capacity and time window constraints.
#                 #Hence, now we'll compute the cost increase and check whether it's the best insertion
#                 #for request a so far. 
                                        
#                 costIncrease = compute_costincrease(k,a,tour, i,j)
#                 if costIncrease < current_best_score:
#                     current_best=copy.deepcopy([k, tour, i, j])#copy.deepcopy needed or not? 
#                     current_best_score= costIncrease

#     if current_best != None: 
#         #May only go through if current_best != None (i.e. feasable insertion is found )
#         succ_child=copy.deepcopy(succ)
#         pre_child=copy.deepcopy(pre)
#         RI_child=copy.deepcopy(RI)
#         #current_best=[k, tour, i, j]
                                        
#         k=current_best[0]
#         tour=current_best[1]
#         i=current_best[2]
#         j=current_best[3]
#         pre_child[a-1]=tour[i-1]
#         succ_child[a+n-1]=tour[j]
                                        
#         if tour[j]== (2*n + 1):
#             RI_child[k][1]=a+n
#         else:
#             pre_child[tour[j]-1]=a+n
#         if tour[i-1]==0:
#             RI_child[k][0]=a
#         else:
#             succ_child[tour[i-1]-1]=a
#         if i==j: #that's the case when a+n would be inserted DIRECTLY after a!
#             pre_child[a+n-1]=a
#             succ_child[a-1]=a+n
#         else:
#             pre_child[tour[i]-1]=a
#             pre_child[a+n-1]=tour[j-1]
#             succ_child[a-1]=tour[i]
#             succ_child[tour[j-1]-1]=a+n

#         #Now we are going to recompute earliest, latest and cap for the new (partial solution). earliest and cap are computed 
#         #by a forward loop starting from vertex a, until the end of the route in which request a has been inserted. latest is 
#         #computed by a backward loop, starting from vertex a+n, until the beginning of the route in which req. a has been inserted.

#         #earliest_child=[None]*len(V)
#         #latest_child=[None]*len(V)
#         #cap_child=[[None for v in range(len(V))] for r in range(len(R))]#initializes a 2D list of |R| lists with length |V|
                                        
#         earliest_child=copy.deepcopy(earliest)
#         latest_child=copy.deepcopy(latest)
#         cap_child=copy.deepcopy(cap)
                                        
#         #earliest_child[a]=max(e[a],earliest[pre_child[a-1]] + s[pre_child[a-1]] + t[pre_child[a-1]][a]) 
#         earliest_child[a]=max(e[a],earliest[pre_child[a-1]] + s[pre_child[a-1]] + dist(k,pre_child[a-1], a)) 
#         #what if a is the first one in the route 
                                        
#         for r in R: 
#             cap_child[r][a]=cap[r][pre_child[a-1]] + q[a][r]
                                        
#         #latest_child[a+n]=min(l[a+n], latest[succ_child[a+n-1]] - s[a+n] - t[a+n][succ_child[a+n-1]]) 
#         latest_child[a+n]=min(l[a+n], latest[succ_child[a+n-1]] - s[a+n] - dist(k, a+n, succ_child[a+n-1])) 

#         vtx1=a
#         vtx2=a+n  

#         while vtx1 != 2*n+1: #can be 2*n+1 (end_depot)
#             vtx1 = succ_child[vtx1-1]
#             if vtx1 != 2*n+1: 
#                 earliest_child[vtx1] = max(e[vtx1],earliest_child[pre_child[vtx1-1]] + s[pre_child[vtx1-1]] + dist(k, pre_child[vtx1-1],vtx1 ))

#                 for r in R: 
#                     cap_child[r][vtx1] = cap[r][pre_child[vtx1-1]] + q[vtx1][r]
#             else: 
#                 earliest_child[vtx1] = max(e[vtx1], earliest_child[RI_child[k][1]] + s[RI_child[k][1]] + dist(k, RI_child[k][1], vtx1))

#                 cap_child[r][vtx1] = cap[r][RI_child[k][1]] + q[vtx1][r]    
        
#         while vtx2 != pre_child[RI_child[k][0]-1]:
#             vtx2=pre_child[vtx2-1]
#             if vtx2 != 0: #startdepot 
#                 latest_child[vtx2]=min(l[vtx2], latest_child[succ_child[vtx2-1]] - s[vtx2] - dist(k, vtx2, succ_child[vtx2-1]))

#             else: #in case vtx2 has become the start depot 
#                 latest_child[vtx2] = min(l[vtx2], latest_child[RI_child[k][0]] - s[vtx2] - dist(k, vtx2 ,RI_child[k][0]))

#         new_state = [succ_child, pre_child, RI_child, earliest_child, latest_child, cap_child]
#         return new_state

#     #Should go back and select a new action; 
#     else:
#         #print("Given the state and action no possible insertion found; old state is returned")
#         return None

# def move_allroutes(state, a):
#     n=num_reqs
#     succ=copy.deepcopy(state[0]) 
#     pre=copy.deepcopy(state[1])
#     RI=copy.deepcopy(state[2])
#     earliest=copy.deepcopy(state[3])
#     latest=copy.deepcopy(state[4])
#     cap=copy.deepcopy(state[5])
#     current_best = [0,[0],0,0] 
#     # index 0: vehicle; index1: tour as list; index2: i index pickup vertex; index2: j index delivery verex
#     current_best_score = np.inf 


#     # initialization that keeps indices of the 3 main loops referring to the insertion   
#     # combination that is currently the best one. (1st index for the vehicle/route 
#     # number, 2nd index for the insertion position of vertex a, 3rd index for the 
#     # insertion position of index a+n in the current solution.)
    
    
#     #loop over vehicles/routes 
#     vehicles = list(range(len(RI)))
#     for k in vehicles:
#         valid1 = True
        
#         #Checks whether empty vehicle has sufficient cap to serve customer 
#         for r in R:
#             if q[a][r]>Q[k][r]:
#                 valid1 = False
#                 break
#         if valid1==False:
#             continue
            
#         #Constructs tour start_depot-user1-user2-...-end_depot
#         tour=list()
#         tour.append(0)
#         if RI[k][0]!= None:
#             vertex=RI[k][0]
#             while vertex!= (2*n + 1):
#                 tour.append(vertex)
#                 vertex=succ[vertex-1]
#         tour.append(2*n + 1) 
        

#         #looping through all possible insertion positions for pickup vertex a
#         for i in range(1, len(tour)): 
            
#             # #earliest_i is the local variable that will be updated incrementally.
#             # if i==1:
#             #     earliest_i = max(e[a], earliest[tour[i-1]] + s[tour[i-1]] + dist(k,a)) 
#             #     #dist(k,a) to incorparate distance from depot 
#             # else:
#             #     earliest_i = max(e[a], earliest[tour[i-1]] + s[tour[i-1]] + t[tour[i-1]][a]) 

#             earliest_i = max(e[a], earliest[tour[i-1]] + s[tour[i-1]] + dist(k, tour[i-1], a))
               
#             if earliest_i > l[a]:
#                 break 
                
#             cap_r = [0]*len(R) 
#             valid2 = True
#             for r in R:
#                 cap_r[r]= cap[r][tour[i-1]] + q[a][r]
#                 if cap_r[r] > Q[k][r]:
#                     valid2 = False
#                     break
#             if valid2==False:
#                 continue 
           
#             #Insertion of pickup immediately after delivery 

#             #earliest_a_Plus_n = max(e[a+n], earliest_i + s[a] + t[a][a+n])
#             earliest_a_Plus_n = max(e[a+n], earliest_i + s[a] + dist(k, a, a+n))
#             if earliest_a_Plus_n > l[a+n]:
#                 break
                    
#             # if tour[i]!= (2*num_reqs +1):
#             #     earliest_succ_a = max(e[tour[i]], earliest_a_Plus_n + s[a+n] + t[a+n][tour[i]])

#             # else:
#             #     earliest_succ_a = max(e[tour[i]], earliest_a_Plus_n + s[a+n] + dist(k,a+n))
#             #     #if tour[i] is equal to the end depot 2n+1, then we should call the dist function.
                                      
#             earliest_succ_a = max(e[tour[i]], earliest_a_Plus_n + s[a+n] + dist(k, a+n, tour[i]))

#             if earliest_succ_a <= latest[tour[i]]: #here <= instead of > !!!!
                                      
#                 #Here I don't think it's necessary to break, because a time window
#                 #violation at the vertex after a+n when positioning a+n directly after a, might
#                 # be resolved when positioning a+n somewhere after this vertex because in that
#                 #case the vehicle only needs to visit a, instead of a and a+n, before visting that vertex.
                                                                            
#                 costIncrease= compute_costincrease(k,a,tour,i,i) #j should be i as j is not yet declared!!! (2nd index was j)
#                 if costIncrease < current_best_score:
#                     current_best=copy.deepcopy([k,tour, i, i])#copy.deepcopy needed or not? FC: better safe than sorry...
#                     current_best_score= costIncrease
                    
#             #Now we will consider insertion positions for delivery vertex a+n later in the tour k under consideration
#             for j in range(i+1, len(tour)): #NOTE: in case route k is empty, len([0,2n+1])=2 -> if i==1, this j loop will
#                                             #not be executed and hence, the only insertion combination considered will be 
#                                             #the one in which a is inserted right after start depot 0, and a+n directly 
#                                             #after a, and hence right before artificial end depot 2n+1! Good!
#                                             #ALSO NOTE: if tour[i]=2n+1, then the only option is to insert a+n directly
#                                             #after a, and hence i+1>len(tour) and then this loop will also not be executed. 

                
#                 #TEST WHETHER FIRST VERTEX AFTER A (VERTEX I) CAN BE REACHED IN TIME                       
#                 #earliest_j= max(e[tour[i]], earliest_i + s[a] + t[a][tour[i]])
#                 earliest_j= max(e[tour[i]], earliest_i + s[a] + dist(k, a, tour[i]))

#                 #tour[i] cannot be 2n+1, otherwise j-loop not executed; else we would need the dist func 
#                 if earliest_j > l[tour[i]]:
#                     break #if inserting j at position i+1 causes route[i] (the successor of pickup vertex a) not to be visited
#                           #in time, inserting a+n at positions further in the tour will also violate the time windows of tour[i].
                
#                 #TEST WHETHER VEHICLE HAS SUFFICIENT CAP TO SERVICE FIRST VERTEX AFTER A (VERTEX I)                             
#                 cap_rj=[0]*len(R) #defining a new local array cap_rj so that local array cap_r can be reused for other insertion
#                                   #positions of a+n.
#                 valid3=True
#                 for r in R:
#                     cap_rj[r]= cap_r[r]+q[tour[i]][r] #i is now after a; cap_r includes cap utilization including vertex a 
#                     if cap_rj[r] > Q[k][r]:
#                         valid3=False
#                         break
#                 if valid3==False:
#                     break  
                                      
#                 #TEST TIME WINDOWS + CAP FOR OTHER VERTICES BETWEEN A AND A+N (EXCEPT THE FIRST ONE)                       
#                 for p in range(i+1, j):
#                     # if tour[p]!=(2*num_reqs + 1):
#                     #     earliest_j = max( e[tour[p]], earliest_j + s[tour[p-1]] + t[tour[p-1]][tour[p]])
#                     #     #unnesecary as j can max be 2*n+1 and the end index is not included 
#                     # else:
#                     #     earliest_j= max( e[tour[p]], earliest_j + s[tour[p-1]] + dist(k, tour[p-1]))
                    
#                     earliest_j = max( e[tour[p]], earliest_j + s[tour[p-1]] + dist(k, tour[p-1], tour[p]))
                    
#                     valid4 = True
#                     if earliest_j > l[tour[p]]:
#                         valid4=False
#                         break 
                                      
#                     for r in R:
#                         cap_rj[r] += q[tour[p]][r]
#                         if cap_rj[r]>Q[k][r]:
#                             valid4=False
#                             break
#                     if valid4 == False:
#                         break 
              
                                      
#                 #Now we will check the time window feasibility for vertex a+n and the vertex that comes after
#                 #a+n, i.e. the vertex (tour[j]) that is located at position j in the current partial tour k and 
#                 #that will be shifted to the right when inserting a+n at position j. Note
#                 #that, given that no capacity violations have occurred at the previous vertices between a and a+n,
#                 #there also won't be a capacity violation at vertex a+n and its successor, since at delivery vertex a+n, 
#                 #the additional load compared to the current partial solution (tour k) is unloaded at a+n
                                      
#                 #earliest_j = max(e[a+n], earliest_j + s[tour[j-1]] + t[tour[j-1]][a+n]) 
#                 #incremental update earliest for vertex; a+n, if inserted at location j.

#                 earliest_j = max(e[a+n], earliest_j + s[tour[j-1]] + dist(k, tour[j-1], a+n))
#                 if earliest_j > l[a+n]:
#                     break
                                      
#                 # if tour[j]!=(2*num_reqs + 1):
#                 #     earliest_j = max(e[tour[j]], earliest_j + s[a+n] + t[a+n][tour[j]])
#                 # else:
#                 #     earliest_j = max(e[tour[j]], earliest_j + s[a+n] + dist(k,a+n))

#                 earliest_j = max(e[tour[j]], earliest_j + s[a+n] + dist(k,a+n, tour[j]))
#                 if earliest_j>latest[tour[j]]: #FC: why latest ??? 
#                     break
#                 #note, latest is not a local variable but one of the variables stored in each
#                 #node of the search tree for each vertex.
                    
                                      
#                 #if we reached this line of the code, than it means that the insertion combination
#                 #of inserting user pickup vertex a at position i and user delivery vertex
#                 #a+n at position j, is valid with regard to capacity and time window constraints.
#                 #Hence, now we'll compute the cost increase and check whether it's the best insertion
#                 #for request a so far. 
                                      
#                 costIncrease = compute_costincrease(k,a,tour, i,j)
#                 if costIncrease < current_best_score:
#                     current_best=copy.deepcopy([k, tour, i, j])#copy.deepcopy needed or not? 
#                     current_best_score= costIncrease

#     succ_child=copy.deepcopy(succ)
#     pre_child=copy.deepcopy(pre)
#     RI_child=copy.deepcopy(RI)
#     #current_best=[k, tour, i, j]
                                      
#     k=current_best[0]
#     tour=current_best[1]
#     i=current_best[2]
#     j=current_best[3]
#     pre_child[a-1]=tour[i-1]
#     succ_child[a+n-1]=tour[j]
                                     
#     if tour[j]== (2*n + 1):
#         RI_child[k][1]=a+n
#     else:
#         pre_child[tour[j]-1]=a+n
#     if tour[i-1]==0:
#         RI_child[k][0]=a
#     else:
#         succ_child[tour[i-1]-1]=a
#     if i==j: #that's the case when a+n would be inserted DIRECTLY after a!
#         pre_child[a+n-1]=a
#         succ_child[a-1]=a+n
#     else:
#         pre_child[tour[i]-1]=a
#         pre_child[a+n-1]=tour[j-1]
#         succ_child[a-1]=tour[i]
#         succ_child[tour[j-1]-1]=a+n

#     #Now we are going to recompute earliest, latest and cap for the new (partial solution). earliest and cap are computed 
#     #by a forward loop starting from vertex a, until the end of the route in which request a has been inserted. latest is 
#     #computed by a backward loop, starting from vertex a+n, until the beginning of the route in which req. a has been inserted.

#     #earliest_child=[None]*len(V)
#     #latest_child=[None]*len(V)
#     #cap_child=[[None for v in range(len(V))] for r in range(len(R))]#initializes a 2D list of |R| lists with length |V|
                                      
#     earliest_child=copy.deepcopy(earliest)
#     latest_child=copy.deepcopy(latest)
#     cap_child=copy.deepcopy(cap)
                                      
#     #earliest_child[a]=max(e[a],earliest[pre_child[a-1]] + s[pre_child[a-1]] + t[pre_child[a-1]][a]) 
#     earliest_child[a]=max(e[a],earliest[pre_child[a-1]] + s[pre_child[a-1]] + dist(k, a-1, a))
                                      
#     for r in R: 
#         cap_child[r][a]=cap[r][pre_child[a-1]] + q[a][r]
                                      
#     #latest_child[a+n]=min(l[a+n], latest[succ_child[a+n-1]] - s[a+n] - t[a+n][succ_child[a+n-1]]) 
#     latest_child[a+n]=min(l[a+n], latest[succ_child[a+n-1]] - s[a+n] - dist(k,a+n, succ_child[a+n-1]))

#     vtx1=a
#     vtx2=a+n  

#     while vtx1 != 2*n+1: #can be 2*n+1 (end_depot)
#         vtx1 = succ_child[vtx1-1]
#         if vtx1 != 2*n+1: 
#             earliest_child[vtx1] = max(e[vtx1],earliest_child[pre_child[vtx1-1]] + s[pre_child[vtx1-1]] + dist(k, pre_child[vtx1-1],vtx1 ))

#             for r in R: 
#                 cap_child[r][vtx1] = cap[r][pre_child[vtx1-1]] + q[vtx1][r]
#         else: 
#             earliest_child[vtx1] = max(e[vtx1], earliest_child[RI_child[k][1]] + s[RI_child[k][1]] + dist(k, RI_child[k][1], vtx1))

#             cap_child[r][vtx1] = cap[r][RI_child[k][1]] + q[vtx1][r]    
    
#     while vtx2 != pre_child[RI_child[k][0]-1]:
#         vtx2=pre_child[vtx2-1]
#         if vtx2 != 0: #startdepot 
#             latest_child[vtx2]=min(l[vtx2], latest_child[succ_child[vtx2-1]] - s[vtx2] - dist(k, vtx2, succ_child[vtx2-1]))

#         else: #in case vtx2 has become the start depot 
#             latest_child[vtx2] = min(l[vtx2], latest_child[RI_child[k][0]] - s[vtx2] - dist(k, vtx2 ,RI_child[k][0]))

#     new_state= [succ_child, pre_child, RI_child, earliest_child, latest_child, cap_child]
                                      
#     return new_state

#     #GENERATING THE ROOT STATE 
#     #state=[suc,pre,RI,earliest,latest,cap]