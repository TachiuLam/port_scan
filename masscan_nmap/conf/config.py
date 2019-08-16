# -*- coding: utf-8 -*-
# clint
# lintechoa@yingzi.com
# 2019/8/16 14:53

import time


class MailInfo:
    # 发送邮箱
    from_addr = 'pentest@126.com'
    # 邮箱授权码
    password = 'Hundun321abc'
    # 接收邮箱
    # toaddrs = ['huangzehong@yingzi.com']
    toaddrs = ['lintechao@yingzi.com']
    # 邮件内容
    content = 'The scan for port has finshed.for details, see attached'
    # 邮件标题
    now_time = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))
    title = 'result of portscan  ' + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    # 附件路径
    filepath = '/home/techao/report.xls'
