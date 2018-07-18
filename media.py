# -*- coding: utf-8 -*-
# filename: media.py
from basic import Basic
from urllib import request
import poster.encode
import requests
from poster.streaminghttp import register_openers


class Media(object):
    def __init__(self):
        register_openers()

    # 上传图片
    def uplaod(self, accessToken, filePath, mediaType):
        print("uploading...")
        # with open(filePath, 'rb') as openFile:
        #     txt = openFile.read()
        #     param = {'media': txt}
        #     print(param)
        #     postData, postHeaders = poster.encode.multipart_encode(param)
        #     print(postData)
        #
        #     postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=" + accessToken + "&type=" + mediaType
        #     print(postUrl)
        #     req = request.Request(postUrl, postData, postHeaders)
        #     urlResp = request.urlopen(req)
        #     print(urlResp.read())
        postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=" + accessToken + "&type=" + mediaType
        data = {"media": open(filePath, "rb")}
        r = requests.post(url=postUrl, files=data)
        dict = r.json()
        print(dict)
        return dict['media_id']

if __name__ == '__main__':
    myMedia = Media()
    accessToken = Basic().get_access_token()
    filePath = "D:/code/mpGuide/media/test.jpg"   #请安实际填写
    mediaType = "image"
    myMedia.uplaod(accessToken, filePath, mediaType)
