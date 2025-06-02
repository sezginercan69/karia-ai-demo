import streamlit as st
import os
import tedarik

st.set_page_config(page_title="LCW AI Demo", layout="wide")

# Sayfa seçimi
sayfa = st.sidebar.radio("🧭 Sayfa Seçimi", ["Anasayfa", "Akıllı Kampanya Analizi", "Tedarik Planlama Asistanı"])

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

    Bu sayede hem stoklarınızı daha iyi yönetebilir hem de satışlarınızı artırabilirsiniz.
    """)
    st.markdown("---")
    st.success("💡 Otomatik kampanya üretimi")
    st.success("📊 Günlük ciro simülasyonu")
    st.success("🧠 Yapay zeka destekli karar önerileri")
    st.success("📈 ROI ve indirim oranı analizi")
    st.markdown("---")
    st.markdown("### Devam etmek için sol üstten **Akıllı Kampanya Analizi** sayfasını seçin.")

# Demo
elif sayfa == "Akıllı Kampanya Analizi":
    exec(open("demo.py").read())

# Tedarik Planlama Asistanı
elif sayfa == "Tedarik Planlama Asistanı":
    import pandas as pd  # Eğer zaten dosyada yoksa başta bir kere yeter
    st.header("📦 Tedarik Planlama Asistanı")

    uploaded_file = st.file_uploader("Tedarik verisini yükleyin (.xlsx)", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
            st.success("Dosya başarıyla yüklendi!")
            st.dataframe(df.head())  # İstersen sil veya gizle
        except Exception as e:
            st.error(f"Dosya okunurken hata oluştu: {e}")
    else:
        st.warning("Lütfen bir dosya yükleyin.")

