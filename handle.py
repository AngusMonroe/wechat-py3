# -*- coding: utf-8 -*-
# filename: handle.py
import hashlib
import reply
import receive
import media
import web
import requests
from basic import Basic
import ssl
import urllib.request
import urllib.parse
import re

def download(url, local_filename):
    r = requests.get(url, stream=True)
    print("downloading...")
    with open("./img/" + local_filename, 'wb') as f:
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
            print ("Handle Post webdata is ", webData)
            # 后台打日志
            recMsg = receive.parse_xml(webData)
            if recMsg.MsgType == 'event':
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                event = recMsg.Event
                if event == 'subscribe':  # 判断如果是关注则进行回复
                    content = "你在池塘里活得很好，泥鳅很丑但会说喜庆话，癞哈蟆很马虎但很有趣，田螺是个温柔的自闭症，小鲫鱼是你们共同的女神。\n有一天你听说，江河湖海，哪个都要更大，更好。\n你跳了出去，遇见了美丽的海豚，雄壮的白鲸，婀娜多姿的热带鱼，的确都是好的。\n\n就是偶尔，觉得世界很空，生活很咸。"
                    replyMsg = reply.TextMsg(toUser, fromUser, content)
                    return replyMsg.send()
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
                        _media = r.json()['graphql']['shortcode_media']
                        if _media['is_video']:
                            print("video")
                            print('Saved as ' + download(_media['display_url'],
                                         _media['shortcode'] + '.mp4') + '!')
                            myMedia = media.Media()
                            accessToken = Basic().get_access_token()
                            filePath = "./img/" + _media['shortcode'] + '.jpg'
                            mediaType = "video"
                            link = myMedia.uplaod(accessToken, filePath, mediaType)
                        else:
                            print("image")
                            if _media.get('edge_sidecar_to_children',None):
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
                                print('Saved as ' + download(_media['display_url'],
                                         _media['shortcode'] + '.jpg') + '!')
                                myMedia = media.Media()
                                print("media done")
                                accessToken = Basic().get_access_token()
                                filePath = "./img/" + _media['shortcode'] + '.jpg'   # 请按实际填写
                                mediaType = "image"
                                link = myMedia.uplaod(accessToken, filePath, mediaType)
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

if __name__ == "__main__":
    download("https://www.instagram.com/p/BlVTBLfApgU/?utm_source=ig_share_sheet&igshid=1jucjru4u1o6o", "1.jpg")
