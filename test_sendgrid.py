import os
print("SendGrid Key:", os.getenv("SENDGRID_API_KEY"))

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Get the API key from your environment variable
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# Initialize the client
sg = SendGridAPIClient(SENDGRID_API_KEY)

# Create the message
message = Mail(
    from_email="support@fordfoundationgrant.com",
    to_emails="danielhogwarts29@gmail.com",
    subject="Test Email",
    plain_text_content="Hello"
)

# Send the message
try:
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e)
