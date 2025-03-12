from camera import *
import sys
from ctypes import *
import datetime
import numpy
import json
from IMVApi import *

MONO_CHANNEL_NUM = 1
RGB_CHANNEL_NUM = 3
BGR_CHANNEL_NUM = 3

'''
图像顺时针旋转
成功，返回IMV_OK；错误，返回错误码
只支持gvspPixelRGB8 / gvspPixelBGR8 / gvspPixelMono8格式数据的90/180/270度顺时针旋转。
通过该接口将原始图像数据旋转后并存放在调用者指定内存中。
'''
def getRotateImage(deviceList, cameras, frames, rotationAngle, imageFlipType):
    global cvImage
    frame = IMV_Frame()
    for i in range(deviceList.nDevNum):
        cam_name = f"cam{i}"
        frame_name = f"frame{i}"
        cam =  cameras[cam_name]
        nRet = cam.IMV_GetFrame(frame, 1000)
        if IMV_OK != nRet:
            print("getRotateImage fail! Timeout:[1000]ms, ErrorCode[%d]", nRet)
            continue
        else:
            print("getRotateImage success BlockId = [" + str(frame.frameInfo.blockId) + "], get frame time: " + str(
                datetime.datetime.now()))

        if None == byref(frame):
            print("pFrame is NULL!")
            continue

        stPixelConvertParam = IMV_PixelConvertParam()
        stRotateImageParam = IMV_RotateImageParam()
        pConvertBuf = None
        nChannelNum = 0

        memset(byref(stRotateImageParam), 0, sizeof(stRotateImageParam))
        if IMV_EPixelType.gvspPixelMono8 == frame.frameInfo.pixelFormat:
            stRotateImageParam.pSrcData = frame.pData
            stRotateImageParam.nSrcDataLen = frame.frameInfo.width * frame.frameInfo.height * MONO_CHANNEL_NUM
            stRotateImageParam.ePixelFormat = frame.frameInfo.pixelFormat
            nChannelNum = MONO_CHANNEL_NUM
        elif IMV_EPixelType.gvspPixelBGR8 == frame.frameInfo.pixelFormat:
            stRotateImageParam.pSrcData = frame.pData
            stRotateImageParam.nSrcDataLen = frame.frameInfo.width * frame.frameInfo.height * BGR_CHANNEL_NUM
            stRotateImageParam.ePixelFormat = frame.frameInfo.pixelFormat
            nChannelNum = BGR_CHANNEL_NUM
        elif IMV_EPixelType.gvspPixelRGB8 == frame.frameInfo.pixelFormat:
            stRotateImageParam.pSrcData = frame.pData
            stRotateImageParam.nSrcDataLen = frame.frameInfo.width * frame.frameInfo.height * RGB_CHANNEL_NUM
            stRotateImageParam.ePixelFormat = frame.frameInfo.pixelFormat
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
                stRotateImageParam.pSrcData = pConvertBuf
                stRotateImageParam.nSrcDataLen = stPixelConvertParam.nDstDataLen
                stRotateImageParam.ePixelFormat = IMV_EPixelType.gvspPixelBGR8
                nChannelNum = BGR_CHANNEL_NUM
            else:
                stRotateImageParam.pSrcData = None
                print("image convert to BGR8 failed! ErrorCode[%d]", nRet)
        bEnd = True
        while bEnd:
            if None == stRotateImageParam.pSrcData:
                print("stRotateImageParam pSrcData is NULL!")
                break
            nRotateBufSize = frame.frameInfo.width * frame.frameInfo.height * nChannelNum
            pRotateBuf = (c_ubyte * nRotateBufSize)()

            stRotateImageParam.nWidth = frame.frameInfo.width
            stRotateImageParam.nHeight = frame.frameInfo.height
            stRotateImageParam.eRotationAngle = rotationAngle
            stRotateImageParam.pDstBuf = pRotateBuf
            stRotateImageParam.nDstBufSize = nRotateBufSize

            # 释放图像缓存 (否则会造成图像缓存被占满，报超时）
            nRet = cameras[cam_name].IMV_ReleaseFrame(frame)
            if IMV_OK != nRet:
                print("Release frame failed! ErrorCode[%d]\n", nRet)
                sys.exit()

            # 图像顺时针旋转
            nRet = cam.IMV_RotateImage(stRotateImageParam)

            if IMV_OK == nRet:
                if IMV_ERotationAngle.rotationAngle90 == rotationAngle:
                    print("Image rotation angle 90 degree successfully!")
                    FileName = "rotationAngle90.bin"
                    hFile = open(FileName.encode('ascii'), "wb")
                elif IMV_ERotationAngle.rotationAngle180 == rotationAngle:
                    print("Image rotation angle 180 degree successfully!")
                    FileName = "rotationAngle180.bin"
                    hFile = open(FileName.encode('ascii'), "wb")
                else:
                    print("Image rotation angle 270 degree successfully!")
                    FileName = "rotationAngle270.bin"
                    hFile = open(FileName.encode('ascii'), "wb")

                try:
                    img_buff = c_buffer(b'\0', stRotateImageParam.nDstBufSize)
                    memmove(img_buff, stRotateImageParam.pDstBuf, stRotateImageParam.nDstBufSize)
                    hFile.write(img_buff)
                    grayByteArray = bytearray(img_buff)
                    cvImage = numpy.array(grayByteArray).reshape(stRotateImageParam.nHeight,stRotateImageParam.nWidth)
                    if imageFlipType == 0 or imageFlipType == 1:
                        cvImage = cv2.flip(cvImage, imageFlipType)
                except:
                    print("save file executed failed")
                finally:
                    hFile.close()
            else:
                if IMV_ERotationAngle.rotationAngle90 == rotationAngle:
                    print("Image rotation angle 90 degree failed! ErrorCode[%d]", nRet)
                elif IMV_ERotationAngle.rotationAngle180 == rotationAngle:
                    print("Image rotation angle 180 degree failed! ErrorCode[%d]", nRet)
                else:
                    print("Image rotation angle 270 degree failed! ErrorCode[%d]", nRet)
            if None != pConvertBuf:
                del pConvertBuf
                pConvertBuf = None
            if None != pRotateBuf:
                del pRotateBuf
            bEnd = False
        frames[frame_name] = cvImage
    return frames


