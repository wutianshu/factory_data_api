import smtplib
from email.mime.text import MIMEText
from email.header import Header


class SendEmail(object):

    def __init__(self, origin, destination, email_pwd, email_header):
        self.origin = origin
        # 需要传入list
        self.destination = destination
        self.pwd = email_pwd
        self.email_header = email_header
        self.msg = ''

    def send_html_email(self):
        '''
        当用户发送信息过来时，发送邮件告知开发者
        :return:
        '''
        # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
        message = MIMEText(self.msg, 'html', 'utf-8')

        message['from'] = self.origin
        message['to'] = Header("智能协作质量组", 'utf-8')
        password = self.pwd
        message['subject'] = Header(self.email_header, 'utf-8').encode()
        smtp_server = "smtp.163.com"
        server = smtplib.SMTP(smtp_server, 25)  # SMTP协议默认端口是25
        # 打印出和SMTP服务器交互的所有信息。
        # server.set_debuglevel(1)
        # 登录SMTP服务器
        server.login(message['from'], password)

        # 发邮件，由于可以一次发给多个人，所以传入一个list;
        # 邮件正文是一个str，as_string()把MIMEText对象变成str。
        server.sendmail(message['from'], self.destination, message.as_string())
        server.quit()

    def create_email(self, work, study, issue):
        if work:
            _work = '<br>'.join(work.split('\n'))
        else:
            _work = ''
        if study:
            _study = '<br>'.join(study.split('\n'))
        else:
            _study = ''
        if issue:
            _issue = '<br>'.join(issue.split('\n'))
        else:
            _issue = ''

        head = '''<html>
<head>
    <meta charset="utf-8">
    <STYLE TYPE="text/css" MEDIA=screen>
        table.dataframe {
            border-collapse: collapse;
            border: 2px solid #a19da2; /*居中显示整个表格*/
            margin: auto;
        }

        table.dataframe thead {
            border: 2px solid #91c6e1;
            background: #f1f1f1;
            padding: 10px 10px 10px 10px;
            color: #333333;
        }

        table.dataframe tbody {
            border: 2px solid #91c6e1;
            padding: 10px 10px 10px 10px;
        }

        table.dataframe tr {
        }

        table.dataframe th {
            vertical-align: top;
            font-size: 14px;
            padding: 10px 10px 10px 10px;
            color: #105de3;
            font-family: arial;
            text-align: center;
        }

        table.dataframe td {
            padding: 10px 10px 10px 10px;
        }

        body {
            font-family: 宋体;
        }

        h1 {
            color: #5db446
        }

        div.header h2 {
            color: #0002e3;
            font-family: 黑体;
        }

        div.content h2 {
            text-align: center;
            font-size: 28px;
            text-shadow: 2px 2px 1px #de4040;
            color: #fff;
            font-weight: bold;
            background-color: #008eb7;
            line-height: 1.5;
            margin: 20px 0;
            box-shadow: 10px 10px 5px #888888;
            border-radius: 5px;
        }

        h3 {
            font-size: 22px;
            background-color: rgba(0, 2, 227, 0.71);
            text-shadow: 2px 2px 1px #de4040;
            color: rgba(239, 241, 234, 0.99);
            line-height: 1.5;
        }

        h4 {
            color: #e10092;
            font-family: 楷体;
            font-size: 20px;
            text-align: center;
        }

        td img { /*width: 60px;*/
            max-width: 300px;
            max-height: 300px;
        }

        table {
            table-layout: fixed;
        }

        table thead tr th:nth-child(9) {
            width: 10%
        }

        table tbody tr td:nth-child(9) {
            width: 10%
        }

    </STYLE>
</head>'''
        tail = '''</html>'''
        middler = '''<body>
<div class="content">
    <div>
        <h2 align="center" class="header">{}</h2>
    </div>
    <div>
        <table border="1" class="dataframe">
            <tbody>
                <tr>
                    <td>工作内容</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td>难点问题</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td>技术提升</td>
                    <td>{}</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
</body>'''.format(self.email_header, _work, _study, _issue)
        self.msg = head + middler + tail


if __name__ == '__main__':
    email = SendEmail(origin='shi_ren_**@163.com',
                      destination=['shi_ren_**@163.com'],
                      email_pwd='******',
                      email_header='测试发送邮件')
    email.create_email(work='这是本周工作', study='这是本周学习', issue='这是本周问题')
    email.send_html_email()
