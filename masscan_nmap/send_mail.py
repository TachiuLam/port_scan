int
# lintechoa@yingzi.com
# 2019/8/16 14:48

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from conf.config import MailInfo


class SendMail:
    def __init__(self, info):
        self.mail_info = info

    def send_mail(self):
        pass
        text_apart = MIMEText(self.mail_info.content)
        excel_file = self.mail_info.filepath
        excel_file_name = 'scan_info-' + self.mail_info.now_time + '.xls'
        excel_apart = MIMEApplication(open(excel_file, 'rb').read())
        excel_apart.add_header('Content-Disposition', 'attachment', filename=excel_file_name)

        m = MIMEMultipart()
        m.attach(excel_apart)
        m.attach(text_apart)
        m['Subject'] = self.mail_info.title
        m['from'] = self.mail_info.from_addr
        m['to'] = ','.join(self.mail_info.toaddrs)

        try:
            server = smtplib.SMTP('smtp.126.com')
            server.login(self.mail_info.from_addr, self.mail_info.password)
            server.sendmail(self.mail_info.from_addr, self.mail_info.toaddrs, m.as_string())
            print('report has sended to your email !')
            server.quit()
        except smtplib.SMTPException as e:
            print('fail to send email:', e)  # 打印错误


if __name__ == '__main__':
    mail_info = MailInfo()
    SendMail(mail_info).send_mail()
