import sensor, image, pyb

def draw_rectangles(rect_points):
    # 初始化摄像头
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time = 2000)

    # 获取图像
    img = sensor.snapshot()

    # 绘制矩形框
    for i in range(len(rect_points) - 1):
        img.draw_line(rect_points[i][0], rect_points[i][1], rect_points[i + 1][0], rect_points[i + 1][1], color = (255, 0, 0))

    # 绘制额外的连线
    img.draw_line(rect_points[1][0], rect_points[1][1], rect_points[8][0], rect_points[8][1], color = (0, 255, 0))
    img.draw_line(rect_points[2][0], rect_points[2][1], rect_points[7][0], rect_points[7][1], color = (0, 255, 0))
    img.draw_line(rect_points[4][0], rect_points[4][1], rect_points[11][0], rect_points[11][1], color = (0, 255, 0))
    img.draw_line(rect_points[5][0], rect_points[5][1], rect_points[10][0], rect_points[10][1], color = (0, 255, 0))

    # 显示图像
    img.show()

# 示例调用
rect_points = [
    (0, 0), (33.3, 0), (66.7, 0), (100, 0),  # 上边
    (100, 33.3), (100, 66.7), (100, 100),   # 右边
    (66.7, 100), (33.3, 100), (0, 100),     # 下边
    (0, 66.7), (0, 33.3), (0, 0)            # 左边
]

while(True):
    draw_rectangles(rect_points)