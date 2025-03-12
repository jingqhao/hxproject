# -- coding: utf-8 --

import sys
from ctypes import *
import datetime
import numpy
import cv2
import gc

from IMVApi import *

def InitCamera():
    deviceList=IMV_DeviceList()
    interfaceType=IMV_EInterfaceType.interfaceTypeAll
    nWidth=c_uint()
    nHeight=c_uint()
    nRet=MvCamera.IMV_EnumDevices(deviceList,interfaceType)
    if IMV_OK != nRet:
        print("Enumeration devices failed! ErrorCode",nRet)
        sys.exit()
    if deviceList.nDevNum == 0:
        print ("find no device!")
        sys.exit()
    print("deviceList size is",deviceList.nDevNum)
    
    cameras = {}
    for i in range(deviceList.nDevNum):
        cam_name = f"cam{i}"
        cam = MvCamera()
        nRet=cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex,byref(c_void_p(i)))
        if IMV_OK != nRet:
            print("Create devHandle failed! ErrorCode",nRet)
            sys.exit()
        cameras[cam_name] = cam

    for i in range(deviceList.nDevNum):
        cam_name = f"cam{i}"
        print(cam_name)
        # 打开相机
        nRet=cameras[cam_name].IMV_Open()
        if IMV_OK != nRet:
            print("Open devHandle failed! ErrorCode",nRet)
            sys.exit()     
    
        # 通用属性设置:设置触发模式为off
        nRet=IMV_OK
        nRet=cameras[cam_name].IMV_SetEnumFeatureSymbol("TriggerSource","Software")
        if IMV_OK != nRet:
            print("Set triggerSource value failed! ErrorCode[%d]" % nRet)
            sys.exit()
            
        nRet=cameras[cam_name].IMV_SetEnumFeatureSymbol("TriggerSelector","FrameStart")
        if IMV_OK != nRet:
            print("Set triggerSelector value failed! ErrorCode[%d]" % nRet)
            sys.exit()

        nRet=cameras[cam_name].IMV_SetEnumFeatureSymbol("TriggerMode","Off")
        if IMV_OK != nRet:
            print("Set triggerMode value failed! ErrorCode[%d]" % nRet)
            sys.exit()

        # 相机属性设置:设置初始曝光时间为8.00ms（曝光时间下限8.00，上限1000000.00）
        nRet = cameras[cam_name].IMV_SetDoubleFeatureValue("ExposureTime", 500000.00)
        if IMV_OK != nRet:
            print("Set ExposureTime value failed! ErrorCode[%d]" % nRet)
            return nRet

        # 相机属性设置:设置初始亮度为30
        nRet = cameras[cam_name].IMV_SetIntFeatureValue("Brightness", 40)
        if IMV_OK != nRet:
            print("Set Brightness value failed! ErrorCode[%d]" % nRet)
            return nRet

        # 相机属性设置:设置初始对比度为50
        nRet = cameras[cam_name].IMV_SetIntFeatureValue("Contrast", 50)
        if IMV_OK != nRet:
            print("Set Contrast value failed! ErrorCode[%d]" % nRet)
            return nRet

        # 开始拉流
        nRet=cameras[cam_name].IMV_StartGrabbing()
        if IMV_OK != nRet:
            print("Start grabbing failed! ErrorCode",nRet)
            sys.exit()

    return cameras,deviceList

