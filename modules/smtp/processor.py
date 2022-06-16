import smtplib

from email.mime.text import MIMEText
from conf import EMAIL_FOR_SMTP


def send_email(to: str, title: str, body: str):
    msg = MIMEText(body)
    msg['Subject'] = title
    msg['From'] = EMAIL_FOR_SMTP
    msg['To'] = to

    s = smtplib.SMTP('localhost')
    s.sendmail(EMAIL_FOR_SMTP, [to], msg.as_string())
    s.quit()
