# -*- coding: utf-8 -*-
# filename: media.py
from basic import Basic
from urllib import request
import poster.encode
from poster.streaminghttp import register_openers


class Media(object):
    def __init__(self):
        register_openers()

    # 上传图片
    def uplaod(self, accessToken, filePath, mediaType):
        print("uploading...")
        with open(filePath, 'rb') as openFile:
            param = {'media': openFile}
            print(param)
            postData, postHeaders = poster.encode.multipart_encode(param)
            print(postData)

            postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=" + accessToken + "&type=" + mediaType
            print(postUrl)
            req = request.Request(postUrl, postData, postHeaders)
            urlResp = request.urlopen(req)
            print(urlResp.read())

if __name__ == '__main__':
    myMedia = Media()
    accessToken = Basic().get_access_token()
    filePath = "D:/code/mpGuide/media/test.jpg"   #请安实际填写
    mediaType = "image"
    myMedia.uplaod(accessToken, filePath, mediaType)
