import asyncio
import websockets
from datetime import datetime
import time
import serial
from pymodbus.client import ModbusSerialClient
from camera import *
import json
import base64
import threading
# import schedule
import os
import cv2
import numpy as np
from utils import *
import socket

global cameras, deviceList, frames, KeyNumList
global type, angle, cam
current_task = None  # 用于存储当前的定时任务
jpg_as_text = ""
timings = {}

# 存储所有客户端连接的集合
connected_clients = set()


#
# client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_s.connect(("192.168.1.110", 8501))
#
# def SCWR(S=""):
#     client_s.send(S.encode("utf-8"))
#     recv_content = client_s.recv(1024)
#     return recv_content.decode("utf-8")
#
# # 读取
# def SR(S1):
#     return SCWR(f"RDS {S1} 1\r\n").strip("\r\n")
#
# # 写入
# def SW(S1,S2):
#     return SCWR(f"WRS {S1} 1 {S2}\r\n").strip("\r\n")
#
# def timing(func):
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time()
#         elapsed_time = end_time - start_time
#         timings[func.__name__] = elapsed_time
#         print(f"{func.__name__} 执行时间: {elapsed_time} 秒")
#         return result
#     return wrapper
#
# @timing
# def scanPort(trigger_pos, function_plc_pos, return_pos, function_pc_pos,return_status_pos):
#     if trigger_pos == 59000:
#         camID = 1
#     elif trigger_pos == 59100:
#         camID = 2
#     elif trigger_pos == 59200:
#         camID = 3
#     else:
#         camID = 0
#
#     # 触发状态查询： 0=未触发 1=触发
#     trigger = "DM" + str(trigger_pos)
#     trigger_status = int(SR(trigger))
#     if trigger_status == 1:
#         # 重置触发状态
#         SW(trigger, 0)
#
#         # 读取功能码
#         func_code = "DM" + str(function_plc_pos)
#         plc_function_code = int(SR(func_code))
#         match plc_function_code:
#             case 1:
#                 print("复位指令")
#                 reset(return_pos,function_pc_pos,plc_function_code,return_status_pos)
#             case 4:
#                 print("配方切换指令")
#                 Recipe_switching(return_pos,function_pc_pos,plc_function_code,return_status_pos)
#             case 5:
#                 print("标定指令")
#                 calibration()
#             case 6:
#                 print("拍目标指令")
#             case 7:
#                 print("拍对象指令")
#                 match camID:
#                     case 0:
#                         return
#                     case 1:
#                         object_location = int(SR("DM59002"))
#                         if object_location == 1:
#                             feed_left_pic = Use_Addr_GetImg(trigger_pos, cameras, KeyNumList)
#                             feed_left_img = frame_encode(feed_left_pic, 'feed_left_img')
#                             # 获取当前事件循环
#                             loop = asyncio.get_event_loop()
#                             # 假设我们想要给特定的客户端发送消息
#                             client_id = next(iter(connected_clients), None)  # 假设我们选择第一个连接的客户端
#                             if client_id:
#                                 # 在事件循环中安排异步函数的执行
#                                 print(client_id)
#                                 loop.create_task(send_message_to_specific_client(client_id, feed_left_img))
#
#                         elif object_location == 2:
#                             feed_right_pic = Use_Addr_GetImg(trigger_pos, cameras, KeyNumList)
#                             feed_right_img = frame_encode(feed_right_pic, 'feed_right_img')
#                         else:
#                             return
#                     case 2:
#                         align_pic1 = Use_Addr_GetImg(trigger_pos, cameras, KeyNumList)
#                     case 3:
#                         align_pic2 = Use_Addr_GetImg(trigger_pos, cameras, KeyNumList)
#
#                 # 返回状态： 0=未返回 1=返回
#                 SW("DM59020", 1)
#                 # 功能码要和PLC相同
#                 SW("DM59021", plc_function_code)
#                 # 返回状态： 1=OK 2=NG
#                 SW("DM59022", 1)
#             case 8:
#                 print("多次对位指令")
#             case 10:
#                 print("移动循环指令")
#             case 13:
#                 print("1次对位指令")
#             case _:
#                 print("默认执行指令")
#     else:
#         return

