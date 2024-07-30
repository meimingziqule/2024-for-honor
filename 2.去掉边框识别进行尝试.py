import sensor, image, time, pyb, math, display
from pyb import UART, LED, Pin, Timer

# 阈值待调
black_thresholds = (29, 97, 14, 127, -128, 127)
white_thresholds = (0, 100, -128, 127, -128, 127)

rect_flag = 1  # 执照一次矩形
rect_points_flag = 1  # 矩形点识别一次标志位

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QQVGA2) # Set frame size to QQVGA2 (128x160)
sensor.set_hmirror(True)
sensor.set_vflip(True)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
sensor.set_auto_gain(False)         # 必须关闭自动增益以进行颜色追踪
sensor.set_auto_whitebal(False)     # 必须关闭白平衡以进行颜色追踪0
clock = time.clock()

lcd = display.SPIDisplay()          # 初始化lcd屏幕
uart = UART(3, 115200)  
uart.init(115200, bits=8, parity=None, stop=1)

# 打印颠倒后的矩形四个顶点坐标，并返回矩形矩形顶点
def find_rect_corners(rect, img):
    for r in rect:
        corners = r.corners()
        corners = [corners[3], corners[2], corners[1], corners[0]]  # 颠倒点的顺序
        for p in corners:
            img.draw_cross(p[0], p[1], 5, color=(0, 255, 0))
        print(corners)  # 打印顶点[(x1,y1),................]
    return corners

# 矩形分割函数
def divide_polygon_segments(points, n):
    if len(points) != 4:
        raise ValueError("points列表必须包含四个点")

    result = []
    for i in range(4):
        segment_points = divide_line_segment(points[i], points[(i + 1) % 4], n)
        result.extend(segment_points)

    return result

# 去重函数
def remove_duplicates_preserve_order(input_list):
    seen = set()
    unique_list = []
    first_element = input_list[0]  # 保存第一个元素
    for item in input_list:
        if item not in seen:
            seen.add(item)
            unique_list.append(item)
    unique_list.remove(first_element)  # 移除第一个元素
    unique_list.append(first_element)  # 将第一个元素添加到末尾
    return unique_list

# 线段分割函数
def divide_line_segment(point1, point2, n):
    if n < 1:
        raise ValueError("n必须大于等于1")

    x1, y1 = point1
    x2, y2 = point2

    points = []
    for i in range(n + 1):
        x = x1 + (x2 - x1) * i / n
        y = y1 + (y2 - y1) * i / n
        points.append((int(x), int(y)))

    return points

# 矩形绘制函数
def draw_rectangles(img, rect_points):
    for i in range(len(rect_points) - 1):
        img.draw_line(rect_points[i][0], rect_points[i][1], rect_points[i + 1][0], rect_points[i + 1][1], color=(255, 0, 0))

    img.draw_line(rect_points[1][0], rect_points[1][1], rect_points[8][0], rect_points[8][1], color=(0, 255, 0))
    img.draw_line(rect_points[2][0], rect_points[2][1], rect_points[7][0], rect_points[7][1], color=(0, 255, 0))
    img.draw_line(rect_points[4][0], rect_points[4][1], rect_points[11][0], rect_points[11][1], color=(0, 255, 0))
    img.draw_line(rect_points[5][0], rect_points[5][1], rect_points[10][0], rect_points[10][1], color=(0, 255, 0))
'''
# 检测棋盘格子内的黑棋和白棋
def detect_chess_pieces(img, rect_points):
    grid_width = (rect_points[2][0] - rect_points[1][0]) // 3
    grid_height = (rect_points[4][1] - rect_points[1][1]) // 3

    for row in range(3):
        for col in range(3):
            x = rect_points[1][0] + col * grid_width
            y = rect_points[1][1] + row * grid_height
            roi = (x, y, grid_width, grid_height)
            img.draw_rectangle(roi, color=(0, 0, 255))

            black_blobs = img.find_blobs([black_thresholds], roi=roi, merge=True)
            white_blobs = img.find_blobs([white_thresholds], roi=roi, merge=True)

            if black_blobs:
                print("Grid (%d, %d): Black棋" % (row, col))
            elif white_blobs:
                print("Grid (%d, %d): White棋" % (row, col))
            else:
                print("Grid (%d, %d): 无棋" % (row, col))
'''


# 检测棋盘格子内的黑棋和白棋
def detect_chess_pieces(img, rect_points):
    grid_width = (rect_points[2][0] - rect_points[1][0]) // 3
    grid_height = (rect_points[4][1] - rect_points[1][1]) // 3

    # 初始化标志位数组
    flags = [0] * 9

    for row in range(3):
        for col in range(3):
            x = rect_points[1][0] + col * grid_width
            y = rect_points[1][1] + row * grid_height
            roi = (x, y, grid_width, grid_height)
            img.draw_rectangle(roi, color=(0, 0, 255))

            black_blobs = img.find_blobs([black_thresholds], roi=roi, merge=True)
            white_blobs = img.find_blobs([white_thresholds], roi=roi, merge=True)

            index = row * 3 + col
            if black_blobs:
                flags[index] = 2
            elif white_blobs:
                flags[index] = 1
            else:
                flags[index] = 0

    # 将标志位数组转换为字符串输出
    result = ''.join(map(str, flags))
    print(result)

kernel_size = 1 # 3x3==1, 5x5==2, 7x7==3, etc.

kernel = [-2, -1,  0, \
          -1,  1,  1, \
           0,  1,  2]


while(True):
    clock.tick()                    # Update the FPS clock.
    
    img = sensor.snapshot()         # Take a picture and return the image.
    img.morph(kernel_size, kernel)
    
    # 识别黑色圆形
    black_blobs = img.find_blobs([black_thresholds], x_stride=5, y_stride=5, pixels_threshold=800, merge=True)
    for blob in black_blobs:
        if blob.roundness() > 0.3: # 判断是否为圆形
            img.draw_circle(blob.cx(), blob.cy(), 25, color=(0,0,255))
            print("黑色圆形位置: x=%d, y=%d, r=%d" % (blob.cx(), blob.cy(), 25))
            print("黑色像素数量：%d" % blob.pixels())
    
    # 识别白色圆形
    white_blobs = img.find_blobs([white_thresholds], x_stride=5, y_stride=5, pixels_threshold=800, merge=True)
    for blob in white_blobs:
        img.draw_circle(blob.cx(), blob.cy(), 25, color=(255,0,0))
        print("白色圆形位置: x=%d, y=%d, r=%d" % (blob.cx(), blob.cy(), 25))
        print("白色像素数量：%d" % blob.pixels())

    #找到矩形后不再继续找
    if rect_flag == 1:
        rect = img.find_rects(threshold=65000)
                                
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
    # 绘制识别到的矩形框
    if rect_points_flag == 0:
        draw_rectangles(img, rect_points_transform)
        detect_chess_pieces(img, rect_points_transform)
         
