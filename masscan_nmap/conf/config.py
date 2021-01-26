# -*- coding: utf-8 -*-
# clint
# 2019/8/16 14:53

import time


class MailInfo:
    # 发送邮箱
    from_addr = 'test@126.com'
    # 邮箱授权码
    password = '123'
    # 接收邮箱
    toaddrs = ['test@126.com']
    # 邮件内容
    content = 'The scan for port has finshed.for details, see attached'
    # 邮件标题
    now_time = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))
    title = 'result of portscan  ' + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    # 附件路径
    filepath = '/home/techao/report.xls'
