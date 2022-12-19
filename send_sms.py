import os 
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

<<<<<<< HEAD
account_sid = ''
auth_token = ''
client = Client(st.secrets["account_sid"], st.secrets["auth_token"])
=======
account_sid = ''
auth_token = ''
client = Client(account_sid, auth_token)
>>>>>>> 321c70a (update)

def sendSMS(messages,phone_number):
    message = client.messages.create(
        body=messages,
        from_='+12724358071',
        to='+977'+phone_number
    )
<<<<<<< HEAD
    return
=======
    return
>>>>>>> 321c70a (update)
