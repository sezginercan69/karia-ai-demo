import streamlit as st
import imaplib
import email
from bs4 import BeautifulSoup
import pandas as pd
import io

st.set_page_config(page_title="Kampanya Mail Bot", layout="centered")

st.title("📧 Kampanya Mail Bot")

st.info("Bu sayfa, Zara, H&M, Mango gibi sitelerden gelen kampanya maillerini tarar ve raporlar.")

EMAIL = st.text_input("📧 Gmail adresini gir:", value="seninmailadresin@gmail.com")
PASSWORD = st.text_input("🔑 Uygulama şifresini gir:", type="password")

if st.button("📨 Kampanya Maillerini Kontrol Et"):
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(EMAIL, PASSWORD)
        imap.select("INBOX")

        status, messages = imap.search(None, 'UNSEEN')
        mail_ids = messages[0].split()

        if len(mail_ids) == 0:
            st.info("📭 Yeni kampanya maili bulunamadı.")
        else:
            st.success(f"📨 {len(mail_ids)} yeni kampanya maili bulundu. Okunuyor...")

            kampanya_listesi = []

            for mail_id in mail_ids:
                status, msg_data = imap.fetch(mail_id, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                subject = msg["subject"]
                from_ = msg["from"]

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/html":
                            body = part.get_payload(decode=True)
                            soup = BeautifulSoup(body, "html.parser")
                            text = soup.get_text()
                            kampanya_listesi.append({
                                "Gönderen": from_,
                                "Konu": subject,
                                "İçerik": text[:500] + "..."
                            })
                            break
                else:
                    body = msg.get_payload(decode=True)
                    soup = BeautifulSoup(body, "html.parser")
                    text = soup.get_text()
                    kampanya_listesi.append({
                        "Gönderen": from_,
                        "Konu": subject,
                        "İçerik": text[:500] + "..."
                    })

            kampanya_df = pd.DataFrame(kampanya_listesi)
            st.dataframe(kampanya_df)

            # İndir butonu
            buffer = io.BytesIO()
            kampanya_df.to_excel(buffer, index=False, engine="openpyxl")
            st.download_button(
                label="📥 Kampanya Maillerini İndir (Excel)",
                data=buffer.getvalue(),
                file_name="kampanya_mailleri.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        imap.logout()

    except Exception as e:
        st.error(f"❌ Hata oluştu: {str(e)}")
