import numpy as np

def transform_points(A, B, C, Tx, Ty, theta):
    """
    计算平移和旋转之后的A和B坐标
    :param A: 原始点A坐标 (x_A, y_A)
    :param B: 原始点B坐标 (x_B, y_B)
    :param C: 旋转中心坐标 (cx, cy)
    :param Tx: C的横向平移量
    :param Ty: C的纵向平移量
    :param theta: 旋转角度（弧度）
    :return: 平移和旋转之后的A和B坐标
    """
     
    # 计算新的旋转中心C_prime
    C_prime = np.array(C) + np.array([Tx, Ty])
    # 计算旋转矩阵
    R = np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta), np.cos(theta)]])
    # 将A和B相对于C计算中心
    A_relative_to_C = np.array(A) - np.array(C)
    B_relative_to_C = np.array(B) - np.array(C)
    # 旋转A和B点
    A_rotated = R @ A_relative_to_C
    B_rotated = R @ B_relative_to_C 
    # 将旋转后的A和B点转回原始坐标系
    A_prime = A_rotated + C_prime
    B_prime = B_rotated + C_prime
    return A_prime, B_prime



# 已知点坐标
A = np.array([0, 0.8])
B = np.array([1, 1])
C = np.array([0, 0])

# 目标位置
A_prime = np.array([1, -1])
B_prime = np.array([0, -0.8])

# 目标位置
L_AB = np.linalg.norm(B - A)
theta_AB = np.arctan2(B[1] - A[1], B[0] - A[0])


# 计算目标线段长度和角度
L_A_prime_B_prime = np.linalg.norm(B_prime - A_prime)
theta_A_prime_B_prime = np.arctan2(B_prime[1] - A_prime[1], B_prime[0] - A_prime[0])

# 计算旋转角度
theta = theta_A_prime_B_prime - theta_AB

# 计算旋转矩阵
R = np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta), np.cos(theta)]])

# 计算旋转后的点
A_double_prime = np.dot(R, A - C) + C
B_double_prime = np.dot(R, B - C) + C

# 计算平移量
T = A_prime - A_double_prime

# 平移旋转中心
C_prime = C + T

# 输出结果
print(f"平移量: {T}")
print(f"旋转角度: {np.degrees(theta)} 度")
print(f"新的旋转中心坐标: {C_prime}")


# 旋转回去
Tx = T[0]# C的横向平移量
Ty = T[1]# C的纵向平移量
theta0 = theta # 旋转角度（45度）

# 调用函数计算平移和旋转之后的A和B坐标
A_prime_t, B_prime_t = transform_points(A, B, C, Tx, Ty, theta0)

# 显示结果
print('平移和旋转之前的A坐标:', A)
print('平移和旋转之前的B坐标:', B)
print('平移和旋转之后的A坐标:', A_prime_t)
print('平移和旋转之后的B坐标:', B_prime_t)
print('平移和旋转之后正确的A坐标:', A_prime)
print('平移和旋转之后正确的B坐标:', B_prime)