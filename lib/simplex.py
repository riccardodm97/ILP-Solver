import numpy as np

class SimplexProblem:

    def __init__(self, obj_func_coefficent, coefficent_matrix, constant_terms):
        self.c = np.array(obj_func_coefficent)
        self.A = np.array(coefficent_matrix)
        self.b = np.array(constant_terms) 

        self.in_basis = None
        self.out_basis = None

        self.carry_matrix = np.zeros((self.b.size + 1,self.b.size + 1))

    def get_y(self):
        return self.carry_matrix[0,:-1]
    def get_z(self):
        return self.carry_matrix[0:1,-1]
    def get_inverse_matrix(self):
        return self.carry_matrix[1:,:-1]  
    def get_xb(self):
        return self.carry_matrix[1:,-1]
    
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
        self.set_xb(np.dot(self.get_inverse_matrix(),self.b))                #TODO Sometimes useless computation
        self.set_y(np.dot(-self.c[self.in_basis],self.get_inverse_matrix()))
        self.set_z(np.dot(self.get_y(),self.b))
    
    def compute_out_of_base(self):
        self.out_basis = np.array(list(set(range(self.A.shape[1])) - set(self.in_basis)))
        self.out_basis.sort()      #BLAND rule
    
    def get_Aj(self, j):
        return np.dot(self.get_inverse_matrix(),self.A[:,j])
    
    def swap_vars(self,ext_var,ent_var):
        self.in_basis[ext_var] = ent_var
    
    def determine_entering_var(self):
        for j in self.out_basis :
            cj = self.c[j] + np.dot(self.get_y(),self.A[:,j])
            if cj < 0 : 
                return cj,j
        
        return None,None
    
    def determine_exiting_var(self,ent_var):
        Aj = self.get_Aj(ent_var)
        if (Aj<=0).all() :                            #unlimited problem            
            return None,None 

        arr = self.get_xb()/Aj
        positives = np.where(arr > 0, arr, np.inf)
        h = np.where(positives == positives.min())

        out_index = h[self.in_basis[h].argmin()][0]     #BLAND rule
        
        return Aj,out_index

    def update_carry(self,h,Aj,cost=None):
        self.carry_matrix[h+1] = self.carry_matrix[h+1]/Aj[h]
        for i in range(self.carry_matrix.shape[0]):
            if i != h+1:
                if i == 0 and cost is not None:
                    self.carry_matrix[i] = self.carry_matrix[i]-self.carry_matrix[h+1]*cost
                else :
                    self.carry_matrix[i] = self.carry_matrix[i]-self.carry_matrix[h+1]*Aj[i-1]
                

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
        for idx in idxs[0]:
            #determine which is entering
            ent_var = None 
            for var in self.out_basis[~np.isin(self.out_basis,self.artificial_vars)]:
                Aj = self.get_Aj(var)
                if Aj[idx] != 0:
                    # var entering
                    self.in_basis[idx] = var
                    self.update_carry(idx,Aj)
                    ent_var = var
                    break                                   
            if ent_var == None :                            #cannot find a substituting out of base var
                lin_dependent_rows.append(idx)              #a row of the original problem was redundant
            else :
                self.compute_out_of_base() 
            
        return np.array(lin_dependent_rows) if lin_dependent_rows else None
 

def define_artificial_problem(p):
    r = np.count_nonzero(p.in_basis == -1)    #num of var to be replaced by artificial ones 
    
    #create obj function with artificial variables 
    obj_func = np.zeros_like(p.c)                                                        
    obj_func = np.concatenate([obj_func,np.ones(r)])     

    #create artificial columns for the coefficents matrix 
    id = np.identity(p.A.shape[0])
    coeff_matrix = p.A.copy()
    for i in range(len(p.in_basis)):
        if p.in_basis[i] == -1:
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
        ret_type = phase1(problem)             #TODO: return type                    
        if ret_type is None:                   #TODO: modificare in base al valore di ritorno
            return ret_type
    
    phase2(problem)
    print("\nthe optimum value is",-problem.get_z()[0])

def from_p1_to_p2(p1,p,lin_dep_rows):
    if lin_dep_rows is not None :
        #modify original problem data
        p.A = np.delete(p.A, lin_dep_rows, axis=0)
        p.b = np.delete(p.b,lin_dep_rows)
        #modify phase1 dara
        p1.set_carry_matrix(np.delete(p1.carry_matrix, lin_dep_rows+1 , axis=0))   #delete rows from carry
        p1.set_carry_matrix(np.delete(p1.carry_matrix, lin_dep_rows, axis=1))     #delete columns from carry
        p1.in_basis = np.delete(p1.in_basis,lin_dep_rows)

    p.set_carry_matrix(p1.carry_matrix)
    p.in_basis = p1.in_basis.copy()


def phase1(p : SimplexProblem):
    #determine changes to make for artificial problem
    c,A,b,art_vars = define_artificial_problem(p)

    #create object 
    p1 = SimplexArtificialProblem(c,A,b,art_vars,p.in_basis.copy())

    #set starting basis 
    p1.find_initial_basis()
    p1.set_inverse_matrix()

    p1.init_carry()

    while True :

        #save out of basis vars
        p1.compute_out_of_base()

        #compute reduced costs and determine entering var 
        cost,ent_var = p1.determine_entering_var()
        lin_dep_rows = None
        if cost == None:                                    #no negative cost found
            if p1.get_z()[0] != 0 :                               #TODO: cosa succede se minore di zero 
                return "original problem is impossible"     #TODO: return type
            elif p1.check_basis():   
                lin_dep_rows = p1.substitute_artificial_vars()   

            from_p1_to_p2(p1,p,lin_dep_rows)
            return "go on with phase 2"                      #TODO : return type  

        #determine exiting var 
        Aj,ext_var_index = p1.determine_exiting_var(ent_var)

        #ent_var entering basis , ext_var leaving
        p1.swap_vars(ext_var_index,ent_var)        

        #modify carry matrix 
        p1.update_carry(ext_var_index,Aj,cost)

def phase2(p : SimplexProblem):

    p.init_carry()

    while True :

        #save out of basis vars
        p.compute_out_of_base()

        #compute reduced costs and determine entering var 
        cost,ent_var = p.determine_entering_var()
        if cost == None: 
            return "found optimum of original problem"      #TODO return type
        
        #determine exiting var 
        Aj,ext_var_index = p.determine_exiting_var(ent_var)
        if Aj is None:
            return "unlimited problem"                      #TODO: return type
        
        #ent_var entering basis , ext_var leaving
        p.swap_vars(ext_var_index,ent_var)        

        #modify carry matrix 
        p.update_carry(ext_var_index,Aj,cost)
