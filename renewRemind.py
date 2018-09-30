# -*- coding:utf-8 -*-
import re
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.header import Header
# import schedule
import time
import datetime


timeout = 30                       # 超时时间
charset = 'utf-8'		           # 请求页面的编码格式
conf_file = 'data/conf.ini'        # 配置文件
my_email = ''                      # 邮箱地址
my_password = ''                   # 邮箱授权码

subject = '【更新提示】'	 # email 中的主题
content = ''			 # email 中的内容
isRenew = False			 # 是否有更新
renew_dict = {}          # 更新记录
record_file = ''         # 记录文件
aim_email = ''           # 收件邮箱


def get_html(url, timeout=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request, timeout=timeout)
    return response.read()


def send_email(sub, cont):
    # send email
    global my_email, my_password
    sender = my_email                   # 发送方
    receiver = [aim_email]               # 收件方
    subject = sub                       # 邮件主题
    smtpserver = 'smtp.qq.com'          # 邮箱服务器
    username = my_email                 # 用户名
    password = my_password		# 授权码

    msg = MIMEText(cont, 'html', 'utf8')	 # 设置内容
    msg['Subject'] = Header(subject, 'utf8')	 # 设置主题
    msg['From'] = sender			# 设置发送方
    msg['To'] = ','.join(receiver)		# 设置接收方
    smtp = smtplib.SMTP_SSL(smtpserver, 465)
    # smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()


def Init():
    global renew_dict, my_email, my_password, record_file
    print('正在加载邮箱地址和授权码……')
    try:
        fp = open(conf_file, 'r', encoding='utf8')
    except Exception as e:
        print('加载失败，conf.ini文件不存在')
        raise Exception(e)
    lines = fp.readlines()
    my_email = lines[1].strip()     # 加载邮箱地址
    my_password = lines[3].strip()  # 加载邮箱授权码
    fp.close()

    print('正在加载更新记录……')
    # 提取更新情况记录
    fp = open(record_file, 'r', encoding='utf8')

    for line in fp:
        items = line.split(':#:')
        # print items
        key = items[0].strip()
        value = items[1].strip()
        # idx = line.find(':#:')
        # key = line[:idx].strip()
        # value = line[idx:].strip()
        renew_dict[key] = value

    print(renew_dict)

    fp.close()


def RenewCheck(key, src_url, pattern_str, charset):
    # 提示信息
    print('正在检查【%s】的更新状态……' % (key))

    # 检查更新
    global subject, content, isRenew, renew_dict
    # host = 'http://' + src_url.split('//')[1].split('/')[0]   # 检查网站的host地址
    html = get_html(src_url, timeout).decode(charset)        # 获得页面源码
    # print(html)

    # 解析源码
    # pattern = re.compile(pattern_str, re.S)
    items = re.findall(pattern_str, html)
    if items:
        items = [items[0]]

    # 清洗数据
    print(items)
    items = [x.strip() for x in items]
    # print(items)

    # 输出解析结果
    title = ' '.join(items)
    print(title)
    # raise NotImplemented

    # 判断是否有更新
    cur = title
    if key[-1] == ' ':
        key = key[:-1]
    if key in renew_dict:  # 判断之前有无记录
        last = renew_dict[key]
    else:
        last = None
    # print(last)
    # print(key)
    # print(renew_dict)
    if items and cur != last or last == None:
        # 如果有更新，发送邮件提示
        isRenew = True

        # 更新记录
        renew_dict[key] = cur
        fp = open(record_file, 'w')
        for item, value in list(renew_dict.items()):
            fp.write('%s:#:%s\n' % (item, value))
        fp.close()

        print('【%s】有更新，发送邮件……' % (key))
        subject += '%s ' % (key)
        content += '【%s】已经更新到【%s】，戳这里看详情：%s<br/>' % (key, cur, src_url)
    else:
        # 没有更新
        print('【%s】没有更新'%(key))


def job(id, email):
    global subject, content, isRenew, renew_dict, record_file, aim_email
    subject = '【更新提示】'  # email 中的主题
    content = ''  # email 中的内容
    isRenew = False  # 是否有更新
    renew_dict = {}  # 更新记录
    record_file = 'data/record/' + id + '.txt'  # 记录文件
    aim_email = email  # 收件邮箱

    # 提取更新情况记录
    Init()

    # 检查所有更新，并输出提示信息
    # 函数原型：
    # def RenewCheck( key,src_url,des_url,pattern_str,charset )
    # 参数介绍 :
    # key           - 检查对象，例如：西部世界等
    # src_url       - 检查对象的网站地址
    # des_url       - 如果有更新，提示中所指向的跳转地址
    # pattern_str   - 匹配正则表达式
    # charset       - 检查对象网站的编码
    catalogue_file = open('data/catalogue/' + id + '.txt', 'r', encoding='utf8')

    for line in catalogue_file.readlines():
        item = line.split('\t')
        print(item)
        try:
            if item[-1] == '1\n':
                RenewCheck(key=item[0], src_url=item[1], pattern_str=item[2], charset=item[3])
        except Exception as e:
            print('[ERROR]:%s' % e)
            continue
    catalogue_file.close()

    if isRenew:
        send_email(subject + '有更新！', content)
        t = datetime.datetime.now().strftime('%Y-%m-%d')
        send_log = open('send.log', 'a', encoding='utf8')
        send_log.write(t + ' ' + aim_email + '\n' + content)
        send_log.close()

        content = ''
        subject = '【更新提示】'  # email 中的主题
        isRenew = False  # 是否有更新
        renew_dict = {}  # 更新记录


def work():
    print('start')
    user_file = open('data/user.dat', 'r', encoding='utf8')
    for line in user_file.readlines():
        word = line.split('\t')
        print(word)
        if len(word) == 3 and word[-1] == '1\n':
            job(id=word[0], email=word[1])
    user_file.close()
    print('done!')


def query(id):
    print('start')
    user_file = open('data/user.dat', 'r', encoding='utf8')
    for line in user_file.readlines():
        word = line.split('\t')
        if word[0] == id:
            job(id=word[0], email=word[1])
    user_file.close()
    print('done!')


# schedule.every(2).minutes.do(work)
# schedule.every().hour.do(work)
# schedule.every().day.at("18:00").do(work)
# schedule.every(5).to(10).days.do(work)
# schedule.every().monday.do(work)
# schedule.every().wednesday.at("13:15").do(work)



if __name__ == '__main__':
    # job('oYwh408660opW2RQ0MaNK60XZLC0', '2382971319@qq.com')
    job('oYwh4086nDj-G_VwHIMXhDA9e8Mc', '2382971319@qq.com')
    # job('oYwh4086nDj-G_VwHIMXhDA9e8Mc', 'm13761635326@163.com')
    # work()
    # print('this is us\thttp://www.ttmeiju.vip/meiju/This.Is.Us.html\t<font color="#339999">内嵌双语字幕</font>\\s*</td>\\s*<td>([^>]*)</td>\tutf8\t1\n')
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    #     '''
    #     try:
    #         main()
    #     except Exception,e:
    #         print '[ERROR]:%s'%e
    #
    #     '''
