import cv2
import numpy as np
import os
from PIL import Image,ImageDraw

folder_path = 'D:/UVP/code_set/HX_end/pictures/'
image_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
template1 = cv2.imread('template1.bmp')
template2 = cv2.imread('template2.bmp')
h1, w1 = template1.shape[:2]
h2, w2 = template2.shape[:2]
temp1 = (400, 40)
temp2 = (400, 600)
point1 = (70,85)
point2 = (95,20)
roi1_x, roi1_y, roi1_w, roi1_h = 400, 40, 700, 300 
roi2_x, roi2_y, roi2_w, roi2_h = 400, 600, 700, 300 

for filename in os.listdir(folder_path):
    if any(filename.lower().endswith(ext) for ext in image_formats):
        file_path = os.path.join(folder_path, filename)
# file_path = 'D:/UVP/code_set/HX_end/pictures/Pic_2024_10_17_181746_14.bmp'
        image = cv2.imread(file_path) 
        roi1 = image[roi1_y:roi1_y+roi1_h, roi1_x:roi1_x+roi1_w]
        roi2 = image[roi2_y:roi2_y+roi2_h, roi2_x:roi2_x+roi2_w]
# cv2.imshow('ROI1', roi1)
# cv2.imshow('ROI2', roi2)
# model_x1, model_y1, model_w1, model_h1 = 120, 120, 300, 100
# model_x2, model_y2, model_w2, model_h2 = 20, 100, 400, 150
# template1 = roi1[model_y1:model_y1+model_h1, model_x1:model_x1+model_w1]
# template2 = roi2[model_y2:model_y2+model_h2, model_x2:model_x2+model_w2]
# cross_size = 10
# cv2.line(template1, (70 - cross_size, 85), (70 + cross_size, 85), (0, 0, 255), 2)  # 水平线
# cv2.line(template1, (70, 85 - cross_size), (70, 85 + cross_size), (0, 0, 255), 2)  # 垂直线
# cv2.line(template2, (95 - cross_size, 20), (95 + cross_size, 20), (0, 0, 255), 2)  # 水平线
# cv2.line(template2, (95, 20 - cross_size), (95, 20 + cross_size), (0, 0, 255), 2)  # 垂直线
# cv2.imshow('template1', template1)
# cv2.imshow('template2', template2)
# cv2.imwrite('template1.bmp', template1)
# cv2.imwrite('template2.bmp', template2)

        result1 = cv2.matchTemplate(roi1, template1, cv2.TM_CCOEFF_NORMED)
        result2 = cv2.matchTemplate(roi2, template2, cv2.TM_CCOEFF_NORMED)
        _, max_val1, _, max_loc1 = cv2.minMaxLoc(result1)
        _, max_val2, _, max_loc2 = cv2.minMaxLoc(result2)
        loc1 = tuple([a + b for a, b in zip(max_loc1, temp1)])
        loc2 = tuple([a + b for a, b in zip(max_loc2, temp2)])
        if max_val1 > 0.1 and max_val2 > 0.1:  # 假设阈值为0.8
            top_left = loc1
            bottom_right = (top_left[0] + w1, top_left[1] + h1)
            point1_loc = tuple([a + b for a, b in zip(top_left, point1)])
            cv2.rectangle(image, top_left, bottom_right, (0,255,0), 2)
            top_left = loc2
            bottom_right = (top_left[0] + w2, top_left[1] + h2)
            point2_loc = tuple([a + b for a, b in zip(top_left, point2)])
            cv2.rectangle(image, top_left, bottom_right, (0,255,0), 2)
            cross_size = 10
            cv2.line(image, (point1_loc[0] - cross_size, point1_loc[1]), (point1_loc[0] + cross_size, point1_loc[1]), (0, 0, 255), 2)  # 水平线
            cv2.line(image, (point1_loc[0], point1_loc[1] - cross_size), (point1_loc[0], point1_loc[1] + cross_size), (0, 0, 255), 2)  # 垂直线
            cv2.line(image, (point2_loc[0] - cross_size, point2_loc[1]), (point2_loc[0] + cross_size, point2_loc[1]), (0, 0, 255), 2)  # 水平线
            cv2.line(image, (point2_loc[0], point2_loc[1] - cross_size), (point2_loc[0], point2_loc[1] + cross_size), (0, 0, 255), 2)  # 垂直线
            cv2.imshow(filename, image)

# 等待按键，然后关闭所有窗口
cv2.waitKey(0)
cv2.destroyAllWindows()