def reset(return_pos, function_pc_pos, plc_function_code, return_status_pos):
    # 复位操作

    # 返回状态： 0=未返回 1=返回
    com.write_register(return_pos, 1, 1)
    # 功能码要和PLC相同
    com.write_register(function_pc_pos, plc_function_code, 1)
    # 返回状态： 1=OK 2=NG
    com.write_register(return_status_pos, 1, 1)


def Recipe_switching(return_pos, function_pc_pos, plc_function_code, return_status_pos):
    # 配方号寄存器存储地址：59002
    Recipe_index = com.read_holding_registers(59002, 1, 1).registers[0]
    # 配方切换操作

    com.write_register(return_pos, 1, 1)
    com.write_register(function_pc_pos, plc_function_code, 1)
    com.write_register(return_status_pos, 1, 1)


def calibration():
    # 读取移动标志位、标定为编号（左边|右边）
    calibration_flag = com.read_holding_registers(59002, 1, 1).registers[0]
    # 读取X、Y、Q的值
    origin_X = com.read_holding_registers(59006, 1, 1).registers[0]
    origin_Y = com.read_holding_registers(59008, 1, 1).registers[0]
    origin_Q = com.read_holding_registers(59010, 1, 1).registers[0]

    if calibration_flag == 1:
        points = calibration_move(origin_X, origin_Y, origin_Q, 12, 45, True)
    elif calibration_flag == 2:
        points = calibration_move(origin_X, origin_Y, origin_Q, 12, 45, False)
    else:
        print("其他拍摄需求")

    global pic_points
    send_calibration_position(points, 2)

    if len(pic_points) == 6:
        P = points[:3]
        Q = pic_points[:3]
        matrix1 = compute_affine_matrix(P, Q)  # 得到第一次的矩阵matrix1

        M = pic_points[3:]
        N = affine_transform_points(matrix1, M)  # 得到三点的假真实坐标

        center, _ = find_circle_center(N)
        delta_x = center[0] - origin_X
        delta_y = center[1] - origin_Y

        Z = [(x + delta_x, y + delta_y) for x, y in P]
        True_matrix = compute_affine_matrix(Z, Q)
        if calibration_flag == 1:
            with open('./config/leftmatrix.json', 'w') as json_file:
                json.dump(True_matrix, json_file, indent=4)
            pass
        elif calibration_flag == 2:
            # 保存True_matrix为右边坐标系的变换矩阵
            pass
        else:
            print("其他拍摄需求")

    else:
        print("标定失败！")


def calibration_move(origin_X, origin_Y, origin_Q, pos_movement, angle_movement, left_or_right):
    initial_position = (origin_X, origin_Y, origin_Q)
    if left_or_right:
        first_position = (origin_X + pos_movement, origin_Y, origin_Q)
    else:
        first_position = (origin_X - pos_movement, origin_Y, origin_Q)
    second_position = (origin_X, origin_Y - pos_movement, origin_Q)
    third_position = (origin_X, origin_Y, origin_Q + angle_movement)
    forth_position = (origin_X, origin_Y, origin_Q - angle_movement)
    return [first_position, second_position, initial_position, third_position, forth_position, initial_position]


