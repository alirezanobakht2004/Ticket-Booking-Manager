import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config  # Add your email credentials here

def send_otp_email(to_email, otp_code):
    sender_email = Config.EMAIL_SENDER
    sender_password = Config.EMAIL_PASSWORD
    subject = "Your OTP Code"
    body = f"Your OTP code is: {otp_code}. It is valid for 2 minutes."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
