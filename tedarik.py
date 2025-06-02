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

def tedarik_segmenti(row):
    yas = max(row["ürün_yaşı"], 1)
    stok = row["stok_miktarı"]
    satis_adedi = row["satış_adedi"]

    gunluk_satis = satis_adedi / yas

    if gunluk_satis > 1.5 and stok < 50:
        return "🔴 Yüksek Öncelikli Tedarik"
    elif gunluk_satis > 0.7 and stok < 100:
        return "🟠 Orta Öncelikli Tedarik"
    else:
        return "🟢 Düşük Öncelikli Tedarik"

df["tedarik_onceligi"] = df.apply(tedarik_segmenti, axis=1)

# Segmentleri sırayla göster
for segment in ["🔴 Yüksek Öncelikli Tedarik", "🟠 Orta Öncelikli Tedarik", "🟢 Düşük Öncelikli Tedarik"]:
    st.subheader(segment)
    filtreli = df[df["tedarik_onceligi"] == segment]
    st.write(f"Toplam: {len(filtreli)} ürün")
    st.dataframe(filtreli)

