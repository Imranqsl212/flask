import os
from twilio.rest import Client


my_email = os.getenv('EMAIL')
password = os.getenv('PASS')



def send_message(phone_number, message):
    account_sid = os.getenv('YOUR_TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('YOUR_TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('YOUR_TWILIO_PHONE_NUMBER')

    client = Client(account_sid, auth_token)

    client.messages.create(
        body=message,
        from_=twilio_number,
        to=phone_number
    )

