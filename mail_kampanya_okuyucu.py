import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import pandas as pd

def kampanya_mailleri_cek(email_user, email_pass, folder="INBOX", limit=50):
    kampanyalar = []

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_user, email_pass)
    mail.select(folder)

    _, search_data = mail.search(None, 'ALL')
    mail_ids = search_data[0].split()[-limit:]

    for i in reversed(mail_ids):
        _, msg_data = mail.fetch(i, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
        
        from_ = msg.get("From")
        date_ = msg.get("Date")

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/html":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            if msg.get_content_type() == "text/html":
                body = msg.get_payload(decode=True).decode(errors="ignore")

        soup = BeautifulSoup(body, "html.parser")
        text = soup.get_text(separator="\n", strip=True)

        kampanyalar.append({
            "from": from_,
            "subject": subject,
            "date": date_,
            "body_snippet": text[:200]
        })

    mail.logout()
    return pd.DataFrame(kampanyalar)
