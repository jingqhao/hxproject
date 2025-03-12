import cv2

# 读取图像 Pic_2024_10_17_115315_2.bmp
image = cv2.imread('C:/Users/lycode/MVviewer/pictures/Pic_2024_10_17_115108_1.bmp')

# 转换为灰度图像
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 创建一个窗口显示原始图像
cv2.imshow('Original Image', image)

# 创建一个窗口显示灰度图像
cv2.imshow('Gray Image', gray_image)

# 等待按键，然后关闭所有窗口
cv2.waitKey(0)
cv2.destroyAllWindows()

# 保存灰度图像
cv2.imwrite('gray_image.jpg', gray_image)