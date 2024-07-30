import sensor, image, time, pyb,math,display
from pyb import UART, LED,Pin, Timer
#阈值待调
black_thresholds = (0, 6, -128, 127, -128, 127)
white_thresholds = (66, 100, -128, 127, -128, 127)

rect_flag = 1 #执照一次矩形
rect_points_flag  = 1 #矩形点识别一次标志位

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.VGA)   # Set frame size to QQVGA2 (128x160)
sensor.set_hmirror(True)
sensor.set_vflip(True)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
sensor.set_auto_gain(False) # 必须关闭自动增益以进行颜色追踪
sensor.set_auto_whitebal(False) # 必须关闭白平衡以进行颜色追踪0
sensor.set_windowing((324, 249, 155, 141))
clock = time.clock()

lcd = display.SPIDisplay() # 初始化lcd屏幕
uart = UART(3,115200)  
uart.init(115200, bits=8, parity=None, stop=1 )
#  #1是十字路口    #2是终点

#颠倒识别到的矩形四个顶点坐标顺序
def change_condi(corners_list):
    corners = [0,0,0,0]
    corners[0] = corners_list[-1]
    corners[1] = corners_list[-2]
    corners[2] = corners_list[-3]
    corners[3] = corners_list[-4]
    if corners is not None:
        return corners

# 打印颠倒后的矩形四个顶点坐标，并返回画面中最大的矩形顶点
def find_rect_corners(rect, img):
    for r in rect:
        if r.magnitude() < 85000:
            continue  # 如果矩形的magnitude小于85000，则跳过这个矩形
        corners = r.corners()
        corners = [corners[3], corners[2], corners[1], corners[0]]  # 颠倒点的顺序
        for p in corners:
            img.draw_cross(p[0], p[1], 5, color=(0, 255, 0))
        print(corners)  # 打印顶点[(x1,y1),................]
        return corners  # 返回第一个符合条件的矩形的顶点
    return None  # 如果没有符合条件的矩形，返回None


#矩形分割函数
def divide_polygon_segments(points, n):#如[(0.0, 0.0), (10.0, 1.2), (20.0, 2.4), (30.0, 3.6), (40.0, 4.8), (50.0, 6.0), (50.0, 6.0), (48.0, 10.8)]  
    """
    将一个四边形的每条边平分成n份，并将所有结果拼接成一个新的列表。

    参数:
    points (list): 包含四个点的列表，例如[(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    n (int): 要平分的份数

    返回:
    list: 包含所有点的数组，例如[(x1, y1), (x2, y2), ..., (x4, y4), ...]
    """
    if len(points) != 4:
        raise ValueError("points列表必须包含四个点")

    result = []
    for i in range(4):
        segment_points = divide_line_segment(points[i], points[(i + 1) % 4], n)
        result.extend(segment_points)

    return result

def remove_duplicates_preserve_order(input_list):
    seen = set()
    unique_list = []
    first_element = tuple(int(coord) for coord in input_list[0])  # 保存第一个元素并转换为int类型
    for item in input_list:
        item = tuple(int(coord) for coord in item)  # 将元组中的每个坐标转换为int类型
        if item not in seen:
            seen.add(item)
            unique_list.append(item)
    
    unique_list.append(first_element)  # 将第一个元素添加到末尾
    return unique_list



#线段分割函数
def divide_line_segment(point1, point2, n):
    """
    将两个点连成的线段平分成n份，并返回包含这些点的数组。

    参数:
    point1 (tuple): 第一个点的坐标 (x1, y1)
    point2 (tuple): 第二个点的坐标 (x2, y2)
    n (int): 要平分的份数

    返回:
    list: 包含所有点的数组，例如[(x1, y1), (x2, y2), ...]CC
    """
    if n < 1:
        raise ValueError("n必须大于等于1")

    x1, y1 = point1
    x2, y2 = point2

    points = []
    for i in range(n + 1):
        x = x1 + (x2 - x1) * i / n
        y = y1 + (y2 - y1) * i / n
        points.append((x, y))

    return points

#矩形绘制函数
def draw_rectangles(img,rect_points):

    # 绘制矩形框
    for i in range(len(rect_points) - 1):
        img.draw_line(rect_points[i][0], rect_points[i][1], rect_points[i + 1][0], rect_points[i + 1][1], color = (255, 0, 0))

    # 绘制额外的连线
    img.draw_line(rect_points[1][0], rect_points[1][1], rect_points[8][0], rect_points[8][1], color = (0, 255, 0))
    img.draw_line(rect_points[2][0], rect_points[2][1], rect_points[7][0], rect_points[7][1], color = (0, 255, 0))
    img.draw_line(rect_points[4][0], rect_points[4][1], rect_points[11][0], rect_points[11][1], color = (0, 255, 0))
    img.draw_line(rect_points[5][0], rect_points[5][1], rect_points[10][0], rect_points[10][1], color = (0, 255, 0))


