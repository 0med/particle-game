import numpy as np

# x1 = np.arange(9.0).reshape((3, 3))
# x2 = np.arange(3.0)
# new_arr = np.add(x1, x2)

matrix = np.array(
    [[2, -4],
     [1, 2]])

matrix_inverse = np.linalg.inv(matrix)
id = matrix @ matrix_inverse

print(matrix_inverse)
print(id)