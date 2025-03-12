import json
import os

# 要写入JSON文件的数据
data = {
    'x': 100.1,
    'y': 100.2,
    'w': 100.3,
    'h': 100.4
}

# 指定JSON文件的保存路径
file_path = 'C:/Users/lycode/Desktop/PeiFang/Camera1/abc/ROI.json'

# 确保目录存在，如果不存在则创建
os.makedirs(os.path.dirname(file_path), exist_ok=True)

# 将数据写入JSON文件
with open(file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

print(f'JSON data has been written to {file_path}')