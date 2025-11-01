import boto3
import smtplib
from email.mime.text import MIMEText

def send_email(cfg, message_body):
    subject = cfg["subject"]
    sender = cfg["sender"]
    recipient = cfg["recipient"]

    if cfg.get("use_ses"):
        ses = boto3.client("ses", region_name="eu-central-1")
        ses.send_email(
            Source=sender,
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": message_body}}
            }
        )
        print("E-Mail über AWS SES gesendet.")
    else:
        msg = MIMEText(message_body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient
        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as server:
            server.starttls()
            server.login(cfg["smtp_user"], cfg["smtp_password"])
            server.send_message(msg)
        print("E-Mail über SMTP gesendet.")
