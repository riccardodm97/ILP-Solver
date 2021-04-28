import numpy as np

class SimplexProblem:

    def __init__(self, obj_func_coefficent, coefficent_matrix, constant_terms):
        self.c = np.array(obj_func_coefficent)
        self.A = np.array(coefficent_matrix)
        self.b = np.array(constant_terms) 

        self.in_base = None
        self.out_base = None
        self.carry_matrix = np.zeros((self.b.size + 1,self.b.size + 1))
        self.y = self.carry_matrix[0,:-1]
        self.z = self.carry_matrix[0:1,-1]
        self.inverse_matrix = self.carry_matrix[1:,:-1]   
        self.xb = self.carry_matrix[1:,-1]

    def set_y(self, y):
        self.carry_matrix[0,:-1] = y
        
    def set_xb(self, xb):
        self.carry_matrix[1:,-1] = xb

    def set_z(self, z):
        self.carry_matrix[0,-1] = z

    def set_inverse_matrix(self, inverse_matrix):
        self.carry_matrix[1:,:-1] = inverse_matrix
    

    def find_initial_basis(self):
        
        base_indexes = []
        id_matrix = np.identity(self.A.shape[0])
        for col in id_matrix:
            idx = np.where((self.A.T == col).all(axis=1))
            base_indexes.append(idx[0][0] if len(idx[0])>0 else -1)
        return np.array(base_indexes)

    def compute_out_of_base(self):
        self.out_base = np.array(list(set(range(self.A.shape[1])) - set(self.in_base)))
        self.out_base.sort()

    def get_Aj(self, j):
        return np.dot(self.inverse_matrix,self.A[:,j])

    def create_artificial_problem(self):

        #create obj function with artificial variables 
        obj_func = np.zeros_like(self.c)                                                        # TODO: [0 for _ in range(len(self.c))]
        obj_func = np.concatenate([obj_func,np.ones(np.count_nonzero(self.in_base == -1))])     # TODO: obj_func.extend([1 for _ in range(self.in_base.count(-1))]) 

        #add artificial columns to the matrix of coefficents  
        id = np.identity(self.A.shape[0])
        coeff_matrix = self.A.copy()
        for i in range(len(self.in_base)):
            if self.in_base[i] == -1:
                coeff_matrix = np.c_[coeff_matrix,id[:,i]]

        #add constant terms 
        constant_terms = self.b.copy()

        #create object 
        data_p1 = SimplexArtificialProblem(obj_func,coeff_matrix,constant_terms)  

        #artificial variables 
        data_p1.in_base = self.in_base.copy()
        artificial_variables = np.arange(len(self.c),len(self.c)+np.count_nonzero(data_p1.in_base == -1))
        np.place(data_p1.in_base, data_p1.in_base == -1, artificial_variables)

        #init matrix
        data_p1.set_inverse_matrix = np.identity(data_p1.A.shape[0])

        return data_p1, artificial_variables

    def determine_entering_var(self):
        for j in self.out_base :
            cj = self.c[j] + np.dot(self.y,self.A[:,j])
            if cj < 0 : 
                return cj,j
        
        return None,None 

    def determine_exiting_var(self,Aj):

        arr = self.xb/Aj
        positives = np.where(arr > 0, arr, np.inf)
        h = np.where(positives == positives.min())

        #TODO: rifare 
        out_index = h[self.in_base[h].argmin()][0]       #TODO: test          #BLAND rule
        
        return out_index

    #TODO: nome ?? 
    def init_carry(self):
        self.set_xb(np.dot(self.inverse_matrix,self.b)) #TODO Sometimes useless computation
        self.set_y(np.dot(-self.c[self.in_base],self.inverse_matrix))
        self.set_z(np.dot(self.y,self.b))

    #TODO cost=0
    def change_basis(self,h,Aj,cost=0):
    
        self.carry_matrix[h+1] = self.carry_matrix[h+1]/Aj[h]
        for i in range(self.carry_matrix.shape[0]):
            if i != h+1:
                if i>0 :
                    self.carry_matrix[i] = self.carry_matrix[i]-self.carry_matrix[h+1]*Aj[i-1]
                else:
                    self.carry_matrix[i] = self.carry_matrix[i]-self.carry_matrix[h+1]*cost

            
    def start_simplex(self):

        self.in_base = self.find_initial_basis() 
        self.set_inverse_matrix(np.identity(self.A.shape[0]))

        if -1 in self.in_base:
            data = self.phase1()
            if data is None:
                return "IMPOSSIBBILE" #TODO Impossible
        
        self.phase2()
        return -self.z[0]

    def phase1(self):

        data_p1,artificial_vars = self.create_artificial_problem()

        data_p1.init_carry()
        
        while True :

            #determina le variabili fuori base
            data_p1.compute_out_of_base()

            #calcola i costi ridotti e trova quello negativo con indice minore
            cost,ent_var = data_p1.determine_entering_var()
            if cost == None: 
                if data_p1.z[0] != 0 :     #TODO: cosa succede se minore di zero 
                    return None
                elif np.in1d(data_p1.in_base,artificial_vars).any():   
                    lin_dep_rows = data_p1.substitute_artificial_vars(artificial_vars)
                    self.A = np.delete(self.A, lin_dep_rows, axis=0)
                
                from_p1_to_p2(data_p1, self)
            
            Aj = data_p1.get_Aj(ent_var)     #np.dot(data_p1.inverse_matrix,data_p1.A[:,ent_var])

            #determino la variabile uscente
            ext_var_index = data_p1.determine_exiting_var(Aj)

            #faccio entrare ent_var e uscire ext_var
            data_p1.in_base[ext_var_index] = ent_var

            #cambio di base
            data_p1.change_basis(ext_var_index,Aj,cost)

    def phase2(self):

        self.init_carry()

        while True :

            #determina le variabili fuori base
            self.compute_out_of_base()

            #calcola i costi ridotti e trova quello negativo con indice minore
            cost,ent_var = self.determine_entering_var()
            if cost == None: 
                break      #TODO 'trovato ottimo'
            
            #verifica condizioni illimitatezza
            Aj = self.get_Aj(ent_var)
            if (Aj<=0).all() :
                break     #TODO 'problema illimitato inferiormente'
            
            #determino la variabile uscente
            ext_var_index = self.determine_exiting_var(Aj)

            #faccio entrare ent_var e uscire ext_var
            self.in_base[ext_var_index] = ent_var

            #cambio di base
            self.change_basis(ext_var_index,Aj,cost)
        
class SimplexArtificialProblem(SimplexProblem):
    def substitute_artificial_vars(data_p1,artificial_vars):

        lin_dependent_rows = []

        idxs = np.where(np.in1d(data_p1.in_base,artificial_vars))
        #faccio uscire la variabile artificiale all'indice idx 
        for idx in idxs:
            #determino chi entra
            ent_var = None 
            for var in data_p1.out_base:
                Aj = data_p1.get_Aj(var)
                if Aj[idx] != 0:
                    # entra var 
                    data_p1.in_base[idx] = var
                    data_p1.change_basis(idx,Aj)
                    ent_var = var
                    break
            if ent_var == None :                            #non esiste una variabile fuori base con cui sositutire la variabile artificiale 
                lin_dependent_rows.append(idx)              #una riga del sistema originale è ridondante 
            else :
                data_p1.compute_out_of_base() 
            
        return np.array(lin_dependent_rows)


def from_p1_to_p2(data_p1,self):
    
    self.set_inverse_matrix(data_p1.inverse_matrix)
    self.in_base = data_p1.in_base.copy()