def send_calibration_position(True_points, interval):
    pic_points = []
    points = True_points

    def send_next_position():
        if points:
            move_flag = com.read_holding_registers(59002, 1, 1).registers[0]
            if move_flag == 1:
                com.write_register(59002, 0, 1)
                # 移动完成进行拍照
                feed_frame = Get_Frame_UseAddr(59000)
                # 得到图像中的定位点
                pic_point = Pic_Point_Locate(feed_frame)
                # 存入数组中
                pic_points.append(pic_point)
                X, Y, Q = points.pop(0)
                print(f"发送坐标: ({X}, {Y}, {Q})")
                com.write_register(59026, X, 1)
                com.write_register(59028, Y, 1)
                com.write_register(59030, Q, 1)
                com.write_register(59021, 10, 1)
                com.write_register(59020, 1, 1)
                threading.Timer(interval, send_next_position).start()
            elif move_flag == 2:
                print("移动失败！退出标定！")
                return
            else:
                threading.Timer(interval, send_next_position).start()
        else:
            if len(pic_points) == 6:
                position_algorithm(True_points, pic_points)
                print("标定坐标已经全部发送完成！")
            else:
                print("没有可继续执行的标定点！")
            return

    send_next_position()


def alignment_algorithm(frame, ROI_workpiece, ROI_target, workpiece_template, target_template, workpiece_point,
                        target_point):
    workpiece = frame[ROI_workpiece["ROI_y"]:ROI_workpiece["ROI_y"] + ROI_workpiece["ROI_h"],
                ROI_workpiece["ROI_x"]:ROI_workpiece["ROI_x"] + ROI_workpiece["ROI_w"]]
    target = frame[ROI_target["ROI_y"]:ROI_target["ROI_y"] + ROI_target["ROI_h"],
             ROI_target["ROI_x"]:ROI_target["ROI_x"] + ROI_target["ROI_w"]]
    workpiece_res = cv2.matchTemplate(workpiece, workpiece_template, cv2.TM_CCOEFF_NORMED)
    target_res = cv2.matchTemplate(target, target_template, cv2.TM_CCOEFF_NORMED)
    h1, w1 = workpiece_template.shape[:2]
    h2, w2 = target_template.shape[:2]
    _, max_val1, _, max_loc1 = cv2.minMaxLoc(workpiece_res)
    _, max_val2, _, max_loc2 = cv2.minMaxLoc(target_res)
    loc1 = tuple([a + b for a, b in zip(max_loc1, workpiece_point)])
    loc2 = tuple([a + b for a, b in zip(max_loc2, target_point)])
    if max_val1 > 0.1 and max_val2 > 0.1:
        top_left = loc1
        bottom_right = (top_left[0] + w1, top_left[1] + h1)
        workpiece_point_loc = tuple([a + b for a, b in zip(top_left, workpiece_point)])
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
        top_left = loc2
        bottom_right = (top_left[0] + w2, top_left[1] + h2)
        target_point_loc = tuple([a + b for a, b in zip(top_left, target_point)])
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
        cross_size = 10
        cv2.line(frame, (workpiece_point_loc[0] - cross_size, workpiece_point_loc[1]),
                 (workpiece_point_loc[0] + cross_size, workpiece_point_loc[1]), (0, 0, 255), 2)  # 水平线
        cv2.line(frame, (workpiece_point_loc[0], workpiece_point_loc[1] - cross_size),
                 (workpiece_point_loc[0], workpiece_point_loc[1] + cross_size), (0, 0, 255), 2)  # 垂直线
        cv2.line(frame, (target_point_loc[0] - cross_size, target_point_loc[1]),
                 (target_point_loc[0] + cross_size, target_point_loc[1]), (0, 0, 255), 2)  # 水平线
        cv2.line(frame, (target_point_loc[0], target_point_loc[1] - cross_size),
                 (target_point_loc[0], target_point_loc[1] + cross_size), (0, 0, 255), 2)  # 垂直线
        # cv2.imshow('detect_result', frame)
    diff_loc = target_point_loc - workpiece_point_loc
    return frame, diff_loc


