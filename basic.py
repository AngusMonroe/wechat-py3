
# -*- coding: utf-8 -*-
# filename: basic.py
from urllib import request
import time
import json


class Basic:
    def __init__(self):
        self.__accessToken = ''
        self.__leftTime = 0

    def __real_get_access_token(self):
        appId = "wx28e7c0e2ca1c1264"
        appSecret = "188780ef17299cb4a6cbb6ac3a1bb507"
        postUrl = ("https://api.weixin.qq.com/cgi-bin/token?grant_type="               "client_credential&appid=%s&secret=%s" % (appId, appSecret))
        urlResp = request.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        self.__accessToken = urlResp['access_token']
        self.__leftTime = urlResp['expires_in']

    def get_access_token(self):
        if self.__leftTime < 10:
            self.__real_get_access_token()
        return self.__accessToken

    def run(self):
        while(True):
            if self.__leftTime > 10:
                time.sleep(2)
                self.__leftTime -= 2
            else:
                self.__real_get_access_token()
