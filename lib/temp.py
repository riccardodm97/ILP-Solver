import numpy as np 

class Problem_data:
    
    def __init__(self,coefficent_matrix,constant_terms,obj_func_coefficent):
        self.c = obj_func_coefficent
        self.A = coefficent_matrix
        self.b = constant_terms 

    
class Support_data:

    def __init__(self,num_rows):
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

 #TODO aggiungere metodi di update 
    



#from f1 to f2 function called by f1 


#out of base ordinabile e inizializzato a partire da in base 
#in base non ordinabile 
