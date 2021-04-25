import numpy as np

class SupportData: # TODO Change name

    def __init__(self,obj_func_coefficent,coefficent_matrix,constant_terms,num_rows):
        self.c = obj_func_coefficent
        self.A = coefficent_matrix
        self.b = constant_terms 

        self.in_base = []
        self.out_base = []
        self.carry = self.carry(num_rows)

class Carry:
    
    def __init__(self, num_rows):
        self.matrix = np.zeros((num_rows+1,num_rows+1))
        self.y = self.matrix[0,:-1]
        self.z = self.matrix[0,-1]   
        self.inverse_matrix = self.matrix[1:,:-1]   
        self.xb = self.matrix[1:,-1]

    def set_y(self, y):
        self.matrix[0,:-1] = y
        
    def set_xb(self, xb):
        self.matrix[1:,-1] = xb

    def set_z(self, z):
        self.matrix[0,-1] = z
        self.z = z

    def set_inverse_matrix(self, inverse_matrix):
        self.matrix[1:,:-1] = inverse_matrix
    

def find_initial_basis(A):
    
    base_indexes = []
    id_matrix = np.identity(A.shape[0])
    for col in id_matrix:
        idx = np.where((A.T == col).all(axis=1))
        base_indexes.append(idx[0][0] if len(idx[0])>0 else -1)
    return base_indexes

def compute_out_of_base(data):
    data.out_base = np.array(set(range(data.A.shape[1])) - set(data.in_base)).sort()

def get_Aj(data,j):
    return np.dot(data.inverse_matrix,data.A[:,j])


def create_artificial_problem(data):

    #create obj function with artificial variables 
    obj_func = np.zeros_like(data.c)                             #TODO:   [0 for _ in range(len(data.c))]
    np.concatenate([obj_func,np.ones(data.in_base.count(-1))])      # TODO: obj_func.extend([1 for _ in range(data.in_base.count(-1))]) 

    #add artificial columns to the matrix of coefficents  
    id = np.identity(data.A.shape[0])
    coeff_matrix = data.A.copy()
    for i in range(len(data.in_base)):
        if data.in_base[i] == -1:
            coeff_matrix = np.c_[coeff_matrix,id[:,i]]

    #add constant terms 
    constant_terms = data.b.copy()

    #create object 
    data_p1 = SupportData(obj_func,coeff_matrix,constant_terms)  

    #artificial variables 
    data_p1.in_base = data.in_base.copy()
    artificial_variables = np.arange(len(data.c),len(data.c)+np.count_nonzero(data_p1.in_base == -1))
    np.place(data_p1.in_base, data_p1.in_base == -1, artificial_variables)

    #init matrix
    data_p1.set_inverse_matrix = np.identity(data_p1.A.shape[0])

    return data_p1, artificial_variables

#TODO 
def from_p1_to_p2(data_p1,data):
    #modifica data con i valori presi da data_p1 -> variabili in base , carry ecc 
    return 

def determine_entering_var(data):
    for j in data.out_base :
        cj = data.c[j] + np.dot(data.y,data.A[:,j])
        if cj < 0 : 
            return cj,j
    
    return None,None 

def determine_exiting_var(data,Aj):

    arr = data.xb/Aj
    h = np.where(arr > 0, arr, np.inf).argmin()

    #TODO: qui tocca vedere che porco due ritorna np.where
    out_index = h[data.in_base[h].argmin()]       #TODO: test          #BLAND rule
    
    return out_index

#TODO: nome ?? 
def init_carry(data):
    data.carry.set_xb = np.dot(data.carry.inverse_matrix,data.b)
    data.carry.set_y = np.dot(-data.c[data.in_base],data.carry.inverse_matrix)
    data.carry.jset_z = np.dot(data.y,data.b)

#TODO cost=0
def change_basis(data,h,Aj,cost=0):
   
    data.matrix = data.matrix[h+1]/Aj[h]
    for i in range(data.matrix.shape[0]):
        if i != h+1:
            if i>0 :
                data.matrix[i] = data.matrix[i]-data.matrix[h+1]*Aj[h]
            else:
                data.matrix[i] = data.matrix[i]-data.matrix[h+1]*cost

def substitute_artificial_vars(data_p1,artificial_vars):

    lin_dependent_rows = []

    idxs = np.where(np.in1d(data_p1.in_base,artificial_vars))
    #faccio uscire la variabile artificiale all'indice idx 
    for idx in idxs:
        #determino chi entra
        ent_var = None 
        for var in data_p1.out_base:
            Aj = get_Aj(var)
            if Aj[idx] != 0:
                # entra var 
                data_p1.in_base[idx] = var
                change_basis(data_p1,idx,Aj)
                ent_var = var
                break
        if ent_var == None :                            #non esiste una variabile fuori base con cui sositutire la variabile artificiale 
            lin_dependent_rows.append(idx)              #una riga del sistema originale è ridondante 
        else :
            compute_out_of_base(data_p1) 
        
    return lin_dependent_rows


        
def start_simplex(data):

    data.in_base = find_initial_basis(data.A) 
    data.set_inverse_matrix = np.identity(data.A.shape[0])

    if -1 in data.in_base:
        data_p1 = phase1(data)
        from_p1_to_p2(data_p1,data)            #TODO: quando farlo ? problema impossibile ? 
    
    phase2(data)

    #TODO: leggere data e metter in output ottimo , base , ecc 

def phase1(data):

    data_p1,artificial_vars = create_artificial_problem(data)

    init_carry(data_p1)
    
    while True :

        #determina le variabili fuori base
        compute_out_of_base(data_p1)

        #calcola i costi ridotti e trova quello negativo con indice minore
        cost,ent_var = determine_entering_var(data_p1)
        if cost == None: 
            if data_p1.carry.z != 0 :     #TODO: cosa succede se minore di zero 
                break     #TODO: 'problema originale inammissibile'
            elif np.in1d(data_p1.in_base,artificial_vars).any()  :   
                lin_dep_rows = substitute_artificial_vars()
                break     #TODO: eliminare le righe ridondanti
            else : 
                break     #TODO: 'nessuna var artificiale in base, uscire e iniziare fase 2 

        
        Aj = get_Aj(data_p1,ent_var)     #np.dot(data_p1.inverse_matrix,data_p1.A[:,ent_var])

        #determino la variabile uscente
        ext_var_index = determine_exiting_var(data_p1,Aj)

        #faccio entrare ent_var e uscire ext_var
        data_p1.in_base[ext_var_index] = ent_var

        #cambio di base
        change_basis(data_p1,ext_var_index,Aj,cost)

def phase2(data):

    init_carry(data)

    while True :

        #determina le variabili fuori base
        compute_out_of_base(data)

        #calcola i costi ridotti e trova quello negativo con indice minore
        cost,ent_var = determine_entering_var(data)
        if cost == None: 
            break      #TODO 'trovato ottimo'
        
        #verifica condizioni illimitatezza
        Aj = get_Aj(data,ent_var)
        if (Aj<=0).all() :
            break     #TODO 'problema illimitato inferiormente'
        
        #determino la variabile uscente
        ext_var_index = determine_exiting_var(data,Aj)

        #faccio entrare ent_var e uscire ext_var
        data.in_base[ext_var_index] = ent_var

        #cambio di base
        change_basis(data,ext_var_index,Aj,cost)
    
    return data
    