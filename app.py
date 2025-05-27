import streamlit as st
import os

st.set_page_config(page_title="LCW AI Demo", layout="wide")

# Sayfa seçimi
sayfa = st.sidebar.radio("🧭 Sayfa Seçimi", ["Anasayfa", "Kampanya Asistanı"])

# Anasayfa
if sayfa == "Anasayfa":
    st.image("karia_header.png", use_container_width=True)
    st.title("📦 Karia – Akıllı Kampanya Asistanı")

    st.markdown("""
    Hoş geldiniz!

    Bu uygulama yüklediğiniz ürün verisine göre:

    ✅ Yeni fiyat önerir  
    ✅ Uygun kampanyaları analiz eder  
    ✅ Günlük bazlı ciro tahmini sunar  
    ✅ Kampanya başarısını tahmin eder

    Bu sayede hem stoklarınızı daha iyi yönetebilir hem de satışlarınızı artırabilirsiniz.
    """)
    st.markdown("---")
    st.success("💡 Otomatik kampanya üretimi")
    st.success("📊 Günlük ciro simülasyonu")
    st.success("🧠 Yapay zeka destekli karar önerileri")
    st.success("📈 ROI ve indirim oranı analizi")
    st.markdown("---")
    st.markdown("### Devam etmek için sol üstten **Kampanya Asistanı** sayfasını seçin.")

# Demo
elif sayfa == "Kampanya Asistanı":
    exec(open("demo.py").read())
