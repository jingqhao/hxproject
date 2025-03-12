# -- coding: utf-8 --
import numpy as np
import matplotlib.pyplot as plt
from camera import *
import json
import sys
import datetime
from ctypes import *

sys.path.append("../MVSDK")
from IMVApi import *
global cameras,deviceList,frames,KeyNumList
frames = {}
MONO_CHANNEL_NUM=1
RGB_CHANNEL_NUM=3
BGR_CHANNEL_NUM=3
rotated_image = None


def InitCamera():
    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll
    nWidth = c_uint()
    nHeight = c_uint()
    nRet = MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    if IMV_OK != nRet:
        print("Enumeration devices failed! ErrorCode", nRet)
        sys.exit()
    if deviceList.nDevNum == 0:
        print("find no device!")
        sys.exit()
    print("deviceList size is", deviceList.nDevNum)

    cameras = {}
    for i in range(deviceList.nDevNum):
        cam_name = f"cam{i}"
        cam = MvCamera()
        nRet = cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(i)))
        if IMV_OK != nRet:
            print("Create devHandle failed! ErrorCode", nRet)
            sys.exit()
        cameras[cam_name] = cam

    for i in range(deviceList.nDevNum):
        cam_name = f"cam{i}"
        print(cam_name)
        # 打开相机
        nRet = cameras[cam_name].IMV_Open()
        if IMV_OK != nRet:
            print("Open devHandle failed! ErrorCode", nRet)
            sys.exit()

            # 通用属性设置:设置触发模式为off
        nRet = IMV_OK
        nRet = cameras[cam_name].IMV_SetEnumFeatureSymbol("TriggerSource", "Software")
        if IMV_OK != nRet:
            print("Set triggerSource value failed! ErrorCode[%d]" % nRet)
            sys.exit()

        nRet = cameras[cam_name].IMV_SetEnumFeatureSymbol("TriggerSelector", "FrameStart")
        if IMV_OK != nRet:
            print("Set triggerSelector value failed! ErrorCode[%d]" % nRet)
            sys.exit()

        nRet = cameras[cam_name].IMV_SetEnumFeatureSymbol("TriggerMode", "Off")
        if IMV_OK != nRet:
            print("Set triggerMode value failed! ErrorCode[%d]" % nRet)
            sys.exit()

        # 开始拉流
        nRet = cameras[cam_name].IMV_StartGrabbing()
        if IMV_OK != nRet:
            print("Start grabbing failed! ErrorCode", nRet)
            sys.exit()

    return cameras, deviceList

