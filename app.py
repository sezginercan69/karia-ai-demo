import streamlit as st
import os

st.set_page_config(page_title="LCW AI Demo", layout="wide")

# Sayfa seçimi
sayfa = st.sidebar.radio("🧭 Sayfa Seçimi", ["Anasayfa", "Akıllı Kampanya Analizi", "Tedarik Planlama Asistanı", "Kampanya Mail Bot"])

# Anasayfa
if sayfa == "Anasayfa":
    st.video("Kaira.mp4")  # Video dosyasını göster
    st.title("Kaira – Fiyatlandırma & Kampanya Öneri Asistanı")

    st.markdown("""
    Hoş geldiniz!

    Bu uygulama yüklediğiniz ürün verisine göre:

    ✅ Yeni fiyat önerir  
    ✅ Uygun kampanyaları analiz eder  
    ✅ Günlük bazlı ciro tahmini sunar  
    ✅ Kampanya başarısını tahmin eder  
    ✅ Tedarik planlama önerileri üretir

    Bu sayede hem stoklarınızı daha iyi yönetebilir hem de satışlarınızı artırabilirsiniz.
    """)
    st.markdown("---")
    st.success("💡 Otomatik kampanya üretimi")
    st.success("📊 Günlük ciro simülasyonu")
    st.success("🧠 Yapay zeka destekli karar önerileri")
    st.success("📦 Tedarik planlama içgörüleri")
    st.markdown("---")
    st.markdown("### Devam etmek için sol üstten bir sayfa seçin.")

# Akıllı Kampanya Analizi
elif sayfa == "Akıllı Kampanya Analizi":
    exec(open("demo.py").read())

# Tedarik Planlama Asistanı
elif sayfa == "Tedarik Planlama Asistanı":
    exec(open("tedarik.py").read())
