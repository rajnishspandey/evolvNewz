import pytz
import smtplib
from dotenv import load_dotenv
import os

load_dotenv()
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

from string_literals import JSON_PATH
from flask.helpers import get_flashed_messages

def add_ordinal(day):
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix}"

def convert_gmt_to_ist(gmt_time):
    gmt_timezone = pytz.timezone('GMT')
    ist_timezone = pytz.timezone('Asia/Kolkata')  # Indian Standard Time

    gmt_time = gmt_timezone.localize(gmt_time)
    ist_time = gmt_time.astimezone(ist_timezone)

    # Format IST time to show only time
    ist_time_str = ist_time.strftime(f"{add_ordinal(ist_time.day)}-{ist_time.strftime('%b')[:3]}-%y %H:%M").lower()

    return ist_time_str

# Function to send email
def send_email(feedback_name,feedback_text):
    subject = f"Feedback Submission from {feedback_name}"
    body = f"Feedback: {feedback_text}"
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, f"Subject: {subject}\n\n{body}")