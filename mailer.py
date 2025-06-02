import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_to_kindle(file_path, title):
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    kindle_email = os.getenv("KINDLE_EMAIL")

    msg = MIMEMultipart()
    msg["From"] = smtp_email
    msg["To"] = kindle_email
    msg["Subject"] = "Convert"

    with open(file_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_email, smtp_pass)
        server.sendmail(smtp_email, kindle_email, msg.as_string())
