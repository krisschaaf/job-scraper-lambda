import smtplib
from email.mime.text import MIMEText


def send_email(cfg, message_body):
    subject = cfg["subject"]
    sender = cfg["sender"]
    recipient = cfg["recipient"]

    msg = MIMEText(message_body, "html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as server:
        server.starttls()
        server.login(cfg["smtp_user"], cfg["smtp_password"])
        server.send_message(msg)
    print("E-Mail über SMTP gesendet.")


def format_email_body(new_jobs, old_jobs):
    html = ["<html><body style='font-family:sans-serif'>"]

    html.append("<h2>🆕 Neue Stellen</h2>")
    if new_jobs:
        html.append("<ul>")
        for j in new_jobs:
            html.append(f"<li><b>{j['title']}</b> ({j['term']})<br><a href='{j['url']}'>{j['url']}</a></li>")
        html.append("</ul>")
    else:
        html.append("<p><i>Keine neuen Stellen gefunden.</i></p>")

    html.append("<hr style='margin:20px 0;'>")

    html.append("<h2>📁 Bereits bekannte Stellen</h2>")
    if old_jobs:
        html.append("<ul>")
        for j in old_jobs:
            html.append(f"<li>{j['title']} ({j['term']})<br><a href='{j['url']}'>{j['url']}</a></li>")
        html.append("</ul>")
    else:
        html.append("<p><i>Keine bekannten Stellen derzeit gelistet.</i></p>")

    html.append("</body></html>")
    return "\n".join(html)