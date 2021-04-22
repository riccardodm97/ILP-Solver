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

    data_f1= SupportData(cose)  #TODO: cose non so in che modo partendo da data
    return data_f1

def from_f1_to_f2(data_f1,data):
    #modifica data con i valori presi da data_f1 -> variabili in base , carry ecc 
    #TODO 
    return 

def start_simplex(data):

    base_indexes = find_initial_basis(data.A)
    data.in_base = base_indexes 
    compute_out_of_base(data)

    if -1 in base_indexes:
        phase1(data)
    
    phase2(data)

def phase1(data):

    data_f1 = create_artificial_problem(data)
    
    #fai cose fino a una soluzione / impossibile 

    from_f1_to_f2(data_f1,data)

def phase2(data):



