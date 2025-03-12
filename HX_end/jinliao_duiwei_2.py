import numpy as np
import cv2


############################################################
# 计算仿射变换矩阵
############################################################
def compute_affine_matrix(P, Q):
    # 将点转换为 numpy 数组，并指定数据类型为 float
    P = np.array(P, dtype=float)
    Q = np.array(Q, dtype=float)

    # 构造最小二乘问题的矩阵
    A = np.hstack([P, np.ones((P.shape[0], 1))])
    B = Q

    # 求解最小二乘问题
    affine_matrix, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)

    # 将结果转换为 3x3 的仿射变换矩阵
    affine_matrix = np.vstack([affine_matrix.T, [0, 0, 1]])

    return affine_matrix


############################################################
# 根据仿射变换矩阵求转换后的点
############################################################
def affine_transform_points(affine_matrix, points):
    # 将点转换为 numpy 数组，并指定数据类型为 float
    points = np.array(points, dtype=float)

    # 将点扩展为齐次坐标形式 (x, y) -> (x, y, 1)
    points_hom = np.hstack([points, np.ones((points.shape[0], 1))])

    # 应用仿射变换矩阵
    transformed_points_hom = points_hom @ affine_matrix.T

    # 将结果转换为非齐次坐标形式 (x, y, 1) -> (x, y)
    transformed_points = transformed_points_hom[:, :2]

    return transformed_points


############################################################
# 三点求圆
############################################################
def find_circle_center(points):
    # 将输入点转换为numpy数组
    points = np.array(points, dtype=np.float32)

    # 使用cv2.minEnclosingCircle找到最小外接圆
    (x, y), radius = cv2.minEnclosingCircle(points)

    # 返回圆心坐标和半径
    center = (x, y)
    return center, radius


############################################################
# 三点求圆可视化
############################################################
def visualize_points_and_center(points, center, radius):
    # 创建一个空白图像
    width, height = 400, 400
    image = np.zeros((height, width, 3), dtype=np.uint8)

    # 定义颜色
    point_color = (0, 255, 0)  # 绿色
    center_color = (0, 0, 255)  # 红色
    circle_color = (255, 0, 0)  # 蓝色

    # 定义半径
    point_radius = 5
    center_radius = 5
    circle_thickness = 2

    # 将点坐标转换为整数类型以便绘制
    points = [(int(point[0]), int(point[1])) for point in points]
    center = (int(center[0]), int(center[1]))

    # 绘制三个点
    for point in points:
        cv2.circle(image, point, point_radius, point_color, -1)

    # 绘制圆心
    cv2.circle(image, center, center_radius, center_color, -1)

    # 绘制圆
    cv2.circle(image, center, int(radius), circle_color, circle_thickness)

    # 显示图像
    cv2.imshow("Points and Circle Center", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()




############################################################
# 示例使用
############################################################

P = [[10.0, 20.0], [10.0, 0.0], [20.0, 10.0]]
Q = [[100.0, 200.0], [100.0, 0.0], [200.0, 100.0]]

# 求仿射变换矩阵
Matrix1 = compute_affine_matrix(P, Q)
print(Matrix1)

points = [[10.0, 20.0], [10.0, 0.0], [20.0, 10.0]]  # 输入点列表

# 求仿射变换后的点
transformed_points = affine_transform_points(Matrix1,points)
print("仿射变换后的点:", transformed_points)


# 求圆心
center, radius = find_circle_center(transformed_points)
print("圆心O的坐标:", center)
print("半径:", radius)

# 可视化
visualize_points_and_center(transformed_points, center, radius)