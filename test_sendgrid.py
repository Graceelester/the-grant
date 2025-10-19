import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

if not SENDGRID_API_KEY:
    raise ValueError("SENDGRID_API_KEY not set. Run 'export SENDGRID_API_KEY=\"your-key\"' before running this script.")

sg = SendGridAPIClient(SENDGRID_API_KEY)
message = Mail(
    from_email="support@fordfoundationgrant.com",
    to_emails="danielhogwarts29@gmail.com",
    subject="Test Email",
    plain_text_content="Hello"
)

try:
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e)

