from plyfile import PlyData
import pandas as pd
import numpy as np

def read_pc(filename):
    '''
    description: 读取ply转为(n, 6) numpy.array
    return {*} data_np (n, 6) numpy.array
    '''    
    plydata = PlyData.read(filename) 
    data = plydata.elements[0].data
    data_pd = pd.DataFrame(data)  # 转换成DataFrame, 因为DataFrame可以解析结构化的数据
    data_np = np.zeros(data_pd.shape, dtype=np.float32)  # 初始化储存数据的array
    property_names = data[0].dtype.names  # 读取property的名字
    for i, name in enumerate(property_names):  # 按property读取数据，这样可以保证读出的数据是同样的数据类型。
        data_np[:, i] = data_pd[name]
    return data_np
def reg_pc(pc):
    center = np.mean(pc[:, :3], axis=0)
    pc[:, :3] -= center
    
    R = np.sqrt(np.max(np.sum(pc[:, :3]**2, axis=1)))
    return pc, R
def project_point_cloud(K, view, image_shape, pc):
    W2C = np.linalg.inv(view)
    H, W = image_shape
    image = np.zeros((H, W, 3), dtype=np.uint8)
    depth = np.zeros((H, W), dtype=np.uint16)
    cnt = 0
    # 遍历点云中的每个点
    for point in pc:
        # 获取点的位置和颜色
        position = point[:3]
        color = point[3:]
        # 将点的位置从世界坐标系转换到相机坐标系
        position = W2C @ np.append(position, 1)
        # 将点的位置从相机坐标系转换到图像坐标系
        position = K @ position[:3]

        # 该点深度
        d = int(position[2] * 1000)
        if d == 0:
            continue
        color = (int(color[0]), int(color[1]), int(color[2]))
        # 将点的位置归一化，得到像素坐标
        position = position / position[2]
        
        # 判断像素坐标是否在图像范围内，如果是，就将图像上对应的像素设置为点的颜色
        if 0 <= position[0] < 640 and 0 <= position[1] < 480:
            if d > 0 and (d < depth[int(position[1]), int(position[0])] or depth[int(position[1]), int(position[0])] == 0):
                image[int(position[1]), int(position[0])] = color
                depth[int(position[1]), int(position[0])] = d
                cnt += 1
    print(cnt)
    return image, depth