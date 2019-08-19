# -*- coding: utf-8 -*-
# clint
# lintechoa@yingzi.com
# 2019/8/14 14:33

import nmap
import datetime
import threading
import requests
import chardet
import re
import os
import json
import queue
import urllib3
import xlwt

# 取消requests请求未认证https服务的警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MulThreading(threading.Thread):
    def __init__(self, que):
        """
        用的别人的多线程方法，也不知道什么意思，需要研究一下⚠
        :param que:
        """
        threading.Thread.__init__(self)
        self._queue = que

    def run(self):
        while not self._queue.empty():
            ip = self._queue.get()
            try:
                ports = PortScan().port_scan(ip)
                PortScan().nmap_scan(ip, ports)
            except Exception as e:
                print(e)
                pass


class PortScan:
    def __init__(self):
        pass

    @staticmethod
    def port_scan(ip):
        """
        调用当前路径下的masscan进行端口扫描发现，将发现的端口保存在masscan.json
        多次扫描会覆盖该json文件，每次扫描一个ip后就对json文件进行处理
        :param ip:
        :return:
        """
        # 新建一个列表保存扫描出中的端口
        temp_ports = []
        # 全端口扫描，masscan默认进行隐蔽扫描，每秒发送的速率为1000个包（目前测试最快最准确的速率）
        cmd = 'masscan %s -p 1-65535 -oJ masscan.json --rate 100 --wait 5' % ip
        print(cmd)
        os.system(cmd)
        # json文件会被复写，需扫描每个IP后就处理
        with open('masscan.json', 'r') as f:
            for line in f:
                if line.startswith('{ '):
                    temp = json.loads(line[:-2])
                    temp1 = temp["ports"][0]
                    temp_ports.append(str(temp1["port"]))
                    print(line)
        if len(temp_ports) > 50:
            temp_ports.clear()  # 如果端口数量大于50，说明可能存在防火墙，属于误报，清空列表
        return temp_ports

    def nmap_scan(self, ip, ports):
        """
        对于masscan发现的端口，调用nmap模块进行服务识别
        :param ip:
        :param ports:
        :return:
        """
        nm = nmap.PortScanner()
        try:
            for port in ports:
                # 对扫描出的ip的端口进行服务探测，隐蔽扫描，不ping主机是否存活
                res = nm.scan(ip, port, arguments='-Pn,-sS')
                # 探测结果为json嵌套，见wiki
                service_name = res['scan'][ip]['tcp'][int(port)]['name']
                print('[*]主机' + ip + '的' + str(port) + '端口服务为：' + service_name)
                if 'http' in service_name or service_name == 'sun-answerbook':
                    if service_name == 'https' or service_name == 'https-alt':
                        # url_port = 'https://' + ip + ':' + str(port)
                        # 导入urllib3库，忽略未认证警告
                        self.url_request(1, ip, port, service_name)
                    else:
                        # url_port = 'http://' + ip + ':' + str(port)
                        self.url_request(0, ip, port, service_name)
                else:
                    # 写文件保存
                    with open('scan_info.txt', 'a') as f:
                        f.write(ip + '\t' + str(port) + '\t' + service_name + '\n')
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def url_request(num, ip, port, service_name):
        try:
            if num == 1:
                url = 'https://' + ip + ':' + str(port)
            else:
                url = 'http://' + ip + ':' + str(port)
            res = requests.get(url, timeout=3, verify=False)
            # 获取网站的页面编码
            # res_coding = chardet.detect(res.content)
            # encode = res_coding['encoding']  # ASCII
            # # 将页面解码为utf-8，获取标题
            response = re.findall(u'<title>(.*?)</title>', res.content.decode('utf-8'), re.S)
            # print(response)  # 列表，取list[0]进行拼接
            if not response:  # 判断是否有页面服务
                with open('scan_info.txt', 'a') as f:
                    f.write(ip + '\t' + str(port) + '\t' + service_name + '\n')
            else:
                # response = response[0].decode(encode).decode('utf-8')
                banner = res.headers.get('server')
                print(banner)
                with open('scan_info.txt', 'a') as f:
                    f.write(ip + '\t' + str(port) + '\t' + banner + '\n')
        except Exception as e:
            print(e)
            pass

class Execute:
    def __init__(self, ip_file, white_ip_file):
        self.scan_info = []
        self.ip_file = ip_file
        self.white_ip_file = white_ip_file

    def check_white_port(self, ip, port):
        """
        根据传入的ip和端口判断是否属于白名单，如果不是，归类为新增端口
        :param ip:
        :param port:
        :return:
        """
        white_ip_list = []
        with open(self.white_ip_file) as f:
            for line in f:
                line = line.strip('\r\n')
                white_ip_list.append(line)
        # print('白名单： ' +  str(white_ip_list))
        ip_port = ip + ':' + str(port)
        # print(ip_port)
        if ip_port in white_ip_list:
            return True

    def write_xls(self, info_list):
        """
        我是用来将数据保存为xls的
        :param info_list:
        :return:
        """
        wb = xlwt.Workbook(encoding='utf-8')
        pattern = xlwt.Pattern()  # Create the Pattern
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = 22
        style = xlwt.XFStyle()  # Create the Pattern
        style.pattern = pattern  # Add Pattern to Style

        all_info = wb.add_sheet('端口开放情况', style)
        all_info.write(0, 0, 'ip地址', style)
        all_info.write(0, 1, '端口', style)
        all_info.write(0, 2, '服务信息', style)
        new_info = wb.add_sheet('新增对外开放的端口', style)
        new_info.write(0, 0, 'ip地址', style)
        new_info.write(0, 1, '端口', style)
        new_info.write(0, 2, '服务信息', style)
        new_row = 0     # 新sheet的行初始化

        for i, each_list in enumerate(info_list):
            all_info.write(i + 1, 0, each_list[0])
            all_info.write(i + 1, 1, each_list[1])
            all_info.write(i + 1, 2, each_list[2])
            # 如果没在白名单理，则是新增端口
            if not self.check_white_port(each_list[0], each_list[1]):
                new_info.write(new_row, 0, each_list[0])
                new_info.write(new_row, 1, each_list[1])
                new_info.write(new_row, 2, each_list[2])
                new_row += 1

        wb.save('report.xls')

    def main(self, count):
        que = queue.Queue()
        threads = []
        thread_count = count

        with open(self.ip_file) as f:
            for line in f:
                # ip_list.append(line.strip('\r\n'))
                que.put(line.strip('\r\n'))
        for i in range(thread_count):
            threads.append(MulThreading(que))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 处理保存结果的txt文件    
        with open('scan_info.txt', 'r+') as f:
            for line in f:
                res = line.strip('\r\n').split('\t')
                self.scan_info.append(res)
            f.seek(0)   # 定位文件初始位置
            f.truncate()    # 清空文件内容，避免以后重复写入
        print(self.scan_info)

        self.write_xls(self.scan_info) 
        

if __name__ == '__main__':
   # ip = '103.215.44.154'
   # res= PortScan().main(ip)
   # url = 'https://103.215.44.154:443'
   # print(res)
    start_time = datetime.datetime.now()
    ip_list = 'ip.txt'
    white_ip = 'white_ip.txt'
    Execute(ip_list, white_ip).main(20)
    mail_info = MailInfo()
    SendMail(mail_info).send_mail()     # 发送邮件
    
    spend_time = (datetime.datetime.now() - start_time)
    print('程序共运行了：' + str(spend_time))