def position_algorithm(A, B, O1, O2, P, Q):
    # 已知初始点A、B的坐标（分别在两个坐标系下得到） （左右）拍照中心O1、O2 (左右)当前产品点位P、Q
    diff = O2 - O1
    dx, dy = diff[0], diff[1]
    new_Q_x, new_Q_y = Q[0] - dx, Q[1] - dy
    new_Q = np.array(new_Q_x, new_Q_y)
    new_B_x, new_B_y = B[0] - dx, B[1] - dy
    new_B = np.array(new_B_x, new_B_y)
    # 计算向量AB和PQ
    AB = new_B - A
    PQ = new_Q - P
    # 计算向量AB与X轴的夹角theta
    theta_AB = np.arctan2(AB[1], AB[0])
    theta_PQ = np.arctan2(PQ[1], PQ[0])
    Delta_theta = theta_AB - theta_PQ
    # 规范化角度差，确保它在-pi到pi的范围内
    Delta_theta = (Delta_theta + np.pi) % (2 * np.pi) - np.pi
    Delta_theta_degrees = np.degrees(Delta_theta)
    direction = 0  #逆时针
    # 默认逆时针转，如果是顺时针，角度要取反
    if Delta_theta < 0:
        Delta_theta = -Delta_theta
        direction = 1

    R = np.array([[np.cos(Delta_theta), -np.sin(Delta_theta)], [np.sin(Delta_theta), np.cos(Delta_theta)]])
    new_P = np.dot(R, P - O1) + O1

    # 计算平移量
    T = new_P - A
    dis_X = T[0]
    dis_Y = T[1]

    return dis_X, dis_Y, Delta_theta_degrees, direction


def Pic_Point_Locate(frame):
    pass


def readPF(CameraID, Product_Name):
    # 根据CameraID对应文件夹
    PF_Path = "D:/code/AAA_AOI/PF/" + CameraID + "/" + Product_Name
    if not os.path.exists(PF_Path):
        print("路径不存在")
    else:
        for filename in os.listdir(PF_Path):
            file_path = os.path.join(PF_Path, filename)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename)
                if ext.lower() in ['.json', '.bmp']:
                    var_name = os.path.splitext(filename)[0]
                    if ext.lower() == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            globals()[var_name] = data
                    elif ext.lower() == '.bmp':
                        with open(file_path, 'rb') as f:
                            image_data = f.read()
                            globals()[var_name] = image_data


def init():
    # 定义全局可以使用的 串口、相机、设备列表、图片帧、相机和地址对应关系、进料相机地址、左侧检测相机地址、右侧检测相机地址、定时器任务
    global com, cameras, deviceList, frames, KeyNumList, feed_addr, left_addr, right_addr, feed_left_pic, feed_right_pic, align_pic1, align_pic2, angle

    # 进料相机、对位相机的画面全部为空
    feed_left_pic, feed_right_pic, align_pic1, align_pic2 = None, None, None, None

    # 判断是否存在配置文件KeyNumList
    if If_KeyNumList_Exist():
        KeyNumList = From_json_Get_KeyNumList()
    else:
        KeyNumList = -1

    # cameras, deviceList = InitCamera()
    # frames = {}
    # for i in range(deviceList.nDevNum):
    #     frame_name = f"frame{i}"
    #     frames[frame_name] = None


def updatePic(camera_frames):
    if not camera_frames:
        camera_frames = getFrame(deviceList, cameras, frames)
    encoded_frames = []
    for frame_name, frame in camera_frames.items():
        ret, img_encode = cv2.imencode('.jpg', frame)
        if not ret:
            print("图片编码失败")
            continue
        img_data = img_encode.tobytes()
        if img_data is not None:
            encoded_frames.append({
                'frame_name': frame_name,
                'img_data': base64.b64encode(img_data).decode('utf-8')
            })
    return encoded_frames


def getModeFrame(frames):
    encoded_frames = []
    for frame_name, frame in frames.items():
        ret, img_encode = cv2.imencode('.jpg', frame)
        if not ret:
            print("图片编码失败")
            continue
        img_data = img_encode.tobytes()
        if img_data is not None:
            encoded_frames.append({
                'frame_name': frame_name,
                'img_data': base64.b64encode(img_data).decode('utf-8')
            })
    return encoded_frames


