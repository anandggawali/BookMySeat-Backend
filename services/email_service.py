import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:

    EMAIL = "dailycabsbe7@gmail.com"
    PASSWORD = "gpxp kjnw iwxh fcny"

    @staticmethod
    def send_otp(email: str, otp: str):

        subject = "DailyCabs Password Reset OTP"

        body = f"""
Hello,

Your DailyCabs OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request this, please ignore this email.

Regards,
DailyCabs Team
"""

        message = MIMEMultipart()
        message["From"] = EmailService.EMAIL
        message["To"] = email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(
            EmailService.EMAIL,
            EmailService.PASSWORD
        )

        server.send_message(message)

        server.quit()