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
import os
from renewRemind import query


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


def update_data(file, pattern_str, info_str):
    file_data = ""
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            word = line.split('\t')
            # print(word)
            if word[0] == pattern_str:
                continue
            file_data += line
        file_data += pattern_str + '\t' + info_str + '\n'
    with open(file, "w", encoding="utf-8") as f:
        f.write(file_data)
    # print(file_data)


def find_episode(name):
    url = "http://www.ttmeiju.vip/index.php/search/index.html?keyword=" + urllib.parse.quote(name)
    # print(url)
    try:
        # 抓取页面
        urlop = urllib.request.urlopen(url, timeout=100)
        data = urlop.read().decode('utf-8')
        # print(data)
        data = re.sub('\s', '', data)
        str = re.findall("<trclass=\"Scontent1\">(.*)</tr>", data)
        # print(str)
        if str:
            ans = re.findall("<ahref=\"(\S*)\.html", str[0])
            return 'http://www.ttmeiju.vip' + ans[0] + '.html'
        else:
            return ''
    except Exception:
        return ''


class Handle(object):
    def GET(self):
            data = web.input()
            if len(data) == 0:
                return "hello, this is handle view"
            signature = data.signature
            timestamp = data.timestamp
            nonce = data.nonce
            echostr = data.echostr
            token = "wechat"  # 请按照公众平台官网\基本配置中信息填写

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
            print("Handle Post webdata is ", webData)
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
                if txt[0] == "ins" and len(txt) == 2:  # 保存ins图片
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
                            if _media.get('edge_sidecar_to_children', None):
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

                    replyMsg = reply.ImageMsg(toUser, fromUser, link)
                    return replyMsg.send()

                if txt[0] == 'remind':  # 追剧助手
                    try:
                        if len(txt) == 2:
                            if txt[1] == 'unsubscribe':
                                update_data('data/user.dat', toUser, txt[1] + '\t0')
                                replyMsg = reply.TextMsg(toUser, fromUser, '服务已关闭')
                                return replyMsg.send()
                            elif txt[1] == 'query':
                                query(toUser)
                                replyMsg = reply.TextMsg(toUser, fromUser, '查询完毕')
                                return replyMsg.send()
                            elif txt[1] == 'list':
                                if not os.path.exists('data/catalogue/' + toUser + '.txt'):
                                    replyMsg = reply.TextMsg(toUser, fromUser, "请先提供接收提醒的邮箱")
                                    return replyMsg.send()
                                with open('data/catalogue/' + toUser + '.txt', "r", encoding="utf-8") as f:
                                    ans = ''
                                    for line in f:
                                        word = line.split('\t')
                                        # print(word)
                                        if word[-1] == '1\n':
                                            ans += word[0] + '\n'
                                    if ans == '':
                                        ans = '您还未进行订阅'
                                replyMsg = reply.TextMsg(toUser, fromUser, ans)
                                return replyMsg.send()

                            update_data('data/user.dat', toUser, txt[1] + '\t1')
                            user_catalogue = open('data/catalogue/' + toUser + '.txt', 'w', encoding='utf8')
                            user_record = open('data/record/' + toUser + '.txt', 'w', encoding='utf8')
                            user_catalogue.close()
                            user_record.close()
                            replyMsg = reply.TextMsg(toUser, fromUser, "您的更新提醒将于每天18:00发送至" + txt[1])
                            return replyMsg.send()

                        elif txt[1] == 'add' and len(txt) >= 3:
                            if not os.path.exists('data/catalogue/' + toUser + '.txt'):
                                replyMsg = reply.TextMsg(toUser, fromUser, "请先提供接收提醒的邮箱")
                                return replyMsg.send()
                            keyword = ''
                            for i in range(2, len(txt)):
                                keyword += txt[i] + ' '
                            aim_url = find_episode(keyword)
                            if not aim_url:
                                replyMsg = reply.TextMsg(toUser, fromUser, '未找到您所需的资源')
                                return replyMsg.send()
                            update_data('data/catalogue/' + toUser + '.txt', keyword, aim_url + '\t<font color="#339999">内嵌双语字幕</font>\s*</td>\s*<td>([^>]*)</td>\tutf8\t1')
                            replyMsg = reply.TextMsg(toUser, fromUser, keyword + '的资源地址位于' + aim_url)
                            return replyMsg.send()

                        elif txt[1] == 'delete' and len(txt) >= 3:
                            if not os.path.exists('data/catalogue/' + toUser + '.txt'):
                                replyMsg = reply.TextMsg(toUser, fromUser, "请先提供接收提醒的邮箱")
                                return replyMsg.send()
                            keyword = ''
                            for i in range(2, len(txt)):
                                keyword += txt[i] + ' '
                            aim_url = find_episode(keyword)
                            update_data('data/catalogue/' + toUser + '.txt', keyword, aim_url + '\t<font color="#339999">内嵌双语字幕</font>\s*</td>\s*<td>([^>]*)</td>\tutf8\t0')
                            replyMsg = reply.TextMsg(toUser, fromUser, keyword + '退订成功')
                            return replyMsg.send()

                        else:
                            raise NotImplemented

                    except Exception:
                        replyMsg = reply.TextMsg(toUser, fromUser, "您的输入有误")
                        return replyMsg.send()

                else:
                    replyMsg = reply.TextMsg(toUser, fromUser, "您的输入有误")
                    return replyMsg.send()
            else:
                if recMsg.MsgType == 'image':
                    print(recMsg.MediaId)
                print("暂且不处理")
                return "success"
        except Exception as Argment:
            return Argment

if __name__ == "__main__":
    # download("https://www.instagram.com/p/BlVTBLfApgU/?utm_source=ig_share_sheet&igshid=1jucjru4u1o6o", "1.jpg")
    # update_data('data/user.dat', '2', '2382971319@qq.com')
    print(find_episode('黑镜'))