def frame_encode(frame, frame_name):
    ret, img_encode = cv2.imencode('.jpg', frame)
    if not ret:
        print("图片编码失败")
        return None
    img_data = img_encode.tobytes()
    if img_data is not None:
        encode_frame = {
            'frame_name': frame_name,
            'img_data': base64.b64encode(img_data).decode('utf-8')
        }
        return encode_frame
    else:
        return None


# @timing
def connect():
    # 连接测试：链路 | 相机
    # res = int(SR("DM59004"))
    res = 1
    # 获得所有相机的图像，并返回encoded_frames数组
    encoded_frames = updatePic(None)
    if res == 1:
        return True, encoded_frames
    else:
        return False, encoded_frames


# def startDetect():
#     global timer
#     trigger_pos, function_plc_pos, return_pos, function_pc_pos,return_status_pos = 59000, 59001, 59020, 59021, 59022
#     scanPort(trigger_pos, function_plc_pos, return_pos, function_pc_pos,return_status_pos)
#     timer = threading.Timer(1, startDetect)
#     timer.start()

def stopDetect():
    global timer
    if timer is not None:
        timer.cancel()
        timer = None


def get_json_data(type, encoded_frames, params):
    data = {
        "type": type,  # 将 type 类型传入前端
        "data": encoded_frames,
        "params": params
    }
    return json.dumps(data)


#根据具体指定地址获取对应相机图像图像
def Get_Frame_UseAddr(addr):
    return Get_Frame_UseAddr(addr, cameras, KeyNumList)


#判断本地是否存在KeyNumList配置文件
def If_KeyNumList_Exist():
    directory_path = './config'  # 项目配置文件夹路径
    # 相机key和地址对应配置文件名字
    file_name = 'KeyNumList.json'
    # 构建完整文件路径
    file_path = os.path.join(directory_path, file_name)
    # 判断文件是否存在
    if os.path.isfile(file_path):
        print(f"{file_name} 文件存在于目录中。")
        return True
    else:
        print(f"{file_name} 文件不存在于目录中。")
        return False

#从本地配置读取相机对应关系:KeyNumList
def From_json_Get_KeyNumList():
    file_path = './config/keyNumList.json'  # 请将此替换为你的 JSON 文件路径
    # 从 JSON 文件中读取数据
    with open(file_path, 'r') as file:
        data = json.load(file)
    # 提取 KeyNumList 并转换为所需的字典格式
    List = {k: v for d in data['KeyNumList'] for k, v in d.items()}
    # 输出结果
    return List

#判断本地是否存在camParams配置文件
def If_CamParams_Exist():
    directory_path = './config'  # 项目配置文件夹路径
    # 相机key和地址对应配置文件名字
    file_name = 'camParams.json'
    # 构建完整文件路径
    file_path = os.path.join(directory_path, file_name)
    # 判断文件是否存在
    if os.path.isfile(file_path):
        print(f"{file_name} 文件存在于目录中。")
        return True
    else:
        print(f"{file_name} 文件不存在于目录中。")
        return False

#从本地配置读取相机对应关系:KeyNumList
def From_json_Get_CamParams():
    file_path = './config/camParams.json'  # 请将此替换为你的 JSON 文件路径
    # 从 JSON 文件中读取数据
    with open(file_path, 'r') as file:
        data = json.load(file)
        angleNum = data['angleNum']
        print("angleNum------------", angleNum)
    # # 提取 KeyNumList 并转换为所需的字典格式
    # List = {k: v for d in data['KeyNumList'] for k, v in d.items()}
    # 输出结果
    return angleNum

# 计算仿射变换矩阵
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


# 根据仿射变换矩阵求转换后的点
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


