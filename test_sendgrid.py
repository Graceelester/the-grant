import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Get the SendGrid API key from environment variable
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
if not SENDGRID_API_KEY:
    raise RuntimeError("SENDGRID_API_KEY is not set in environment variables!")

sg = SendGridAPIClient(SENDGRID_API_KEY)

message = Mail(
    from_email=os.getenv("SENDGRID_VERIFIED_SENDER"),  # verified sender email
    to_emails=os.getenv("ADMIN_EMAIL"),                # admin email
    subject="Grant Application Received",
    plain_text_content="New grant application has been submitted."
)

try:
    response = sg.send(message)
    print("Email sent! Status code:", response.status_code)
except Exception as e:
    print("SendGrid error:", e)
