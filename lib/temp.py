from operator import ne
import numpy as np 

new_basis = np.array([-1,-1,3])
c= np.array([-2,3,4,1])

np.place(new_basis,new_basis==-1,np.arange(len(c),len(c)+np.count_nonzero(new_basis == -1)))

print(new_basis)      #[0,4,3]