# 三点求圆
def find_circle_center(points):
    # 将输入点转换为numpy数组
    points = np.array(points, dtype=np.float32)

    # 使用cv2.minEnclosingCircle找到最小外接圆
    (x, y), radius = cv2.minEnclosingCircle(points)

    # 返回圆心坐标和半径
    center = (x, y)
    return center, radius


async def send_message_to_all(message):
    # 给所有客户端发送消息
    for client in connected_clients:
        if client.open:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                # 如果连接已关闭，从集合中移除
                connected_clients.remove(client)


async def send_message_to_specific_client(client_id, message):
    # 给特定的客户端发送消息
    if client_id in connected_clients and client_id.open:
        try:
            json_data = json.dumps(message)
            await client_id.send(json_data)
        except websockets.exceptions.ConnectionClosed:
            connected_clients.remove(client_id)


async def handler(websocket):
    # 将新的连接添加到集合中
    connected_clients.add(websocket)
    global type, angle, params, camera_frames
    async for message in websocket:
        type_message = json.loads(message)
        type = type_message.get('type')
        angle = type_message.get('angle')
        if angle is None:
            angle = -1
        # 获取属性传参
        params = type_message.get('params')
        # 初始化项目
        if type == "Init":
            init()

        # 建立连接：链路 | 相机
        elif type == "Connect":
            Port_connect, encoded_frames = connect()
            if Port_connect:
                await websocket.send('true')
            else:
                await websocket.send('false')
            for frame_data in encoded_frames:
                json_data = json.dumps(frame_data)
                await websocket.send(json_data)
        elif type == "CamSettingInit":
            # 发送摄像头数量
            # num_cameras = len(cameras)
            num_cameras = 1
            # print("摄像头数量:", num_cameras)
            # print("摄像头名称列表:", list(cameras.keys()))
            # 判断是否存在配置文件KeyNumList
            if If_CamParams_Exist():
                angle = From_json_Get_CamParams()
            else:
                angle = -1
            print("angle:", angle)
            params = [angle, 10000.00, 20000.00, 40, 50]
            json_data = get_json_data(type, num_cameras, params)
            await websocket.send(json_data)
        # 渲染相机画面
        elif type == "CamSetting":
            camera_frames = getFrame(deviceList, cameras, frames)
            encoded_frames = updatePic(camera_frames)
            json_data = get_json_data(type, encoded_frames, None)
            # 定时任务，每隔0.05秒发送一次图片
            start_periodic_task(websocket)
            await websocket.send(json_data)
        elif type == "ShowCamImg":
            camera_frames = getFrame(deviceList, cameras, frames)
            encoded_frames = updatePic(camera_frames)
            json_data = json.dumps(encoded_frames)
            # 定时任务，每隔0.05秒发送一次图片
            start_periodic_task(websocket)
            await websocket.send(json_data)
            # 。。。
        elif type == "UpdateModeImg1":
            frame = Use_Addr_GetFrame(59000, cameras, KeyNumList)
            encoded_frame = getModeFrame(frame)
            json_data = json.dumps(encoded_frame)
            await websocket.send(json_data)
        elif type == "UpdateModeImg2":
            encoded_frames = Use_Addr_GetFrame(59100, cameras, KeyNumList)
            json_data = json.dumps(encoded_frame)
            await websocket.send(json_data)
        elif type == "UpdateModeImg3":
            encoded_frames = Use_Addr_GetFrame(59200, cameras, KeyNumList)
            json_data = json.dumps(encoded_frame)
            await websocket.send(json_data)
        # 开始检测
        # elif type == "StartDetect":
        #     startDetect()
        # 停止检测
        elif type == "StopDetect":
            stopDetect()
        # 获取前端参数
        elif type == "Paramters":
            data_message = await websocket.recv()
            global All_paramters
            All_paramters = json.loads(data_message)
            print(All_paramters)
        # 设置图片旋转
        elif type == "RotateImage":
            if angle == -1:
                camera_frames = getFrame(deviceList, cameras, frames)
            elif angle in [0, 1, 2]:
                print("angle:", angle)
                # camera_frames = getRotateImage(deviceList, cameras, frames, angle, None)
            elif angle == 3:
                camera_frames = imageFlip(deviceList, cameras, frames, 1)
            elif angle == 4:
                camera_frames = imageFlip(deviceList, cameras, frames, 0)
            elif angle == 5:
                camera_frames = getRotateImage(deviceList, cameras, frames, 0, 1)
            elif angle == 6:
                camera_frames = getRotateImage(deviceList, cameras, frames, 0, 0)
            # encoded_frames = updatePic(camera_frames)
            # # 添加 type 项
            # json_data = get_json_data(type, encoded_frames, None)
            # start_periodic_task(websocket)
            # await websocket.send()
        # # 设置图片镜像翻转
        # elif type == "FlipImage":
        #     if flipParam == -1:
        #         camera_frames = getFrame(deviceList, cameras, frames)
        #     else:
        #         camera_frames = imageFlip(deviceList, cameras, frames, flipParam)
        #     encoded_frames = updatePic(camera_frames)
        #     # 添加 type 项
        #     json_data = get_json_data(type, encoded_frames, None)
        #     start_periodic_task(websocket)
        #     await websocket.send(json_data)
        # 设置曝光时间
        elif type == "ExposureTime":
            nRet = cameras['cam0'].IMV_SetDoubleFeatureValue("ExposureTime", float(params))
            if IMV_OK != nRet:
                print("Set ExposureTime value failed! ErrorCode[%d]" % nRet)
                return nRet
            start_periodic_task(websocket)
        # 设置亮度
        elif type == "Brightness":
            nRet = cameras['cam0'].IMV_SetIntFeatureValue("Brightness", int(params))
            if IMV_OK != nRet:
                print("Set Brightness value failed! ErrorCode[%d]" % nRet)
                return nRet
            start_periodic_task(websocket)
        # 设置对比度
        elif type == "Contrast":
            nRet = cameras['cam0'].IMV_SetIntFeatureValue("Contrast", int(params))
            if IMV_OK != nRet:
                print("Set Contras value failed! ErrorCode[%d]" % nRet)
                return nRet
            start_periodic_task(websocket)
        elif type == "saveParameters":
            print("angle---------", angle)
            data = {"angleNum": angle}
            # 保存到 JSON 文件
            json_file_path = "./config/camParams.json"
            # 写入 JSON 文件
            with open(json_file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            print(f"数据已保存到 {json_file_path}")
            # await websocket.send()
        elif type == "Close":
            stopCamera(deviceList, cameras)
        else:
            print(message)
            pass

async def periodic_task(websocket):
    global current_task, camera_frames
    while True:
        print("定时器任务执行-- ", "type = ", type, "angle = ", angle)
        if angle == -1:
            camera_frames = getFrame(deviceList, cameras, frames)
        elif angle in [0, 1, 2]:
            print("angle:", angle)
            # camera_frames = getRotateImage(deviceList, cameras, frames, angle, None)
        elif angle == 3:
            camera_frames = imageFlip(deviceList, cameras, frames, 1)
        elif angle == 4:
            camera_frames = imageFlip(deviceList, cameras, frames, 0)
        elif angle == 5:
            camera_frames = getRotateImage(deviceList, cameras, frames, 0, 1)
        elif angle == 6:
            camera_frames = getRotateImage(deviceList, cameras, frames, 0, 0)
        encoded_frames = updatePic(camera_frames)
        json_data = get_json_data(type, encoded_frames, None)
        await websocket.send(json_data)
        await asyncio.sleep(0.05)  # 每隔5秒执行一次

def start_periodic_task(websocket):
    global current_task 
    # 如果当前有任务在运行，则取消它
    if current_task and not current_task.done():
        current_task.cancel()
    # 启动新的定时任务
    current_task = asyncio.create_task(periodic_task(websocket))

async def main():
    async with websockets.serve(handler, "localhost", 9999):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