def imageFlip(cam, frame, imageFlipType):
    global grayByteArray, cvImage, image_array
    stPixelConvertParam = IMV_PixelConvertParam()
    stFlipImageParam = IMV_FlipImageParam()
    pConvertBuf = None
    nChannelNum = 0

    memset(byref(stFlipImageParam), 0, sizeof(stFlipImageParam))
    if IMV_EPixelType.gvspPixelMono8 == frame.frameInfo.pixelFormat:
        stFlipImageParam.pSrcData = frame.pData
        stFlipImageParam.nSrcDataLen = frame.frameInfo.width * frame.frameInfo.height * MONO_CHANNEL_NUM
        stFlipImageParam.ePixelFormat = frame.frameInfo.pixelFormat
        nChannelNum = MONO_CHANNEL_NUM
    elif IMV_EPixelType.gvspPixelBGR8 == frame.frameInfo.pixelFormat:
        stFlipImageParam.pSrcData = frame.pData
        stFlipImageParam.nSrcDataLen = frame.frameInfo.width * frame.frameInfo.height * BGR_CHANNEL_NUM
        stFlipImageParam.ePixelFormat = frame.frameInfo.pixelFormat
        nChannelNum = BGR_CHANNEL_NUM
    elif IMV_EPixelType.gvspPixelRGB8 == frame.frameInfo.pixelFormat:
        stFlipImageParam.pSrcData = frame.pData
        stFlipImageParam.nSrcDataLen = frame.frameInfo.width * frame.frameInfo.height * RGB_CHANNEL_NUM
        stFlipImageParam.ePixelFormat = frame.frameInfo.pixelFormat
        nChannelNum = RGB_CHANNEL_NUM

    # MONO8/RGB24/BGR24以外的格式都转化成BGR24
    else:
        nConvertBufSize = frame.frameInfo.width * frame.frameInfo.height * BGR_CHANNEL_NUM;
        pConvertBuf = (c_ubyte * nConvertBufSize)()
        memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))
        stPixelConvertParam.nWidth = frame.frameInfo.width
        stPixelConvertParam.nHeight = frame.frameInfo.height
        stPixelConvertParam.ePixelFormat = frame.frameInfo.pixelFormat
        stPixelConvertParam.pSrcData = frame.pData
        stPixelConvertParam.nSrcDataLen = frame.frameInfo.size
        stPixelConvertParam.nPaddingX = frame.frameInfo.paddingX
        stPixelConvertParam.nPaddingY = frame.frameInfo.paddingY
        stPixelConvertParam.eBayerDemosaic = IMV_EBayerDemosaic.demosaicNearestNeighbor
        stPixelConvertParam.eDstPixelFormat = IMV_EPixelType.gvspPixelBGR8
        stPixelConvertParam.pDstBuf = pConvertBuf
        stPixelConvertParam.nDstBufSize = nConvertBufSize

        nRet = cam.IMV_PixelConvert(stPixelConvertParam)
        if IMV_OK == nRet:
            stFlipImageParam.pSrcData = pConvertBuf
            stFlipImageParam.nSrcDataLen = stPixelConvertParam.nDstDataLen
            stFlipImageParam.ePixelFormat = IMV_EPixelType.gvspPixelBGR8
            nChannelNum = BGR_CHANNEL_NUM
        else:
            stFlipImageParam.pSrcData = None
            print("image convert to BGR8 failed! ErrorCode[%d]", nRet)
    bEnd = True
    while bEnd:
        if None == stFlipImageParam.pSrcData:
            print("stFlipImageParam pSrcData is NULL!")
            break
        nFlipBufSize = frame.frameInfo.width * frame.frameInfo.height * nChannelNum
        pFlipBuf = (c_ubyte * nFlipBufSize)()

        stFlipImageParam.nWidth = frame.frameInfo.width
        stFlipImageParam.nHeight = frame.frameInfo.height
        stFlipImageParam.eFlipType = imageFlipType
        stFlipImageParam.pDstBuf = pFlipBuf
        stFlipImageParam.nDstBufSize = nFlipBufSize

        nRet = cam.IMV_FlipImage(stFlipImageParam)

        if IMV_OK == nRet:
            if IMV_EFlipType.typeFlipVertical == imageFlipType:
                print("Image vertical flip successfully!")
                FileName = "../verticalFlip.bin"
                hFile = open(FileName.encode('ascii'), "wb")
            else:
                print("Image horizontal flip successfully!")
                FileName = "../horizontalFlip.bin"
                hFile = open(FileName.encode('ascii'), "wb")

            try:
                # 创建缓冲区 (c_buffer):
                img_buff = c_buffer(b'\0', stFlipImageParam.nDstBufSize)
                # 内存数据复制, 将 stFlipImageParam.pDstBuf 指向的内存中的图像数据复制到 img_buff 缓冲区中
                memmove(img_buff, stFlipImageParam.pDstBuf, stFlipImageParam.nDstBufSize)
                # 写入文件
                hFile.write(img_buff)
                # 使用 bytearray 函数将 img_buff 中的图像数据转换为一个字节数组 grayByteArray
                grayByteArray = bytearray(img_buff)
                # 转换为 NumPy 数组并重塑形状
                cvImage = numpy.array(grayByteArray).reshape(stFlipImageParam.nHeight, stFlipImageParam.nWidth)
            except:
                print("save file executed failed")
            finally:
                hFile.close()

        else:
            if IMV_EFlipType.typeFlipVertical == imageFlipType:
                print("Image vertical flip failed! ErrorCode[%d]", nRet)
            else:
                print("Image horizontal flip failed! ErrorCode[%d]", nRet)
            if None != pConvertBuf:
                del pConvertBuf
                pConvertBuf = None
            if None != pFlipBuf:
                del pFlipBuf
        bEnd = False
    return cvImage
