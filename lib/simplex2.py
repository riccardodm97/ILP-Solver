import numpy as np

class SupportData:

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


def create_artificial_problem(data):
    #create obj function with artificial variables 
    obj_func = [0 for _ in range(len(data.c))]
    obj_func.extend([1 for _ in range(data.in_base.count(-1))])

    #add artificial columns to the matrix of coefficents  
    id = np.identity(data.A.shape[0])
    coeff_matrix = data.A.copy()
    for i in range(len(data.in_base)):
        if data.in_base[i] == -1:
            np.c_[coeff_matrix,id[:,i]]

    #add constant terms 
    constant_terms = data.b.copy()

    data_f1= SupportData(obj_func,coeff_matrix,constant_terms)  #create object 
    data_f1.in_base = find_initial_basis(data_f1.A)
    data_f1.set_inverse_matrix = np.identity(data_f1.A.shape[0])
    return data_f1

#TODO 
def from_f1_to_f2(data_f1,data):
    #modifica data con i valori presi da data_f1 -> variabili in base , carry ecc 
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
    out_index = h[data.in_base[h].argmin()]       #TODO: test 
    
    return out_index

#TODO: nome ?? 
def init_carry(data):
    data.carry.set_xb = np.dot(data.carry.inverse_matrix,data.b)
    data.carry.set_y = np.dot(-data.c[data.in_base],data.carry.inverse_matrix)
    data.carry.jset_z = np.dot(data.y,data.b)

#TODO 
def change_basis(data,h,Aj,cost):
   
    data.matrix = data.matrix[h+1]/Aj[h]
    for i in range(data.matrix.shape[0]):
        if i != h+1:
            if i>0 :
                data.matrix[i] = data.matrix[i]-data.matrix[h+1]*Aj[h]
            else:
                data.matrix[i] = data.matrix[i]-data.matrix[h+1]*cost
        
def start_simplex(data):

    base_indexes = find_initial_basis(data.A)
    data.in_base = base_indexes 
    data.set_inverse_matrix = np.identity(data.A.shape[0])

    if -1 in base_indexes:
        data_f1 = phase1(data)
        from_f1_to_f2(data_f1,data)            #TODO: quando farlo ? problema impossibile ? 
    
    phase2(data)

    #TODO: leggere data e metter in output ottimo , base , ecc 

def phase1(data):

    data_f1 = create_artificial_problem(data)

    init_carry(data_f1)

    artificial_vars = []          #TODO: dove le prendo ???
    
    while True :

        #determina le variabili fuori base
        compute_out_of_base(data_f1)

        #calcola i costi ridotti e trova quello negativo con indice minore
        cost,ent_var = determine_entering_var(data_f1)
        if cost == None: 
            if data_f1.carry.z != 0 :     #TODO: cosa succede se minore di zero 
                break     #TODO: 'problema originale inammissibile'
            elif cose :
                break     #TODO: far uscire le variabili artificiali ancora in base 
            else : 
                break     #TODO: 'nessuna var artificiale in base, uscire e iniziare fase 2 

        
        Aj = np.dot(data_f1.inverse_matrix,data_f1.A[:,ent_var])

        #determino la variabile uscente
        ext_var_index = determine_exiting_var(data_f1,Aj)

        #faccio entrare ent_var e uscire ext_var
        data_f1.in_base[ext_var_index] = ent_var

        #cambio di base
        change_basis(data_f1,ext_var_index,Aj,cost)

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
        Aj = np.dot(data.inverse_matrix,data.A[:,ent_var])
        if (Aj<=0).all() :
            break     #TODO 'problema illimitato inferiormente'
        
        #determino la variabile uscente
        ext_var_index = determine_exiting_var(data,Aj)

        #faccio entrare ent_var e uscire ext_var
        data.in_base[ext_var_index] = ent_var

        #cambio di base
        change_basis(data,ext_var_index,Aj,cost)
    
    return data
    