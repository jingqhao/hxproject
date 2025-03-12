from camera import *
import json
import os

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

global cameras,deviceList,frames,KeyNumList

if If_KeyNumList_Exist():
    KeyNumList = From_json_Get_KeyNumList()
else :
    KeyNumList = -1

cameras,deviceList = InitCamera()
frames = {}
for i in range(deviceList.nDevNum):
    frame_name = f"frame{i}"
    frames[frame_name] = None


frame1 = Use_Addr_GetFrame(59200,cameras,KeyNumList)
cv2.imshow('frame', frame1)

# 等待按键，然后关闭所有窗口
cv2.waitKey(0)
cv2.destroyAllWindows()
