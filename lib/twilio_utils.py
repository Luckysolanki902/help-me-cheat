import os
from twilio.rest import Client as TwilioClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Twilio credentials and numbers from environment variables
twilio_sid = os.getenv("TWILIO_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_NUMBER")
recipient_number = os.getenv("RECIPIENT_NUMBER")

# Initialize Twilio client
twilio_client = TwilioClient(twilio_sid, twilio_auth_token)

def send_whatsapp_message(message):
    try:
        print("Sending the received response via WhatsApp...")
        twilio_client.messages.create(
            from_=f"whatsapp:{twilio_number}",
            body=message,
            to=f"whatsapp:{recipient_number}"
        )
        print("Message sent via WhatsApp.")
    except Exception as e:
        print(f"Failed to send message via WhatsApp: {e}")
