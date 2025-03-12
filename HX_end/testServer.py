import asyncio
import base64
import os
import threading
import time

import websockets

from utils import *

global cameras,deviceList,frames,KeyNumList
global type, angle, cam
current_task = None  # 用于存储当前的定时任务
jpg_as_text = ""
timings = {}

def timing(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        timings[func.__name__] = elapsed_time
        print(f"{func.__name__} 执行时间: {elapsed_time} 秒")
        return result
    return wrapper

@timing
def scanPort(trigger_pos, function_plc_pos, return_pos, function_pc_pos,return_status_pos):
    # 触发状态查询： 0=未触发 1=触发
    # trigger_pos = 59000 function_pos = 59001
    trigger_status = com.read_holding_registers(trigger_pos, 1, 1).registers[0]
    print(trigger_status)
    if trigger_status == 1:
        com.write_register(trigger_pos, 0, 1)
        plc_function_code = com.read_holding_registers(function_plc_pos, 1, 1).registers[0]
        match plc_function_code:
            case 1:
                print("复位指令")
                reset(return_pos,function_pc_pos,plc_function_code,return_status_pos)
            case 4:
                print("配方切换指令")
                Recipe_switching(return_pos,function_pc_pos,plc_function_code,return_status_pos)
            case 5:
                print("标定指令")
                calibration()

            case 6:
                print("拍目标指令")

            case 7:
                print("拍对象指令")

            case 8:
                print("多次对位指令")

            case 10:
                print("移动循环指令")

            case 13:
                print("1次对位指令")

            case _:
                print("默认执行指令")
    else:
        return


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
    # 弹出标定确认框


    # 读取移动标志位、标定为编号（左边|右边）
    calibration_flag = com.read_holding_registers(59002, 1, 1).registers[0]
    # 读取X、Y、Q的值
    origin_X = com.read_holding_registers(59006, 1, 1).registers[0]
    origin_Y = com.read_holding_registers(59008, 1, 1).registers[0]
    origin_Q = com.read_holding_registers(59010, 1, 1).registers[0]

    if calibration_flag == 1:
        points = calibration_move(origin_X,origin_Y,origin_Q, 12, 45, True)
    elif calibration_flag == 2:
        points = calibration_move(origin_X,origin_Y,origin_Q, 12, 45, False)
    else:
        print("其他拍摄需求")

    send_calibration_position(points,2)

def calibration_move(origin_X,origin_Y,origin_Q,pos_movement,angle_movement,left_or_right):
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

def alignment_algorithm(frame,ROI_workpiece,ROI_target,workpiece_template,target_template,workpiece_point,target_point):
    workpiece = frame[ROI_workpiece["ROI_y"]:ROI_workpiece["ROI_y"]+ROI_workpiece["ROI_h"], ROI_workpiece["ROI_x"]:ROI_workpiece["ROI_x"]+ROI_workpiece["ROI_w"]]
    target = frame[ROI_target["ROI_y"]:ROI_target["ROI_y"]+ROI_target["ROI_h"], ROI_target["ROI_x"]:ROI_target["ROI_x"]+ROI_target["ROI_w"]]
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
        cv2.rectangle(frame, top_left, bottom_right, (0,255,0), 2)
        top_left = loc2
        bottom_right = (top_left[0] + w2, top_left[1] + h2)
        target_point_loc = tuple([a + b for a, b in zip(top_left, target_point)])
        cv2.rectangle(frame, top_left, bottom_right, (0,255,0), 2)
        cross_size = 10
        cv2.line(frame, (workpiece_point_loc[0] - cross_size, workpiece_point_loc[1]), (workpiece_point_loc[0] + cross_size, workpiece_point_loc[1]), (0, 0, 255), 2)  # 水平线
        cv2.line(frame, (workpiece_point_loc[0], workpiece_point_loc[1] - cross_size), (workpiece_point_loc[0], workpiece_point_loc[1] + cross_size), (0, 0, 255), 2)  # 垂直线
        cv2.line(frame, (target_point_loc[0] - cross_size, target_point_loc[1]), (target_point_loc[0] + cross_size, target_point_loc[1]), (0, 0, 255), 2)  # 水平线
        cv2.line(frame, (target_point_loc[0], target_point_loc[1] - cross_size), (target_point_loc[0], target_point_loc[1] + cross_size), (0, 0, 255), 2)  # 垂直线
        # cv2.imshow('detect_result', frame)
    diff_loc = target_point_loc - workpiece_point_loc
    return frame,diff_loc

def position_algorithm(True_points, Pic_points):
    pass

def Pic_Point_Locate(frame):
    pass

def init():
    # 定义全局可以使用的 串口、相机、设备列表、图片帧、相机和地址对应关系、进料相机地址、左侧检测相机地址、右侧检测相机地址、定时器任务
    global com,cameras,deviceList,frames,KeyNumList,feed_addr,left_addr,right_addr

    # 判断是否存在配置文件KeyNumList
    if If_KeyNumList_Exist():
        KeyNumList = From_json_Get_KeyNumList()
    else :
        KeyNumList = -1

    # com = ModbusSerialClient(method='rtu', port='COM3', baudrate=115200, parity='N', stopbits=1, bytesize=8)
    cameras,deviceList = InitCamera()
    frames = {}
    for i in range(deviceList.nDevNum):
        frame_name = f"frame{i}"
        frames[frame_name] = None

def Get_Frame_UseAddr(addr):
    return Use_Addr_GetFrame(addr, cameras, KeyNumList)

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

def From_json_Get_KeyNumList():
    file_path = './config/keyNumList.json'  # 请将此替换为你的 JSON 文件路径
    # 从 JSON 文件中读取数据
    with open(file_path, 'r') as file:
        data = json.load(file)
    # 提取 KeyNumList 并转换为所需的字典格式
    List = {k: v for d in data['KeyNumList'] for k, v in d.items()}
    # 输出结果
    return List

def On_open():
    if If_KeyNumList_Exist():
        KeyNumList = From_json_Get_KeyNumList()
    else:
        KeyNumList = -1

    cameras, deviceList = InitCamera()
    frames = {}
    for i in range(deviceList.nDevNum):
        frame_name = f"frame{i}"
        frames[frame_name] = None

    frame1 = Use_Addr_GetFrame(59200, cameras, KeyNumList)

    # 假设 cvImage 是你在代码中生成的 numpy 数组
    # 将 cvImage 转换为 JPEG 格式
    _, buffer = cv2.imencode('.jpg', frame1)
    # 将 JPEG 格式的图像转换为字节
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')

    # 现在 jpg_as_text 包含 cvImage 的 base64 编码
    print(jpg_as_text)

    # cv2.imshow('frame', frame1)
    #
    # # 等待按键，然后关闭所有窗口
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

def updatePic(camera_frames):
    # camera_frames = getFrame(deviceList,cameras,frames)
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

def startDetect():
    global timer
    trigger_pos, function_plc_pos, return_pos, function_pc_pos,return_status_pos = 59000, 59001, 59020, 59021, 59022
    scanPort(trigger_pos, function_plc_pos, return_pos, function_pc_pos,return_status_pos)
    timer = threading.Timer(1, startDetect)
    timer.start()

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

async def handler(websocket):
    global type, angle, params
    async for message in websocket:
        type_message = json.loads(message)
        type = type_message.get('type')
        # 获取旋转角度
        angle = type_message.get('angle')
        if angle is None:
            angle = -1
        # 获取属性传参
        params = type_message.get('params')
        if type == "Init":
            init()
            # 发送摄像头数量
            num_cameras = len(cameras)
            print("摄像头数量:", num_cameras)
            print("摄像头名称列表:", list(cameras.keys()))
            params = [50000.00, 40, 50]
            json_data = get_json_data(type, num_cameras, params)
            await websocket.send(json_data)
        elif type == "Connect":
            camera_frames = getFrame(deviceList, cameras, frames)
            encoded_frames = updatePic(camera_frames)
            json_data = get_json_data(type, encoded_frames, None)
            print("json_data: ", json_data)
            # 定时任务，每隔0.05秒发送一次图片
            start_periodic_task(websocket)
            await websocket.send(json_data)
        elif type == "StartDetect":
            startDetect()
        elif type == "StopDetect":
            stopDetect()
        elif type == "Paramters":
            # data_message = await websocket.recv()
            # global All_paramters
            # All_paramters = json.loads(data_message)

            print("2222222222222")
        elif type == "RotateImage":
            if angle == -1:
                camera_frames = getFrame(deviceList, cameras, frames)
            else:
                camera_frames = getRotateImage(deviceList, cameras, frames, angle)
            encoded_frames = updatePic(camera_frames)
            # 添加 type 项
            json_data = get_json_data(type, encoded_frames, None)
            start_periodic_task(websocket)
            await websocket.send(json_data)
        # 设置曝光时间
        elif type == "ExposureTime":
            print("设置曝光时间为",params)
            nRet = cameras['cam0'].IMV_SetDoubleFeatureValue("ExposureTime", float(params))
            if IMV_OK != nRet:
                print("Set ExposureTime value failed! ErrorCode[%d]" % nRet)
                return nRet
            start_periodic_task(websocket)
        # 设置亮度
        elif type == "Brightness":
            print("设置亮度")
            nRet = cameras['cam0'].IMV_SetIntFeatureValue("Brightness", int(params))
            if IMV_OK != nRet:
                print("Set Brightness value failed! ErrorCode[%d]" % nRet)
                return nRet
            start_periodic_task(websocket)
        # 设置对比度
        elif type == "Contrast":
            print("设置对比度")
            nRet = cameras['cam0'].IMV_SetIntFeatureValue("Contrast", int(params))
            if IMV_OK != nRet:
                print("Set Contras value failed! ErrorCode[%d]" % nRet)
                return nRet
            start_periodic_task(websocket)
        elif type == "Close":
            print("关闭相机")
            stopCamera(deviceList, cameras)
        else:
            print(message)
            pass

async def periodic_task(websocket):
    global current_task    # 声明使用全局变量
    while True:
        print("定时器任务执行-- ", "type = ", type, "angle = ", angle)
        if angle == -1:
            camera_frames = getFrame(deviceList, cameras, frames)
        else:
            camera_frames = getRotateImage(deviceList, cameras, frames, angle)
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
    async with websockets.serve(handler, "localhost", 9000):
        await asyncio.Future()

if __name__ == "__main__":
        asyncio.run(main())

