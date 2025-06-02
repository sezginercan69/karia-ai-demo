import streamlit as st
import pandas as pd

def run(veri):
    st.title("📦 Tedarik Planlama Asistanı")

    st.markdown("Satış hızına ve stok miktarına göre ürünler için tedarik önerileri sunulmaktadır.")

    kategori_listesi = veri["kategori"].dropna().unique()
    secilen_kategori = st.sidebar.selectbox("Kategori seçin", kategori_listesi)

    filtrelenmis = veri[veri["kategori"] == secilen_kategori]

    for _, row in filtrelenmis.iterrows():
        urun = row["ürün_ismi"]
        stok = row["stok_miktarı"]
        hiz = row["satış_hızı"]

        if hiz > 0:
            gun_kaldi = round(stok / hiz)
            durum = "🚨 Tedarik Gerekiyor" if gun_kaldi < 15 else "✅ Stok Yeterli"
            st.markdown(f"**{urun}** – Tahmini stok süresi: {gun_kaldi} gün | **{durum}**")
        else:
            st.markdown(f"**{urun}** – Satış verisi yetersiz, analiz yapılamıyor.")
