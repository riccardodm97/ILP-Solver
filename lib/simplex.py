from enum import Enum
from lib.utils import Parameters, ProblemSolution
from lib import logger 
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
        self.set_xb(np.dot(self.get_inverse_matrix(),self.b))                
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
                logger.write("Chosen entering variable: x" + str(j))
                return cj,j
        
        return None,None
    
    def determine_exiting_var(self,ent_var):
        Aj = self.get_Aj(ent_var)
        if (Aj<=0).all() :                            #unlimited problem            
            return None,None 

        positives = np.where(Aj > 0, np.divide(self.get_xb(), Aj, out=np.zeros_like(Aj), where=(Aj!=0)), np.inf)
        h = np.where(positives == positives.min())[0]

        out_index = h[self.in_basis[h].argmin()]     #BLAND rule
        
        logger.write("Chosen exiting variable: x" + str(self.in_basis[out_index])) #TODO Print bland rule
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
                if round(Aj[idx], Parameters.DECIMAL_PRECISION) != 0:
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
    logger.write("\nStarting simplex")                                                                            
    #create object 
    problem = SimplexProblem(c, A, b)

    #set starting basis 
    problem.find_initial_basis()
    problem.set_inverse_matrix()
    
    #if cannot find starting basis phase1 is needed 
    if problem.check_basis():
        logger.write("Unable to find an Initial Starting Basis, proceeding with Phase1")
        ret_type = phase1(problem)
        logger.write("End of Phase 1")                  
        
        if ret_type is ProblemSolution.IMPOSSIBLE:
            return ret_type, None, None
    else:
        logger.write("Starting basis found, switching to Phase 2")   
    
    ret_type = phase2(problem)

    if ret_type is ProblemSolution.FINITE:
        solution = np.zeros(problem.c.size)
        solution[problem.in_basis] = problem.get_xb()
        opt = round(-problem.get_z()[0], Parameters.DECIMAL_PRECISION)
        return ret_type, opt, np.around(solution, Parameters.DECIMAL_PRECISION)    
    else:
        return ret_type, None, None

def from_p1_to_p2(p1 : SimplexArtificialProblem,p : SimplexProblem,lin_dep_rows):
    if lin_dep_rows is not None :
        #modify original problem data
        p.A = np.delete(p.A, lin_dep_rows, axis=0)
        p.b = np.delete(p.b,lin_dep_rows)
        #modify phase1 data
        p1.set_carry_matrix(np.delete(p1.carry_matrix, lin_dep_rows+1 , axis=0))   #delete rows from carry
        p1.set_carry_matrix(np.delete(p1.carry_matrix, lin_dep_rows, axis=1))      #delete columns from carry
        p1.in_basis = np.delete(p1.in_basis,lin_dep_rows)                          #remove not needed in basis variable 

    p.set_carry_matrix(p1.carry_matrix)
    p.in_basis = p1.in_basis.copy()


def phase1(p : SimplexProblem):
    logger.write("\nStarting Phase 1")
    #determine changes to make for artificial problem
    c,A,b,art_vars = define_artificial_problem(p)
    logger.write("Inserting ",["x"+str(i) for i in art_vars]," as artificial variables")

    #create object 
    p1 = SimplexArtificialProblem(c,A,b,art_vars,p.in_basis.copy())

    #set starting basis 
    p1.find_initial_basis()
    p1.set_inverse_matrix()

    p1.init_carry()

    while True :
        logger.write("\nNew basis: ",["x"+str(i) for i in p1.in_basis])

        #save out_of_basis vars
        p1.compute_out_of_base()

        #compute reduced costs and determine entering var 
        cost,ent_var = p1.determine_entering_var()
        lin_dep_rows = None
        if cost == None:            #no negative cost found
            if round(p1.get_z()[0], Parameters.DECIMAL_PRECISION) != 0 :                                                  
                return ProblemSolution.IMPOSSIBLE
            elif p1.check_basis():   
                lin_dep_rows = p1.substitute_artificial_vars()   

            from_p1_to_p2(p1,p,lin_dep_rows)
            return ProblemSolution.FINITE

        #determine exiting var 
        Aj,ext_var_index = p1.determine_exiting_var(ent_var)
        
        if Aj is None:
            # Raising exception as this case should not be achievable
            raise ArithmeticError

        #ent_var entering basis , ext_var leaving
        p1.swap_vars(ext_var_index,ent_var)     

        #modify carry matrix 
        p1.update_carry(ext_var_index,Aj,cost)

def phase2(p : SimplexProblem):
    logger.write("\nStarting Phase 2")

    p.init_carry()

    while True :
        logger.write("\nNew basis: ",["x"+str(i) for i in p.in_basis])

        #save out_of_basis vars
        p.compute_out_of_base()

        #compute reduced costs and determine entering var 
        cost,ent_var = p.determine_entering_var()
        if cost == None: 
            return ProblemSolution.FINITE
            
        #determine exiting var 
        Aj,ext_var_index = p.determine_exiting_var(ent_var)
        if Aj is None:
            return ProblemSolution.UNLIMITED

        #ent_var entering basis , ext_var leaving
        p.swap_vars(ext_var_index,ent_var)        

        #modify carry matrix 
        p.update_carry(ext_var_index,Aj,cost)