'''
图像翻转
成功，返回IMV_OK；错误，返回错误码
只支持像素格式gvspPixelRGB8 / gvspPixelBGR8 / gvspPixelMono8的图像的垂直和水平翻转。
通过该接口将原始图像数据翻转后并存放在调用者指定内存中。
'''
def imageFlip(deviceList, cameras, frames, imageFlipType):
    global cvImage
    frame = IMV_Frame()
    for i in range(deviceList.nDevNum):
        cam_name = f"cam{i}"
        frame_name = f"frame{i}"
        cam = cameras[cam_name]
        nRet = cam.IMV_GetFrame(frame, 1000)
        if IMV_OK != nRet:
            print("getRotateImage fail! Timeout:[1000]ms, ErrorCode[%d]", nRet)
            continue
        else:
            print("getRotateImage success BlockId = [" + str(frame.frameInfo.blockId) + "], get frame time: " + str(
                datetime.datetime.now()))

        if None == byref(frame):
            print("pFrame is NULL!")
            continue

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

            # 释放图像缓存 (否则会造成图像缓存被占满，报超时）
            nRet = cameras[cam_name].IMV_ReleaseFrame(frame)
            if IMV_OK != nRet:
                print("Release frame failed! ErrorCode[%d]\n", nRet)
                sys.exit()

            nRet = cam.IMV_FlipImage(stFlipImageParam)

            if IMV_OK == nRet:
                if IMV_EFlipType.typeFlipVertical == imageFlipType:
                    print("Image vertical flip successfully!")
                    FileName = "verticalFlip.bin"
                    hFile = open(FileName.encode('ascii'), "wb")
                else:
                    print("Image horizontal flip successfully!")
                    FileName = "horizontalFlip.bin"
                    hFile = open(FileName.encode('ascii'), "wb")

                try:
                    img_buff = c_buffer(b'\0', stFlipImageParam.nDstBufSize)
                    memmove(img_buff, stFlipImageParam.pDstBuf, stFlipImageParam.nDstBufSize)
                    hFile.write(img_buff)
                    grayByteArray = bytearray(img_buff)
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
        frames[frame_name] = cvImage
    return frames
