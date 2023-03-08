# -*- coding: utf-8 -*-
# @Time    : 8/3/2023 下午1:15
# @Author  : realMyU
# @FileName: main.py
# @Software: PyCharm
# @Blog    ：no blog
import json
import logging
import re
import sys
from urllib.parse import urlencode
import requests
import yaml
from Crypto.Cipher import AES
import base64

URL = "http://10.53.1.3/gportal/web/login"
HOST = "http://10.53.1.3/gportal/web/authLogin?round=463"
REBINDMAC = "http://10.53.1.3/gportal/web/reBindMac?round=463"


class Giwifi_Login:
    def __init__(self, **kwargs):
        self.STORE = {
            "cookie": "",
            "us": {
                "nasName": "HLG-SN",
                "nasIp": "",
                "userIp": "",
                "userMac": "",
                "ssid": "",
                "apMac": "",
                "pid": "23",
                "vlan": "1",
                "sign": "",
                "iv": "",
                "name": kwargs["name"],
                "password": kwargs["password"],
            }
        }
        self.HEADER = {
            "Connection": "keep-alive",
            "user-agent": "Safari/536.3"
            , "Accept-Encoding": "gzip, deflate, br"
        }

    def loginPage(self):
        payload = ""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/105.0.0.0 Safari/537.36',
        }
        try:
            response = requests.request("GET", URL, headers=headers, data=payload, timeout=3)
            if response.cookies: self.STORE["cookie"] = str(response.cookies)
            logging.info("获取登录页")

            if response.text:
                patternUserIp = r'name="userIp" value="(.*)" />'
                patternSign = r'name="sign" value="(.*)"/>'
                patternIv = r'name="iv" id="iv" value="(.*)"/>'
                userIp = re.findall(pattern=patternUserIp, string=str(response.text))[0]
                sign = re.findall(pattern=patternSign, string=str(response.text))[0]
                iv = re.findall(pattern=patternIv, string=str(response.text))[0]
                if userIp:
                    self.STORE["us"]["userIp"] = userIp
                    self.STORE["us"]["sign"] = sign
                    self.STORE["us"]["iv"] = iv

                logging.debug(self.STORE)
            else:
                print(ValueError)
        except requests.exceptions.ConnectTimeout:
            logging.critical("请链接到GIWIFI,或者检查网络")
            sys.exit(-1)
        return self

    def loginPost(self):
        payload = {
            "data": str(PrpCrypt("1234567887654321", self.STORE["us"]["iv"]).encrypt(urlencode(self.STORE["us"])),
                        'utf8'),
            "iv": self.STORE["us"]["iv"]
        }
        logging.debug(payload)
        response = requests.request("POST", HOST, headers=self.HEADER, data=payload, timeout=3)
        res = json.loads(response.text)
        logging.debug(res)
        if res["data"]["resultCode"] == 2:
            if res["data"]["reasoncode"] == 43:
                self.STORE["us"]["userMac"] = res["data"]["bindmac"]
                logging.info("检测到需要重新绑定mac，绑定mac")
                # 绑定mac
                self.rebindMac()
            elif res["data"]["reasoncode"] == 55:
                logging.debug(res["info"])
                logging.critical("由于热点开启，账号被禁用，不开qq，检测时间为30分钟，")
            elif res["data"]["reasoncode"] == 27:
                logging.debug(res["info"])
                logging.critical("密码或许错误，请检查config.yaml的配置")
            elif res["data"]["reasoncode"] == 1:
                logging.debug(res)
                logging.critical("认证拒绝")
        elif res["data"]["resultCode"] == 0:
            # 认证成功
            logging.debug(res)
            logging.info("认证，登录成功")
        else:
            logging.info(res["info"])

    def rebindMac(self, rebinmac: str = ""):
        if rebinmac:
            self.STORE["us"]["userMac"] = rebinmac

        payload = {
            "data": str(PrpCrypt("1234567887654321", self.STORE["us"]["iv"]).encrypt(urlencode(self.STORE["us"])),
                        'utf8'),
            "iv": self.STORE["us"]["iv"]
        }
        logging.debug(self.STORE)
        logging.debug(payload)
        response = requests.request("POST", REBINDMAC, headers=self.HEADER, data=payload, timeout=3)
        res = json.loads(response.text)
        if res["data"]["resultCode"] == 2:
            logging.error(res["info"])
            self.loginPost()
            logging.info("重新绑定，重新加载loginPost")


class PrpCrypt(object):
    def __init__(self, key, iv):
        self.ciphertext = None
        self.key = key.encode('utf-8')
        self.mode = AES.MODE_CBC
        self.iv = iv.encode('utf-8')

    def encrypt(self, text):
        text = text.encode('utf-8')
        cryptor = AES.new(self.key, self.mode, self.iv)
        length = 16
        count = len(text)
        if count < length:
            add = (length - count)
            text = text + ('\0' * add).encode('utf-8')
        elif count > length:
            add = (length - (count % length))
            text = text + ('\0' * add).encode('utf-8')
        self.ciphertext = cryptor.encrypt(text)
        return base64.b64encode(self.ciphertext)

    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.iv)
        plain_text = cryptor.decrypt(base64.b64decode(text))
        return plain_text


class YAML:
    def __init__(self, yaml_file_path="./config.yaml"):
        self.data = None
        self.yaml_file = yaml_file_path
        self.get_yaml_data(yaml_file_path)

    def get_yaml_data(self, yaml_file_path):
        # 打开yaml文件
        file = open(yaml_file_path, 'r', encoding="utf-8")
        self.data = yaml.load(file.read(), Loader=yaml.FullLoader)

        file.close()

    def __call__(self, *args, **kwargs):
        self.streaming("login", name=self.data["HOST"]["name"], password=self.data["HOST"]["password"])

    @staticmethod
    def streaming(step, **kwargs):
        if step == "login":
            Giwifi_Login(name=kwargs["name"], password=kwargs["password"]).loginPage().loginPost()
        else:
            pass


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - in function:%(funcName)s',
        level=logging.DEBUG)
    logging.info("程序开始")
    YAML()()
