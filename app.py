import streamlit as st
import os

st.set_page_config(page_title="LCW AI Demo", layout="wide")

# Sayfa seçimi
sayfa = st.sidebar.radio("🧭 Sayfa Seçimi", ["Anasayfa", "Demo"])

# Anasayfa
if sayfa == "Anasayfa":
    st.video("Kaira.mp4")  # Video dosyasını göster
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
    st.markdown("### Devam etmek için sol üstten **Demo** sayfasını seçin.")

# Demo
elif sayfa == "Demo":
    exec(open("demo.py").read())