'''
# 示例调用
rect_points = [
    (0, 0), (33.3, 0), (66.7, 0), (100, 0),  # 上边
    (100, 33.3), (100, 66.7), (100, 100),   # 右边
    (66.7, 100), (33.3, 100), (0, 100),     # 下边
    (0, 66.7), (0, 33.3), (0, 0)            # 左边
]
draw_rectangles(rect_points)'''

kernel_size = 1 # 3x3==1, 5x5==2, 7x7==3, etc.

kernel = [-2, -1,  0, \
          -1,  1,  1, \
           0,  1,  2]
           
tim = Timer(4, freq=1000) #设置频率，初始化定时器4，将其设置为1000HZ
# 生成50HZ方波，使用TIM4的channels 1输出占空比为 50%的PWM
ch1 = tim.channel(1, Timer.PWM, pin=Pin("P7"), pulse_width_percent=70)


while(True):
    clock.tick()                    # Update the FPS clock.
    ch1.pulse_width_percent(80)
    img = sensor.snapshot()         # Take a picture and return the image.
    
    img.morph(kernel_size, kernel)
    
    # 识别黑色圆形
    black_blobs = img.find_blobs([black_thresholds], x_stride=5, y_stride=5, pixels_threshold=100,area_threshold=400)
    for blob in black_blobs:
        if blob.w() >30  and blob.h() > 28: # 假设棋盘边框较大  待调整
            continue
        if blob.w() < 15 and blob.h() < 15: # 假设小于就不用 待调整
            continue
            
        # 进一步验证色块形状是否接近圆形（判断宽高比）
        aspect_ratio = blob.w() / blob.h()
        if aspect_ratio < 0.6 or aspect_ratio > 1.4: # 假设棋子的宽高比接近1   待调整
            continue
            
        if blob.roundness() > 0.70 and blob.area() > 500: # 判断是否为圆形
            #img.draw_rectangle(blob.rect(),color=(0,255,0))
            # 绘制矩形框在白色块周围
            enclosing_circle = blob.enclosing_circle()
            img.draw_circle(enclosing_circle[0], enclosing_circle[1], enclosing_circle[2], color=(0, 255, 0))
            print("黑色圆形位置: x=%d, y=%d, r=%d" % (blob.cx(), blob.cy(), 25))
            print("黑色像素数量：%d" % blob.pixels())
    if  black_blobs:
        print("黑色圆形的数量：",len(black_blobs)) 


    # 识别白色圆形
    white_blobs = img.find_blobs([white_thresholds], x_stride=10, y_stride=10, pixels_threshold=100)
    for blob in white_blobs:
            img.draw_rectangle(blob.rect(),color=(0,255,0))
            print("白色圆形位置: x=%d, y=%d, r=%d" % (blob.cx(), blob.cy(), 25))
            print("白色像素数量：%d" % blob.pixels())
    if  white_blobs:
        print("白色圆形的数量：",len(white_blobs))  
    #找到矩形后不再继续找
    if rect_flag == 1:
        rect = img.find_rects(threshold=80000)
                                
        if rect:
            corners = find_rect_corners(rect, img)
            
            if corners:
                rect_flag = 0
        else:
            print("没找到矩形")
    else:
        print("corner:", corners)
        img.draw_rectangle(rect[0].rect(), color=(255, 255, 255))
    print("rect_points_flag",rect_points_flag)

    #识别一次矩形点坐标
    if rect_points_flag == 1:
        if rect:
            '''rect_points_transform = [
            (0, 0), (33.3, 0), (66.7, 0), (100, 0),  # 上边
            (100, 33.3), (100, 66.7), (100, 100),   # 右边
            (66.7, 100), (33.3, 100), (0, 100),     # 下边
            (0, 66.7), (0, 33.3), (0, 0)            # 左边
            ]'''
            rect_points = divide_polygon_segments(corners, 3)
            rect_points_transform = remove_duplicates_preserve_order(rect_points)#去除重复元素
            rect_points_flag = 0 #trect_points_flag置0，不再识别矩形
            print("rect_point:", rect_points)

    #绘制识别到的矩形框
    if rect_points_flag == 0:
        draw_rectangles(img,rect_points_transform)
    
    #通过识别最大黑色色块的旋转角度来判断矩形旋转角度   