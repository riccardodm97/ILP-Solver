import numpy as np
import math 
from lib.temp  import Problem_data, Support_data


#ritorna gli indici delle colonne che formano una base da cui partire
def find_initial_basis(A):
    
    base_indexes = []
    id_matrix = np.identity(A.shape[0])
    for col in id_matrix:
        idx = np.where((A.T == col).all(axis=1))
        base_indexes.append(idx[0][0] if len(idx[0])>0 else -1)
    return base_indexes


def start_simplex(p_d):
    
    base_indexes = find_initial_basis(p_d.A)

    
    if -1 in base_indexes:
        phase1(p_d,base_indexes)

    phase2(data)

   

def phase1():
    return 

def phase2(data):
    
    data.xb = np.dot(data.inverse_matrix,data.b)
    data.y = np.dot(-data.c[data.in_base],data.inverse_matrix)
    data.z= np.dot(data.y,data.b)

    maxsteps =0
    while maxsteps < math.inf :
        #cerca costo negativo
        t = None                                       #decidere nome
        cj =None
        for j in data.out_base :
            cj= data.c[j] + np.dot(data.y,data.A[:,j])
            if cj <0 : 
                t = j
                break 

        if t==None: 
            return #trovato ottimo 

        #verifica condizioni illimitatezza
        Aj = np.dot(data.inverse_matrix,data.A[:,t])
        
        if (Aj<=0).all() :
            return 'problema illimitato inferiormente'

        #determino la variabile uscente 

        #h = np.ma.argmin(np.ma.MaskedArray(data.xb / Aj, Aj > 0))
        h = None
        min_val = math.inf
        min_idx = math.inf
        for i in range(Aj.size):
            x = data.xb[i] / Aj[i]
            if x > 0:
                if x == min_val and data.in_base[i] < min_idx:
                    h = i
                    min_idx = data.in_base[i]
                elif x < min_val:
                    min_val = x
                    min_idx = data.in_base[i]
                    h = i

        h_exiting = data.in_base[h]
        data.in_base[h]=t 
        t_index = np.where(data.out_base == t)[0]
        data.out_base[t_index] = h_exiting

        data.matrix = data.matrix[h+1]/Aj[h]

        for i in range(data.matrix.shape[0]):
            if i != h+1:
                if i>0 :
                    data.matrix[i] = data.matrix[i]-data.matrix[h+1]*Aj[h]
                else:
                    data.matrix[i] = data.matrix[i]-data.matrix[h+1]*cj
        
        maxsteps +=1
   



    
    



