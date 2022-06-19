import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from conf import SENDGRID_EMAIL, SENDGRID_API_KEY


def send_email(to_emails, subject, body):

    sg = SendGridAPIClient(os.environ.get(SENDGRID_API_KEY))
    message = Mail(
        from_email=SENDGRID_EMAIL, to_emails=to_emails, subject=subject, html_content=f"<strong>{body}</strong>"
    )
    try:
        response = sg.send(message)
        print(response.status_code)  # todo update notification info, save status for process errors
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
