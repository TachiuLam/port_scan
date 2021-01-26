# port_scan
## 1、外网端口扫描脚本
### 1.1、脚本描述
作用：端口发现 + 服务识别 + 结果保存  
开发语言：python3
### 1.2、扫描逻辑
调用masscan进行端口发现
利用python-nmap模块对发现的端口进行服务识别
如果识别出http/https服务，则利用http/https请求获取详细的服务信息
对所有发现的端口进行白名单过滤
根据过滤结果保存为开放端口和新增开放端口两个文件
### 1.3、具体模块说明
该脚本由三个功能模块组成，分别是执行扫描任务的模块、多线程调用模块、执行保存模块；依次介绍：
#### 1.3.1、任务扫描模块
类名：PortSacn
包含方法：port_scan(ip)、nmap_scan(self, ip, ports)、url_request(num, ip, port, service_name)
```
class PortScan:
    def __init__(self):
        """
        端口发现和服务识别任务都在这里执行
        """
        pass
    @staticmethod
    def port_scan(ip):
        """
        调用当前路径下的masscan进行端口扫描发现，将发现的端口保存在masscan.json
        多次扫描会覆盖该json文件，每次扫描一个ip后就对json文件进行处理
        :param ip:
        :return:
        """
    def nmap_scan(self, ip, ports):
        """
        对于masscan发现的端口，调用nmap模块进行服务识别
        :param ip:
        :param ports:
        :return:
        """
    @staticmethod
    def url_request(num, ip, port, service_name):
        """
        对识别服务为http/https的端口进行请求，获得详细服务信息
        :param num:
        :param ip:
        :param port:
        :param service_name:
        :return:
        """
 ```
#### 1.3.2、多线程调用模块
```
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
```
#### 1.3.3、执行\保存模块
类名：Execute
包含方法：check_white_port(ip, port)、write_xls(info_list)、main(thread_count)
```
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
    def write_xls(self, info_list):
        """
        我是用来将数据保存为xls的
        :param info_list:
        :return:
        """
    def main(self, thread_count):
        """
        主程序，传入设置的线程数，执行程序
        :param thread_count:
        :return:
        """
 ```

## 2、邮件发送脚本
### 2.1、脚本描述
作用：发送扫描结果
配置文件路径： ./conf/config.py
主程序路径：./send_mail.py
开发语言：python3
### 2.2、 处理逻辑
从配置文件中读取设置的发送邮箱等信息，发送到目标邮箱
### 2.3、说明
方法名和调用方式如下：
config.py
```
# -*- coding: utf-8 -*-
# clint
# 2019/8/16 14:53
 
import time
 
 
class MailInfo:
    # 发送邮箱
    from_addr = 'xxxxxxxx@126.com'
    # 邮箱授权码
    password = 'xxxxxx'
    # 接收邮箱
    toaddrs = ['']
```
send_mail.py
```
# -*- coding: utf-8 -*-
# clint
# 2019/8/16 14:48
# 主机名是中文可发送不了，会报错
 
from conf.config import MailInfo
  
class SendMail:
    def __init__(self, info):
        """
        传入配置信息
        :param info:
        """
        self.mail_info = info
 
    def send_mail(self):
        """
        按需修改配置文件，
        此方法直接调用即可
        :return:
        """
  
if __name__ == '__main__':
    mail_info = MailInfo()
    SendMail(mail_info).send_mail()
```
## 3、运行！
设置定时任务执行运行程序，实例化部分如下
```
if __name__ == '__main__':
    start_time = datetime.datetime.now()
    ip_f = None
    white_ip_f = None
    Execute(ip_f, white_ip_f).main(5)   # 扫描程序
    mail_info = MailInfo()
    SendMail(mail_info).send_mail()     # 发送邮件
    spend_time = (datetime.datetime.now() - start_time)
    print('程序共运行了：' + str(spend_time))
```
## 4、注意事项（关注一下避免踩坑）
我们这个扫描脚本涉及到两个并发，一个是masscan工具自身的设计，一个是设计的多线程执行模块
进行每个IP的端口发现时不调用多线程执行程序，而是利用os‘调用masscan工具，利用该工具自带的并发功能进行发现，每秒发送数据包自己设置；
当ip数增加时，就有必要调用多线程模块提高执行效率了；
所以这里是ip内的端口一个并发，多线程队列放入所有ip一个并发。
所以就需要注意两个值，一个是并发线程数（传参）；masscan每秒发包数，设置为固定。
外网那台机器，单线程执行，masscan设置为每秒发送1000个数据包，一分钟完成全端口扫描和服务发现，而且基本准确率；
但是。。。结合多线程并发运行，如果还设置每秒发送1000个数据包，假如你设置了100个线程，每秒发包理论上就是100*1000，带宽就撑不住，就会频繁丢包，速度是很快，但是误报率飙高。所以迁移的时候再自己慢慢测试调整这两个数值吧~