def getFrame(deviceList, cameras, frames):
    frame = IMV_Frame()
    stPixelConvertParam=IMV_PixelConvertParam()
    for i in range(deviceList.nDevNum):
        cam_name = f"cam{i}"
        frame_name = f"frame{i}"
        nRet = cameras[cam_name].IMV_GetFrame(frame, 1000)
        if  IMV_OK != nRet :
            print("getFrame fail! Timeout:[1000]ms")
            continue
        else:
            print("getFrame success BlockId = [" + str(frame.frameInfo.blockId) + "], get frame time: " + str(datetime.datetime.now()))
        
        if  None==byref(frame) :
            print("pFrame is NULL!")
            continue
        # 给转码所需的参数赋值

        if IMV_EPixelType.gvspPixelMono8==frame.frameInfo.pixelFormat:
            nDstBufSize=frame.frameInfo.width * frame.frameInfo.height
        else:
            nDstBufSize=frame.frameInfo.width * frame.frameInfo.height*3
        
        pDstBuf=(c_ubyte*nDstBufSize)()
        memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))
        
        stPixelConvertParam.nWidth = frame.frameInfo.width
        stPixelConvertParam.nHeight = frame.frameInfo.height
        stPixelConvertParam.ePixelFormat = frame.frameInfo.pixelFormat
        stPixelConvertParam.pSrcData = frame.pData
        stPixelConvertParam.nSrcDataLen = frame.frameInfo.size
        stPixelConvertParam.nPaddingX = frame.frameInfo.paddingX
        stPixelConvertParam.nPaddingY = frame.frameInfo.paddingY
        stPixelConvertParam.eBayerDemosaic = IMV_EBayerDemosaic.demosaicNearestNeighbor
        stPixelConvertParam.eDstPixelFormat = frame.frameInfo.pixelFormat
        stPixelConvertParam.pDstBuf = pDstBuf
        stPixelConvertParam.nDstBufSize = nDstBufSize

        nRet = cameras[cam_name].IMV_ReleaseFrame(frame)
        if IMV_OK != nRet:
            print("Release frame failed! ErrorCode[%d]\n", nRet)
            sys.exit()
        
        if stPixelConvertParam.ePixelFormat == IMV_EPixelType.gvspPixelMono8:
            imageBuff=stPixelConvertParam.pSrcData
            userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
            memmove(userBuff,imageBuff,stPixelConvertParam.nDstBufSize)
            grayByteArray = bytearray(userBuff)
            cvImage = numpy.array(grayByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth)
        else:
            stPixelConvertParam.eDstPixelFormat=IMV_EPixelType.gvspPixelBGR8
            nRet=cameras[cam_name].IMV_PixelConvert(stPixelConvertParam)
            if IMV_OK!=nRet:
                print("image convert to failed! ErrorCode[%d]" % nRet)
                del pDstBuf
                sys.exit()
            rgbBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
            memmove(rgbBuff,stPixelConvertParam.pDstBuf,stPixelConvertParam.nDstBufSize)
            colorByteArray = bytearray(rgbBuff)
            cvImage = numpy.array(colorByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth, 3)
            if None!=pDstBuf:
                del pDstBuf
                pass
        frames[frame_name] = cvImage
    return frames

def stopCamera(deviceList, cameras):
    for i in range(deviceList.nDevNum):
        cam_name = f"cam{i}"
        # 停止拉流
        nRet=cameras[cam_name].IMV_StopGrabbing()
        if IMV_OK != nRet:
            print("Stop grabbing failed! ErrorCode",nRet)
            sys.exit()
        # 关闭相机
        nRet=cameras[cam_name].IMV_Close()
        if IMV_OK != nRet:
            print("Close camera failed! ErrorCode",nRet)
            sys.exit()
        # 销毁句柄
        if(cameras[cam_name].handle):
            nRet=cameras[cam_name].IMV_DestroyHandle()

def Use_addr_Get_CamName(addr,KeyNumList):
    for key, value_ in KeyNumList.items():
        if addr == value_:
            return key

def Use_Addr_GetFrame(addr,cameras,KeyNumList):
    frames={}
    cam_name = Use_addr_Get_CamName(addr,KeyNumList)#根据地址获取相机名字
    frame = IMV_Frame()
    stPixelConvertParam = IMV_PixelConvertParam()
    nRet = cameras[cam_name].IMV_GetFrame(frame, 1000)
    if IMV_OK != nRet:
        print("getFrame fail! Timeout:[1000]ms")
        return -1
    else:
        print("getFrame success BlockId = [" + str(frame.frameInfo.blockId) + "], get frame time: " + str(
            datetime.datetime.now()))

    if None == byref(frame):
        print("pFrame is NULL!")
        return -1
    # 给转码所需的参数赋值

    if IMV_EPixelType.gvspPixelMono8 == frame.frameInfo.pixelFormat:
        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height
    else:
        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height * 3

    pDstBuf = (c_ubyte * nDstBufSize)()
    memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

    stPixelConvertParam.nWidth = frame.frameInfo.width
    stPixelConvertParam.nHeight = frame.frameInfo.height
    stPixelConvertParam.ePixelFormat = frame.frameInfo.pixelFormat
    stPixelConvertParam.pSrcData = frame.pData
    stPixelConvertParam.nSrcDataLen = frame.frameInfo.size
    stPixelConvertParam.nPaddingX = frame.frameInfo.paddingX
    stPixelConvertParam.nPaddingY = frame.frameInfo.paddingY
    stPixelConvertParam.eBayerDemosaic = IMV_EBayerDemosaic.demosaicNearestNeighbor
    stPixelConvertParam.eDstPixelFormat = frame.frameInfo.pixelFormat
    stPixelConvertParam.pDstBuf = pDstBuf
    stPixelConvertParam.nDstBufSize = nDstBufSize

    nRet = cameras[cam_name].IMV_ReleaseFrame(frame)
    if IMV_OK != nRet:
        print("Release frame failed! ErrorCode[%d]\n", nRet)
        sys.exit()

    if stPixelConvertParam.ePixelFormat == IMV_EPixelType.gvspPixelMono8:
        imageBuff = stPixelConvertParam.pSrcData
        userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)
        grayByteArray = bytearray(userBuff)
        cvImage = numpy.array(grayByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth)
    else:
        stPixelConvertParam.eDstPixelFormat = IMV_EPixelType.gvspPixelBGR8
        nRet = cameras[cam_name].IMV_PixelConvert(stPixelConvertParam)
        if IMV_OK != nRet:
            print("image convert to failed! ErrorCode[%d]" % nRet)
            del pDstBuf
            sys.exit()
        rgbBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(rgbBuff, stPixelConvertParam.pDstBuf, stPixelConvertParam.nDstBufSize)
        colorByteArray = bytearray(rgbBuff)
        cvImage = numpy.array(colorByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth, 3)
        if None != pDstBuf:
            del pDstBuf
            pass
    frames[cam_name]= cvImage
    return frames

