#coding: utf-8
import requests
import json
import time
import MySQLdb


"""
    查询关键字：
"""
FileKey = 'baidu'
KeyWord = u"自然地物"

"""
    关注区域的左下角和右上角百度地图坐标(经纬度）
"""
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

newWindowSize = {
    'xNum': 3.0,
    'yNum': 3.0
}

conn = MySQLdb.connect(
    host= 'localhost',
    port= 3306,
    user= 'root',
    passwd= '123456',
    db= 'baidu',
    charset='utf8')
cursor = conn.cursor()

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

def getNewRect(bigRect,windowSize,windowIndex):
    offset_x = (bigRect[3] - bigRect[1]) / windowSize['xNum']
    offset_y = (bigRect[2] - bigRect[0]) / windowSize['yNum']
    left_x = bigRect[1] + offset_x * (windowIndex % windowSize['xNum'])
    left_y = bigRect[0] + offset_y * (windowIndex // windowSize['yNum'])
    right_x = (left_x + offset_x)
    right_y = (left_y + offset_y)
    return str(left_y) + ',' + str(left_x) + ',' + str(right_y) + ',' + str(right_x)

def requestBaiduApi(keyWords,smallRect, baiduAk, fileKey,rect):
    today = time.strftime("%Y-%m-%d")
    pageNum = 0
    logfile = open("./log/" + fileKey + "-" + today + ".log", 'a+', encoding='utf-8')
    # print('-------------')
    # print(index)
    while True:
        try:
            URL = "http://api.map.baidu.com/place/v2/search?query=" + keyWords + \
                  "&bounds=" + smallRect + \
                  "&output=json" + \
                  "&ak=" + baiduAk + \
                  "&scope=2"+ \
                  "&page_size=20" + \
                  "&page_num=" + str(pageNum)
            resp = requests.get(URL)
            res = json.loads(resp.text)
            print(str(res['total']))
            if len(res['results']) == 0:
                logfile.writelines(time.strftime("%Y%m%d%H%M%S") + " stop "  + " " + smallRect + " " + str(pageNum) + '\n')
                break
            else:
                for r in res['results']:
                    province = r.get('province')
                    if province == "香港特别行政区":
                        name = r.get('name')
                        lng = None
                        lat = None
                        if "location" in r:
                            lat = r.get('location').get('lat')
                            lng = r.get('location').get('lng')
                        address = r.get('address')
                        city = r.get('city')
                        area = r.get('area')
                        street_id = r.get('street_id')
                        telephone = r.get('telephone')
                        uid = r.get('uid')
                        detail_info = r.get('detail_info')
                        tag = detail_info.get('tag')
                        navi_lng = None
                        navi_lat = None
                        if "navi_location" in detail_info:
                            navi_lng = detail_info.get('navi_location').get('lng')
                            navi_lat = detail_info.get('navi_location').get('lat')
                        type = detail_info.get('type')
                        price = detail_info.get('price')
                        overall_rating = detail_info.get('overall_rating')
                        children = detail_info.get('children')
                        children = str(children)
                        if children == "[]":
                            children = None
                        t = [name, lat, lng, address, province, city, area, street_id, telephone, uid, tag, navi_lng, navi_lat, type, price, overall_rating, children]
                        # print(t)
                        sql = u"INSERT INTO "+ fileKey + "(name, lat, lng, address, province, city, area, street_id, telephone, uid, tag, navi_lng, navi_lat, type, price, overall_rating, children) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        # print(sql)
                        try:
                            cursor.execute(sql, t)
                            conn.commit()
                        except:
                            print("插入失败")
                pageNum += 1
                time.sleep(1)
        except:
            print("except")
            logfile.writelines(time.strftime("%Y%m%d%H%M%S") + " except "  + " " + smallRect + " " + str(pageNum) + '\n')
            logfile.writelines(time.strftime("%Y%m%d%H%M%S") + " except " + '\n' + str(rect) + " " + '\n')
            break

def main():
    baiduAk = "DgGqDu3U64TDaNYxaTgx6q5nt1ZoWfKF"
    rect = []
    for index in range(int(WindowSize['xNum'] * WindowSize['yNum'])):
        smallRect = getSmallRect(BigRect, WindowSize, index)
        rect.append(smallRect)
    while len(rect) > 0:
        print("还有"+str(len(rect))+"个矩形")
        rectPop = rect.pop()
        pageNum = 0
        URL = "http://api.map.baidu.com/place/v2/search?query=" + KeyWord + \
              "&bounds=" + rectPop + \
              "&output=json" + \
              "&ak=" + baiduAk + \
              "&scope=2" + \
              "&page_size=20" + \
              "&page_num=" + str(pageNum)
        print(URL)
        resp = requests.get(URL)
        res = json.loads(resp.text)
        print("有" + str(res['total']) + "条数据")
        if res['total'] == 400:
            popList = rectPop.split(',')
            popList = map(float, popList)
            popList = list(popList)
            print(popList)
            print("recut")
            for i in range(int(newWindowSize['xNum'] * newWindowSize['yNum'])):
                newRect = getNewRect(popList, newWindowSize, i)
                rect.append(newRect)
        else:
            requestBaiduApi(keyWords=KeyWord, smallRect=rectPop, baiduAk=baiduAk, fileKey=FileKey, rect = rect)
            time.sleep(1)
    print("爬取"+ KeyWord + "结束")

if __name__ == '__main__':
    main()
