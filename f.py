#coding: utf-8
import time

BigRect = {
    'left': {
        'x': 113.800000,
        'y': 22.120000
    },
    'right': {
        'x': 114.480000,
        'y': 22.580000
    }
}

"""
    定义细分窗口的数量，横向X * 纵向Y
"""
WindowSize = {
    'xNum': 9.0,
    'yNum': 9.0
}


def getSmallRect(bigRect, windowSize, windowIndex):
    """
    获取小矩形的左上角和右下角坐标字符串（百度坐标系）
    :param bigRect: 关注区域坐标信息
    :param windowSize:  细分窗口数量信息
    :param windowIndex:  Z型扫描的小矩形索引号
    :return: lat,lng,lat,lng
    """
    offset_x = (bigRect['right']['x'] - bigRect['left']['x'])/windowSize['xNum']
    offset_y = (bigRect['right']['y'] - bigRect['left']['y'])/windowSize['yNum']
    left_x = bigRect['left']['x'] + offset_x * (windowIndex % windowSize['xNum'])
    left_y = bigRect['left']['y'] + offset_y * (windowIndex // windowSize['yNum'])
    right_x = (left_x + offset_x)
    right_y = (left_y + offset_y)
    return str(left_y) + ',' + str(left_x) + ',' + str(right_y) + ',' + str(right_x)


def main():
    rect = []
    today = time.strftime("%Y-%m-%d")
    for index in range(int(WindowSize['xNum'] * WindowSize['yNum'])):
        smallRect = getSmallRect(BigRect, WindowSize, index)
        rect.append(smallRect)
    logfile = open("./log/" + "矩形" + "-" + today + ".log", 'a+', encoding='utf-8')
    logfile.writelines(str(rect)+ '\n')
    print("导出结束")

if __name__ == '__main__':
    main()
