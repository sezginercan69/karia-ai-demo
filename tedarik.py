import streamlit as st
import pandas as pd

st.title("📦 Tedarik Planlama Asistanı")

st.sidebar.header("Excel Yükle")
uploaded_file = st.sidebar.file_uploader("Tedarik Analizi için Dosya Yükle (.xlsx)", type=["xlsx"])

if not uploaded_file:
    st.warning("Lütfen tedarik verisini içeren Excel dosyasını yükleyin.")
    st.stop()

df = pd.read_excel(uploaded_file, engine="openpyxl")
df.columns = df.columns.astype(str)

# Tedarik segmenti belirle
def tedarik_segmenti(row):
    if row['stok_miktarı'] < 50 and row['satış_adedi'] > 500:
        return "1️⃣ Yüksek Öncelikli Tedarik"
    elif 50 <= row['stok_miktarı'] < 150 and 200 < row['satış_adedi'] <= 500:
        return "2️⃣ Orta Öncelikli Tedarik"
    elif row['stok_miktarı'] >= 150 or row['satış_adedi'] <= 200:
        return "3️⃣ Düşük Öncelikli Tedarik"
    else:
        return "🟡 Değerlendiriliyor"

df["tedarik_onceligi"] = df.apply(tedarik_segmenti, axis=1)

# Segmentleri sırayla göster
for segment in ["1️⃣ Yüksek Öncelikli Tedarik", "2️⃣ Orta Öncelikli Tedarik", "3️⃣ Düşük Öncelikli Tedarik"]:
    st.subheader(segment)
    filtreli = df[df["tedarik_onceligi"] == segment]
    st.write(f"Toplam: {len(filtreli)} ürün")
    st.dataframe(filtreli)
