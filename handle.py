# -*- coding: utf-8 -*-
# filename: handle.py
import hashlib
import reply
import receive
import media
import web
import requests
import ssl
import urllib.request
import urllib.parse
import re

def download(url, local_filename):
    r = requests.get(url, stream=True)
    with open("./wechat-py3/img/" + local_filename, 'wb') as f:
        print("opened")
        for chunk in r.iter_content(1024):
            if chunk:
                f.write(chunk)
                f.flush()
    return local_filename

class Handle(object):
    def GET(self):
            data = web.input()
            if len(data) == 0:
                return "hello, this is handle view"
            signature = data.signature
            timestamp = data.timestamp
            nonce = data.nonce
            echostr = data.echostr
            token = "wechat" #请按照公众平台官网\基本配置中信息填写

            list = [token, timestamp, nonce]
            list.sort()
            list2 = ''.join(list)
            sha1 = hashlib.sha1()
            sha1.update(list2.encode('utf-8'))
            hashcode = sha1.hexdigest()
            print(str(hashcode) + " " + str(signature) + " " + str(echostr))
            if hashcode == signature:
                return echostr  # 返回echostr

    def POST(self):
        try:
            webData = web.data()
            # print ("Handle Post webdata is ", webData)
   #后台打日志
            recMsg = receive.parse_xml(webData)
            if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                input = recMsg.Content.decode(encoding='utf-8')
                # context = ssl._create_unverified_context()
                txt = input.split()
                if txt[0] == "ins":
                    url = txt[1]
                    r = requests.get(url, params={'__a': 1})
                    if (
                        (r.headers['content-type'] != 'application/json') or
                        (not 'graphql' in r.json())
                    ):
                        replyMsg = reply.TextMsg(toUser, fromUser, "Wrong link")
                        return replyMsg.send()
                    try:
                        print("begin")
                        media = r.json()['graphql']['shortcode_media']
                        if media['is_video']:
                            print("video")
                            name = url.split("/")
                            print('Saved as ' + download(url,
                                                         name[len(name) - 1] + '.mp4') + '!')
                            myMedia = Media()
                            accessToken = Basic().get_access_token()
                            filePath = media['shortcode'] + '.mp4'   #请安实际填写
                            mediaType = "video"
                            link = myMedia.uplaod(accessToken, filePath, mediaType).MediaID
                        else:
                            print("image")
                            if media.get('edge_sidecar_to_children',None):
                                link = 'You should send a link of picture.'
                                print(link)
                                replyMsg = reply.TextMsg(toUser, fromUser, link)
                                return replyMsg.send()
                                # print('Downloading mutiple images of this post')
                                # for child_node in media['edge_sidecar_to_children']['edges']:
                                #     print('Saved as ' + download(child_node['node']['display_url'],
                                #                                  child_node['node']['shortcode'] + '.jpg') + '!')
                            else:
                                print("1")
                                name = url.split("/")
                                print(name[len(name) - 1])
                                print('Saved as ' + download(url,
                                                             name[len(name) - 1] + '.jpg') + '!')
                                myMedia = Media()
                                accessToken = Basic().get_access_token()
                                print("accessToken is: " + accessToken)
                                filePath = media['shortcode'] + '.jpg'   #请安实际填写
                                mediaType = "video"
                                link = myMedia.uplaod(accessToken, filePath, mediaType).MediaID
                    except Exception:
                        replyMsg = reply.TextMsg(toUser, fromUser, "Wrong link")
                        return replyMsg.send()
                # output = urllib.request.urlopen(
                #     "https://tagging.aminer.cn/query/" + input,
                #     context=context).read().decode(encoding='utf-8')
                # print(output)
                # dic = re.findall("\"([^\"]*)\": \"([^\"]*)\"", output)
                # url = "https://www.aminer.cn/search?"
                # ans = ""
                # for info in dic:
                #     if info[1] == "org":
                #         url += "o=" + urllib.parse.quote(info[0]) + "&"
                #         ans += "来自" + info[0]
                # for info in dic:
                #     if info[1] == "name":
                #         url += "n=" + urllib.parse.quote(info[0]) + "&"
                #         ans += "名为" + info[0] + "的学者"
                # for info in dic:
                #     if info[1] == "item":
                #         url += "k=" + urllib.parse.quote(info[0]) + "&"
                #         ans += "的" + info[0]
                # url = url[:-1]
                # link = "<a href=\"" + url + "\">" + ans + "</a>"
                # print(link)
                # replyMsg = reply.TextMsg(toUser, fromUser, link)
                    replyMsg = reply.ImageMsg(toUser, fromUser, link)
                    return replyMsg.send()
                else:
                    replyMsg = reply.TextMsg(toUser, fromUser, "您的输入有误")
                    return replyMsg.send()
            else:
                if recMsg.MsgType == 'image':
                    print(recMsg.MediaId)
                print ("暂且不处理")
                return "success"
        except Exception as Argment:
            return Argment


