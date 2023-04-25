import smtplib
from threading import Thread
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import getenv

def mail_send(mail: str, code: str):
    msg = MIMEMultipart()
    msg['Subject'] = 'Код подтверждения!'
    html = f'<html><head></head><body><h2 style="text-align:center">Код подтверждения: {code}</h2></body></html>'
    body = MIMEText(html, 'html')
    msg.attach(body)

    Thread(target=send, args=(mail, msg)).start()

def send(email, msg):
    mail = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    mail.login(getenv('mail'),getenv('mail_password'))
    msg['From'] = getenv('mail')

    mail.sendmail(getenv('mail'), email, msg.as_string())
    mail.quit()