--------
## 一、脚本目录结构
### 1.主目录
```
[root@2152218414-1533899798118 portscanbat]# ll /home/techao/portscanbat
 
total 88
-rw-r--r-- 1 root root 11086 Dec 16 11:33 \
drwxr-xr-x 3 root root  4096 Dec 16 11:33 conf		# 邮箱配置信息
-rw-r--r-- 1 root root     0 Dec 16 11:33 __init__.py
drwxr-xr-x 2 root root  4096 Dec 16 11:33 log
-rw-r--r-- 1 root root     0 Dec 16 11:33 masscan.json
-rw-r--r-- 1 root root 11408 Dec 16 11:33 portscan.py		# 扫描程序
drwxr-xr-x 2 root root  4096 Dec 16 11:33 __pycache__
-rw-r--r-- 1 root root 42496 Dec 16 11:33 reports.xls
-rw-r--r-- 1 root root     0 Dec 16 11:33 scan_info.txt
-rw-r--r-- 1 root root  1418 Dec 16 11:33 send_mail.py		# 邮件发送程序
drwxr-xr-x 2 root root  4096 Dec 16 11:33 static 	# ip地址
```
### 2.IP地址文件
```
[root@2152218414-1533899798118 portscanbat]# ll static/
total 36
-rw-r--r-- 1 root root   195 Dec 16 11:33 derek.txt		# 德里克IP地址
-rw-r--r-- 1 root root  2140 Dec 16 11:33 ip.bat.txt	
-rw-r--r-- 1 root root  2140 Dec 16 11:33 ip.txt		# 需要扫描的IP地址
-rw-r--r-- 1 root root 17920 Dec 16 11:33 white.xls		# 白名单IP
-rw-r--r-- 1 root root   551 Dec 16 11:33 yangxiang.txt # 扬翔IP地址
```
需要添加/修改IP地址，直接修改对应txt文件即可

### 3.邮箱信息配置
```
[root@2152218414-1533899798118 portscanbat]# vim conf/config.py 


class MailInfo:
    # 发送邮箱
    # from_addr = 'test@126.com'
    from_addr = 'test@126.com'
    # 邮箱授权码
    #password = '123'
    password = '123'
    # 接收邮箱
    #toaddrs = ['test@126.com']
    # toaddrs = ['test@126.com']
    toaddrs = ['test@126.com','test@126.com']
    # 邮件内容
    content = 'The scan for port has finshed.for details, see attached'
    # 邮件标题
    now_time = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))
    title = '外网端口扫描结果  ' + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    # 附件路径
    filepath = 'reports.xls'
```                                                                                                                                                                                                                                                                                                        
## 二、脚本使用
目前利用crontab，在每天凌晨三点和晚上九点执行，相关配置在上述文件中进行配置

### 1.定时脚本
```
crontab -e
 
0 21 * * * cd /home/techao/portscan_v2/; python3 test3.py &>> ./log/all.log
0 3 * * * cd /home/techao/portscan_v2/; python3 test3.py &>> ./log/all.log
```