def getFrame(deviceList, cameras, frames):
    global rotated_image
    frame = IMV_Frame()
    stPixelConvertParam = IMV_PixelConvertParam()
    for i in range(deviceList.nDevNum):
        cam_name = f"cam{i}"
        frame_name = f"frame{i}"
        nRet = cameras[cam_name].IMV_GetFrame(frame, 500)
        if IMV_OK != nRet:
            print("getFrame fail! Timeout:[1000]ms")
            continue
        else:
            print("getFrame success BlockId = [" + str(frame.frameInfo.blockId) + "], get frame time: " + str(
                datetime.datetime.now()))

        if None == byref(frame):
            print("pFrame is NULL!")
            continue

        # 图像旋转
        print( "BlockId (%d) pixelFormat (%d), Start image rotate..." % (frame.frameInfo.blockId, frame.frameInfo.pixelFormat))
        cvImage = imageFlip(cameras[cam_name], frame, 0)

        rotated_image = process_image_stream(cvImage, angle=90)
        # display_image(rotated_image)
        # frames[frame_name] = cvImage
    # return frames
    return rotated_image
def process_image_stream(image_array, angle):
    #
    # # 获取图像的宽高
    # (h, w) = image_array.shape[:2]
    # (cx, cy) = (w // 2, h // 2)
    #
    # # 计算旋转矩阵
    # M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    #
    # # 执行旋转操作
    # rotated_image = cv2.warpAffine(image_array, M, (w, h))

    horizontal_flip = cv2.flip(cvImage, 1)

    # 竖直镜像翻转
    vertical_flip = cv2.flip(cvImage, 0)

    # cv2.imshow("Original", cvImage)
    # cv2.imshow("Horizontal Flip", horizontal_flip)
    cv2.imshow("Vertical Flip", vertical_flip)
    # 等待按键，然后关闭所有窗口
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return rotated_image

if __name__ == "__main__":
    deviceList = IMV_DeviceList()
    interfaceType = IMV_EInterfaceType.interfaceTypeAll
    # frame = IMV_Frame()
    # 枚举设备
    nRet = MvCamera.IMV_EnumDevices(deviceList, interfaceType)
    if IMV_OK != nRet:
        print("Enumeration devices failed! ErrorCode", nRet)
        sys.exit()
    if deviceList.nDevNum == 0:
        print("find no device!")
        sys.exit()

    print("deviceList size is", deviceList.nDevNum)

    cameras, deviceList = InitCamera()


    def From_json_Get_KeyNumList():
        file_path = '../config/keyNumList.json'  # 请将此替换为你的 JSON 文件路径
        # 从 JSON 文件中读取数据
        with open(file_path, 'r') as file:
            data = json.load(file)
        # 提取 KeyNumList 并转换为所需的字典格式
        List = {k: v for d in data['KeyNumList'] for k, v in d.items()}
        # 输出结果
        return List
    # frames = getFrame(deviceList, cameras, frames)
    # 转换 BGR 图像为 RGB（Matplotlib 使用 RGB 模式）
    image = getFrame(deviceList, cameras, frames)
    # image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 使用 Matplotlib 显示图像
    # plt.imshow(image_rgb)
    # plt.axis('off')  # 隐藏坐标轴
    # plt.show()

    # for frame_name, frame in frames.items():
    #     cv2.imshow('frame', frame)
    #     # 等待按键，然后关闭所有窗口
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()

