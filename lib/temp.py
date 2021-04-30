import numpy as np

class SimplexProblem:

    def __init__(self, obj_func_coefficent, coefficent_matrix, constant_terms):
        self.c = np.array(obj_func_coefficent)
        self.A = np.array(coefficent_matrix)
        self.b = np.array(constant_terms) 

        self.in_basis = None
        self.out_basis = None

        self.carry_matrix = np.zeros((self.b.size + 1,self.b.size + 1))
        self.y = self.carry_matrix[0,:-1]
        self.z = self.carry_matrix[0:1,-1]
        self.inverse_matrix = self.carry_matrix[1:,:-1]   
        self.xb = self.carry_matrix[1:,-1]
    
    def set_carry_matrix(self, matrix):
        self.carry_matrix = matrix

    def set_y(self, y):
        self.carry_matrix[0,:-1] = y
        
    def set_xb(self, xb):
        self.carry_matrix[1:,-1] = xb

    def set_z(self, z):
        self.carry_matrix[0,-1] = z

    def set_inverse_matrix(self, inverse_matrix = None):
        self.carry_matrix[1:,:-1] = inverse_matrix or np.identity(self.A.shape[0])
    
    def check_basis(self):
        return -1 in self.in_basis
    
    def find_initial_basis(self):
        base_indexes = []
        id_matrix = np.identity(self.A.shape[0])
        for col in id_matrix:
            idx = np.where((self.A.T == col).all(axis=1))
            base_indexes.append(idx[0][0] if len(idx[0])>0 else -1)
        self.in_basis = np.array(base_indexes) 
    
    def init_carry(self):
        self.set_xb(np.dot(self.inverse_matrix,self.b))                #TODO Sometimes useless computation
        self.set_y(np.dot(-self.c[self.in_basis],self.inverse_matrix))
        self.set_z(np.dot(self.y,self.b))
    
    def compute_out_of_base(self):
        self.out_basis = np.array(list(set(range(self.A.shape[1])) - set(self.in_base)))
        self.out_basis.sort()      #BLAND rule
    
    def get_Aj(self, j):
        return np.dot(self.inverse_matrix,self.A[:,j])
    
    def determine_entering_var(self):
        for j in self.out_basis :
            cj = self.c[j] + np.dot(self.y,self.A[:,j])
            if cj < 0 : 
                return cj,j
        
        return None,None 

class SimplexArtificialProblem(SimplexProblem):
    def __init__(self, obj_func_coefficent, coefficent_matrix, constant_terms,artificial_vars,old_basis):
        self.artificial_vars = artificial_vars
        self.old_basis = old_basis
        super().__init__(obj_func_coefficent,coefficent_matrix,constant_terms)
    
    def find_initial_basis(self):
        in_basis = self.old_basis.copy()
        np.place(in_basis, in_basis == -1, self.artificial_vars)
        self.in_basis = in_basis
    
    def check_basis(self):
        return np.in1d(self.in_basis,self.artificial_vars).any()

    def substitute_artificial_vars(self):
        lin_dependent_rows = []

        idxs = np.where(np.in1d(self.in_basis,self.artificial_vars))
        #all artificial var with idx index should leave basis  
        for idx in idxs:
            #determine which is entering
            ent_var = None 
            for var in self.out_basis:
                Aj = self.get_Aj(var)
                if Aj[idx] != 0:
                    # var entering
                    self.in_basis[idx] = var
                    self.change_basis(idx,Aj)
                    ent_var = var
                    break                                   
            if ent_var == None :                            #cannot find a substituting out of base var
                lin_dependent_rows.append(idx)              #a row of the original problem was redundant
            else :
                self.compute_out_of_base() 
            
        return np.array(lin_dependent_rows)
    

def find_initial_basis(p):
    base_indexes = []
    id_matrix = np.identity(p.A.shape[0])
    for col in id_matrix:
        idx = np.where((p.A.T == col).all(axis=1))
        base_indexes.append(idx[0][0] if len(idx[0])>0 else -1)
    return np.array(base_indexes) 

def define_artificial_problem(p):
    r = np.count_nonzero(p.in_base == -1)    #num of var to be replaced by artificial ones 
    
    #create obj function with artificial variables 
    obj_func = np.zeros_like(p.c)                                                        
    obj_func = np.concatenate([obj_func,np.ones(r)])     

    #create artificial columns for the coefficents matrix 
    id = np.identity(p.A.shape[0])
    coeff_matrix = p.A.copy()
    for i in range(len(p.in_basis)):
        if p.in_base[i] == -1:
            coeff_matrix = np.c_[coeff_matrix,id[:,i]]

    #copy costant terms 
    constant_terms = p.b.copy()

    #determine artificial vars
    artificial_variables = np.arange(len(p.c),len(p.c)+r)
    

    return obj_func,coeff_matrix,constant_terms,artificial_variables

def simplex_algorithm(c, A, b):
    #create object 
    problem = SimplexProblem(c, A, b)

    #set starting basis 
    problem.find_initial_basis()
    problem.set_inverse_matrix()
    
    #if cannot find starting basis phase1 is needed 
    if problem.check_basis():
        phase1(problem)
        return 
    return 
        


def phase1(p):
    #determine changes to make for artificial problem
    c,A,b,art_vars = define_artificial_problem(p)

    #create object 
    problem_p1 = SimplexArtificialProblem(c,A,b,art_vars,p.in_basis.copy())

    #set starting basis 
    problem_p1.find_initial_basis()
    problem_p1.set_inverse_matrix()

    problem_p1.init_carry()

    while True :

        #save out of basis vars
        problem_p1.compute_out_of_base()

        #compute reduced costs and determine entering var 
        cost,ent_var = problem_p1.determine_entering_var()
        if cost == None:               #no negative cost found
            if problem_p1.z[0] != 0 :     #TODO: cosa succede se minore di zero 
                return None               #TODO: return type
            elif problem_p1.check_basis():   
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