def Use_Addr_GetImg(addr,cameras,KeyNumList):
    cam_name = Use_addr_Get_CamName(addr,KeyNumList)#根据地址获取相机名字
    frame = IMV_Frame()
    stPixelConvertParam = IMV_PixelConvertParam()
    nRet = cameras[cam_name].IMV_GetFrame(frame, 1000)
    if IMV_OK != nRet:
        print("getFrame fail! Timeout:[1000]ms")
        return -1
    else:
        print("getFrame success BlockId = [" + str(frame.frameInfo.blockId) + "], get frame time: " + str(
            datetime.datetime.now()))

    if None == byref(frame):
        print("pFrame is NULL!")
        return -1
    # 给转码所需的参数赋值

    if IMV_EPixelType.gvspPixelMono8 == frame.frameInfo.pixelFormat:
        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height
    else:
        nDstBufSize = frame.frameInfo.width * frame.frameInfo.height * 3

    pDstBuf = (c_ubyte * nDstBufSize)()
    memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))

    stPixelConvertParam.nWidth = frame.frameInfo.width
    stPixelConvertParam.nHeight = frame.frameInfo.height
    stPixelConvertParam.ePixelFormat = frame.frameInfo.pixelFormat
    stPixelConvertParam.pSrcData = frame.pData
    stPixelConvertParam.nSrcDataLen = frame.frameInfo.size
    stPixelConvertParam.nPaddingX = frame.frameInfo.paddingX
    stPixelConvertParam.nPaddingY = frame.frameInfo.paddingY
    stPixelConvertParam.eBayerDemosaic = IMV_EBayerDemosaic.demosaicNearestNeighbor
    stPixelConvertParam.eDstPixelFormat = frame.frameInfo.pixelFormat
    stPixelConvertParam.pDstBuf = pDstBuf
    stPixelConvertParam.nDstBufSize = nDstBufSize

    nRet = cameras[cam_name].IMV_ReleaseFrame(frame)
    if IMV_OK != nRet:
        print("Release frame failed! ErrorCode[%d]\n", nRet)
        sys.exit()

    if stPixelConvertParam.ePixelFormat == IMV_EPixelType.gvspPixelMono8:
        imageBuff = stPixelConvertParam.pSrcData
        userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(userBuff, imageBuff, stPixelConvertParam.nDstBufSize)
        grayByteArray = bytearray(userBuff)
        cvImage = numpy.array(grayByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth)
    else:
        stPixelConvertParam.eDstPixelFormat = IMV_EPixelType.gvspPixelBGR8
        nRet = cameras[cam_name].IMV_PixelConvert(stPixelConvertParam)
        if IMV_OK != nRet:
            print("image convert to failed! ErrorCode[%d]" % nRet)
            del pDstBuf
            sys.exit()
        rgbBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        memmove(rgbBuff, stPixelConvertParam.pDstBuf, stPixelConvertParam.nDstBufSize)
        colorByteArray = bytearray(rgbBuff)
        cvImage = numpy.array(colorByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth, 3)
        if None != pDstBuf:
            del pDstBuf
            pass
    return cvImage
