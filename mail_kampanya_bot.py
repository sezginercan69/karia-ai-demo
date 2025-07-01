import streamlit as st
import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Kampanya Mail Bot", layout="wide")
st.title("📧 Kampanya Mail Bot")

st.info("Bu sayfa Zara, H&M, Mango gibi sitelerden gelen kampanya maillerini tarar ve raporlar.")

EMAIL = "kaira.kampanya@gmail.com"
PASSWORD = "jxowqewgaofsjzec"  # 16 hanelik uygulama şifren, boşluksuz


if st.button("📨 Kampanya Maillerini Kontrol Et"):
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(EMAIL, PASSWORD)
        imap.select("INBOX")

        status, messages = imap.search(None, 'ALL')  # Okunmuş + okunmamış tüm mailleri alır
        mail_ids = messages[0].split()[-50:]  # Son 50 maili al

        kampanya_listesi = []

        for mail_id in reversed(mail_ids):
            status, msg_data = imap.fetch(mail_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Konuyu çöz
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
            from_ = msg.get("From")
            date_ = msg.get("Date")

            # Tarihi biçimlendir
            try:
                parsed_date = email.utils.parsedate_to_datetime(date_)
                formatted_date = parsed_date.strftime("%d.%m.%Y %H:%M")
            except:
                formatted_date = date_

            # İçeriği al
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
            text = soup.get_text(separator=" ", strip=True)

            # Filtreleme: İçerikte hem % hem indirim geçiyorsa al
            if "%" in text and "indirim" in text.lower():
                # Firma belirleme
                if "mango" in from_.lower():
                    firma = "Mango"
                elif "zara" in from_.lower():
                    firma = "Zara"
                elif "hm" in from_.lower() or "h&m" in from_.lower():
                    firma = "H&M"
                elif "hm" in from_.lower() or "h&m" in from_.lower():
                    firma = "Lcw"
                    
                else:
                    firma = "Bilinmeyen"

                kampanya_listesi.append({
                    "Tarih": formatted_date,
                    "Firma": firma,
                    "Gönderen": from_,
                    "Konu": subject,
                    "İçerik": text[:300] + "..."
                })

        if kampanya_listesi:
            kampanya_df = pd.DataFrame(kampanya_listesi)
            st.success(f"📨 {len(kampanya_df)} kampanya maili bulundu ve listelendi.")
            st.dataframe(kampanya_df)

            buffer = io.BytesIO()
            kampanya_df.to_excel(buffer, index=False, engine="openpyxl")
            st.download_button(
                label="📥 Kampanya Maillerini İndir (Excel)",
                data=buffer.getvalue(),
                file_name="kampanya_mailleri.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("📭 % ve indirim içeren kampanya maili bulunamadı.")

        imap.logout()

    except Exception as e:
        st.error(f"❌ Hata oluştu: {str(e)}")
