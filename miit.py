import requests
import time
import base64
import hashlib
from tempfile import NamedTemporaryFile
import cv2
import sys


class MIITSpider():
    def __init__(self) -> None:
        self.s = requests.Session()
        self.s.headers["User-Agent"] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.141 Safari/537.36'

    def auth(self):
        timeStamp = round(time.time() * 1000)
        authKey = hashlib.md5(('testtest' + str(timeStamp)).encode()).hexdigest()
        data = {
            'authKey': authKey,
            'timeStamp': timeStamp
        }
        url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/auth'
        try:
            r = self.s.post(url=url, data=data, headers={'Origin': 'https://beian.miit.gov.cn', 'Referer': 'https://beian.miit.gov.cn/'}).json()
            return r['params']['bussiness']
        except:
            print(r)
            return -1
        
    def getCheckImage(self, token):
        url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/getCheckImage'
        try:
            r = self.s.post(url=url, headers={'Token': token, 'Origin': 'https://beian.miit.gov.cn', 'Referer': 'https://beian.miit.gov.cn/'}).json()
            key = r['params']['uuid']
            with NamedTemporaryFile(mode="wb", delete=False) as bigImage:
                bigImage.write(base64.b64decode(r['params']['bigImage']))
            with NamedTemporaryFile(mode="wb", delete=False) as smallImage:
                smallImage.write(base64.b64decode(r['params']['smallImage']))
        except:
            return -1
        background_image = cv2.imread(bigImage.name, cv2.COLOR_GRAY2RGB)
        fill_image = cv2.imread(smallImage.name, cv2.COLOR_GRAY2RGB)
        position_match = cv2.matchTemplate(background_image, fill_image, cv2.TM_CCOEFF_NORMED)
        max_loc = cv2.minMaxLoc(position_match)[3][0]
        value = max_loc + 1
        return [key, value]
    
    def checkImage(self, token, key, value):
        url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/checkImage'
        try:
            data = {
                'key': key,
                'value': value
            }
            r = self.s.post(url=url, json=data, headers={'Token': token, 'Origin': 'https://beian.miit.gov.cn', 'Referer': 'https://beian.miit.gov.cn/'}).json()
            return r['params']
        except:
            return -1
        
    def queryByCondition(self, unitName):
        token = self.auth()
        if token == -1:
            raise Exception('Token获取失败')
        captcha = self.getCheckImage(token)
        if captcha == -1:
            raise Exception('验证码获取失败')
        sign = s.checkImage(token, captcha[0], captcha[1])
        if sign == -1:
            raise Exception('验证码识别失败')
        url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/icpAbbreviateInfo/queryByCondition'
        data = {
            'pageNum': '',
            'pageSize': '',
            'unitName': unitName,
            'serviceType': 1
        }
        try:
            r = self.s.post(url=url, json=data, headers={'Token': token, 'Sign': sign, 'Origin': 'https://beian.miit.gov.cn', 'Referer': 'https://beian.miit.gov.cn/'}).json()
            return r['params']['list']
        except:
            raise Exception('备案信息查询失败')
        


if __name__ == '__main__':
    unitName = sys.argv[1]
    s = MIITSpider()
    data = s.queryByCondition(unitName)
    print(data)
