from load_instnace import load_instance

path = 'data/a2-16.txt'
K, n, T, Q, L, x_co, y_co, s, cap, e, l  = load_instance(path)


#In total there are 16 users which need to be served 
route = [0, 1, 2, 1+n, 2+n, 2*n+1]

print(route,n)