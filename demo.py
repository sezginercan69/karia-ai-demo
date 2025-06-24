# PART 1
import os
import streamlit as st
import pandas as pd
import requests
import random
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# OpenRouter API key
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# Sayfa yapılandırması
st.image("karia_header.png", use_container_width=True)
st.title("Kaira – Fiyatlandırma & Kampanya Öneri Asistanı")

# Stil – Kutu tasarımı
style = """
<style>
    .ozellik-kutu {
        padding: 12px 18px;
        margin-bottom: 10px;
        background: linear-gradient(135deg, #1c1c1c, #3d3d3d);
        color: white;
        border-radius: 10px;
        font-size: 16px;
        border: 1px solid #555;
    }
</style>
"""
st.markdown(style, unsafe_allow_html=True)

def ozellik_satiri(baslik, deger):
    st.markdown(f'<div class="ozellik-kutu"><strong>{baslik}:</strong> {deger}</div>', unsafe_allow_html=True)

# Excel dosyası yükleme
st.sidebar.header("Excel Yükle")
uploaded_file = st.sidebar.file_uploader("Ürün Excel Dosyasını Yükleyin (.xlsx)", type=["xlsx"])

if not uploaded_file:
    st.warning("Lütfen sol menüden bir ürün dosyası yükleyin.")
    st.stop()

@st.cache_data
def load_data(file):
    df = pd.read_excel(file, engine="openpyxl")
    df.columns = df.columns.astype(str)
    df = df.dropna(subset=["ürün_ismi"])
    df["ürün_ismi"] = df["ürün_ismi"].astype(str)
    return df
    
@st.cache_data
def load_user_interactions(file):
    try:
        df_users = pd.read_excel(file, sheet_name=1, engine="openpyxl")
        df_users.columns = df_users.columns.astype(str)
        return df_users
    except Exception as e:
        st.warning("İkinci sayfa (sheet2) yüklenemedi veya geçersiz.")
        return None

kullanici_verisi = load_user_interactions(uploaded_file)

veri = load_data(uploaded_file)

st.sidebar.header("Model Seçimi")
model_secimi = st.sidebar.selectbox(
    "Bir model seçin:",
    ["openai/gpt-3.5-turbo", "openai/gpt-4o-mini"]
)

st.sidebar.header("Kampanya Seçimi")

kampanya_secimi = st.sidebar.radio(
    "Bir kampanya ekranı seçin:",
  ["🧾 Ürün Fiyatlandırma Analizi", "📊 Ürün Bazlı Kampanya Dashboardu", "👥 Müşteri Segment Kampanyaları"]
)

show_dashboard = kampanya_secimi == "📊 Ürün Bazlı Kampanya Dashboardu"
show_segment_dashboard = kampanya_secimi == "👥 Müşteri Segment Kampanyaları"

st.sidebar.header("Ürün Seçimi")
secim = st.sidebar.selectbox("Bir ürün seçin:", veri["ürün_ismi"].unique())
secili_urun = veri[veri["ürün_ismi"] == secim].iloc[0]
if not show_dashboard and not show_segment_dashboard:
    # Ürün bilgisi gösterimi sadece hiçbir kampanya ekranı açık değilse gösterilsin
    st.subheader(f"🧾 Seçilen Ürün Bilgileri – {secili_urun['ürün_ismi']}")
    ozellik_satiri("Kategori", secili_urun['kategori'])
    ozellik_satiri("Mevcut Fiyat", f"{secili_urun['mevcut_fiyat']} TL")
    ozellik_satiri("Ürün Maliyeti", f"{secili_urun['ürün_maliyeti']} TL")
    ozellik_satiri("Stok Miktarı", secili_urun['stok_miktarı'])
    ozellik_satiri("Satış Hızı", f"{secili_urun['satış_hızı']} / gün")
    ozellik_satiri("Ürün Yaşı", f"{secili_urun['ürün_yaşı']} gün")
    ozellik_satiri("Beden Bulunurluğu", f"%{round(secili_urun['beden_bulunurluğu_oranı']*100)}")
    ozellik_satiri("Rakip Fiyat", f"{secili_urun['rakip_fiyat']} TL")
    ozellik_satiri("Hedef Kârlılık", f"%{round(secili_urun['hedef_karlılık_oranı']*100)}")
    ozellik_satiri("Dönüşüm Oranı", f"%{round(secili_urun['kategori_dönüşüm_oranı']*100)}")
    ozellik_satiri("Tıklama / Satış Oranı", f"%{round(secili_urun['tıklama_satış_oranı']*100)}")
    ozellik_satiri("Yaşam Döngüsü", secili_urun['yaşam_döngüsü'])
    ozellik_satiri("İade Oranı", f"%{round(secili_urun['iade_oranı']*100)}")
    ozellik_satiri("Sepette Bırakılma Oranı", f"%{round(secili_urun['sepette_bırakılma_oranı']*100)}")

    st.markdown("### 🤖 Kaira'dan Öneri Al")
    if st.button("💡 Ürün İçin Tavsiye Al"):
        with st.spinner("Kaira düşünüyor..."):
            prompt = f"""
            Sen bir e-ticaret uzmanı yapay zekasısın. Aşağıdaki ürün bilgilerine göre:
            1. Eğer gerekliyse yeni bir satış fiyatı öner, gerek değilse mevcut fiyatı koru.
            2. Uygun bir kampanya önerisi sun (eğer gerekiyorsa).
            3. Tüm kararlarının nedenlerini kısa ve net şekilde açıkla.

            Ürün Bilgileri:
            - Kategori: {secili_urun['kategori']}
            - Mevcut Fiyat: {secili_urun['mevcut_fiyat']} TL
            - Ürün Maliyeti: {secili_urun['ürün_maliyeti']} TL
            - Stok: {secili_urun['stok_miktarı']}
            - Satış Hızı: {secili_urun['satış_hızı']} / gün
            - Yaş: {secili_urun['ürün_yaşı']} gün
            - Beden Bulunurluğu: %{round(secili_urun['beden_bulunurluğu_oranı']*100)}
            - Rakip Fiyat: {secili_urun['rakip_fiyat']} TL
            - Hedef Kârlılık: %{round(secili_urun['hedef_karlılık_oranı']*100)}
            - Dönüşüm Oranı: %{round(secili_urun['kategori_dönüşüm_oranı']*100)}
            - Tıklama / Satış Oranı: %{round(secili_urun['tıklama_satış_oranı']*100)}
            - Yaşam Döngüsü: {secili_urun['yaşam_döngüsü']}
            - İade Oranı: %{round(secili_urun['iade_oranı']*100)}
            - Sepette Bırakılma Oranı: %{round(secili_urun['sepette_bırakılma_oranı']*100)}
            """

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_secimi,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30
            )

            try:
                result = response.json()["choices"][0]["message"]["content"]
                st.success("Kaira'nın Önerisi:")
                st.markdown(result)
            except Exception as e:
                st.error("Bir hata oluştu. Lütfen tekrar deneyin.")


# Kampanya üretim fonksiyonu
# PART 2

def generate_campaigns(df):
    campaigns = []
    duration_days = 5

    # Kampanya kuralları
    conditions = [
        (df["stok_miktarı"] > 100) & (df["satış_hızı"] < 1),
        (df["tıklama_satış_oranı"] < 0.05) & (df["kategori_dönüşüm_oranı"] > 0.1),
        (df["ürün_yaşı"] > 90) & (df["stok_miktarı"] > 50),
        (df["stok_miktarı"] < 20) & (df["satış_hızı"] < 1),
        (df["beden_bulunurluğu_oranı"] < 0.3)
    ]
    names = [
        "Stok Temelli Kampanya", 
        "Düşük Dönüşüm Odaklı", 
        "Yaşlı Ürünleri Hızlandır", 
        "Düşük Stoklu Ürünler için Fırsat Kuponu", 
        "Kırık Beden Ürünleri Hızlandır"
    ]
    reasons = [
        "Stok fazlası olup satışı yavaş olan ürünleri eritmek için oluşturuldu.",
        "Tıklama oranı yüksek ama dönüşüm düşük ürünleri harekete geçirmek için önerildi.",
        "Uzun süredir satılmayan ürünlerin stok maliyetini azaltmak hedeflenmiştir.",
        "Stok seviyesi azalmış ve satışı yavaşlayan ürünler için kupon bazlı fırsat sunulması önerilir.",
        "Beden çeşitliliği azalmış (kırık beden) ürünler için stok eritme kampanyası önerilmiştir."
    ]

    for cond, name, reason in zip(conditions, names, reasons):
        subset = df[cond]
        if len(subset) < 5:
            continue

        sampled = subset.sample(min(30, len(subset)))
        campaign_products = []
        expected_revenue = 0
        total_roi = 0
        total_click_increase = 0

        for _, row in sampled.iterrows():
            discount_rate = random.uniform(10, 30)
            new_price = round(row["mevcut_fiyat"] * (1 - discount_rate / 100))
            expected_sales_increase = row["satış_hızı"] * (1 + discount_rate / 15)
            added_revenue = expected_sales_increase * new_price
            roi = round((added_revenue - row["satış_hızı"] * row["mevcut_fiyat"]) / (row["stok_miktarı"] * row["ürün_maliyeti"] * discount_rate / 100 + 1), 2)

            campaign_products.append({
                "name": row["ürün_ismi"],
                "current_price": row["mevcut_fiyat"],
                "new_price": new_price
            })

            expected_revenue += added_revenue
            total_click_increase += row["tıklama_satış_oranı"] * discount_rate
            total_roi += roi

        daily = expected_revenue / duration_days
        daily_revenue = [round(daily * (1 + 0.1 * random.uniform(-1, 1)), 2) for _ in range(duration_days)]

        discount_list = []
        for p in campaign_products:
            try:
                cp = float(str(p["current_price"]).replace(",", ".").replace(" TL", "").strip())
                np = float(str(p["new_price"]).replace(",", ".").replace(" TL", "").strip())
                if cp > 0:
                    indirim_orani = ((cp - np) / cp) * 100
                else:
                    indirim_orani = 0
                discount_list.append(indirim_orani)
            except:
                discount_list.append(0)

        average_discount = round(sum(discount_list) / len(discount_list))

        campaigns.append({
            "title": name,
            "reason": reason,
            "duration_days": duration_days,
            "expected_revenue": int(expected_revenue),
            "expected_click_increase": round(total_click_increase / len(campaign_products)),
            "roi": round(total_roi / len(campaign_products), 2),
            "products": campaign_products,
            "daily_revenue": daily_revenue,
            "average_discount": average_discount,
        })

    return campaigns

def generate_user_segments(user_df, product_df):
    if user_df is None:
        return pd.DataFrame()

    merged = user_df.merge(product_df[['ürün_ismi', 'kategori']], left_on="product_id", right_on="ürün_ismi", how="left")
    purchased_users = merged[merged["action"] == "purchase"]["user_id"].unique()
    potential_users = merged[~merged["user_id"].isin(purchased_users)]

    relevant_actions = potential_users[potential_users["action"].isin(["view", "add_to_cart", "exit"])]

    segment_summary = []

    for kategori, grup in relevant_actions.groupby("kategori"):
        if grup.empty:
            continue

        user_ids = grup[grup["action"].isin(["view", "add_to_cart", "exit"])]["user_id"].unique()
        if len(user_ids) < 200:
            continue

        view_count = grup[grup["action"] == "view"].shape[0]
        cart_count = grup[grup["action"] == "add_to_cart"].shape[0]
        exit_count = grup[grup["action"] == "exit"].shape[0]

        total_interaction = view_count + cart_count + exit_count

        segment_summary.append({
            "kategori": kategori,
            "kullanıcı_sayısı": len(user_ids),
            "görüntüleme": view_count,
            "sepete_ekleme": cart_count,
            "çıkış": exit_count,
            "toplam_etkileşim": total_interaction
        })

    return pd.DataFrame(segment_summary)

def gpt_generate_user_campaign(segment_kategori, kullanıcı_sayısı, görüntüleme, sepete_ekleme, çıkış):
    prompt = f"""
The user segment below has interacted with the '{segment_kategori}' category but has not completed a purchase.

Details:
- Number of users: {kullanıcı_sayısı}
- Views: {görüntüleme}
- Add to cart: {sepete_ekleme}
- Exits without action: {çıkış}

Based on this behavior:
1. Analyze how this group behaves and why they might not have converted yet,
2. Propose a tailored campaign strategy for this group,
3. Estimate the potential increase in conversion rate and the revenue impact.

Please write the answer in Turkish with the following structure:
- Kullanıcı Davranış Analizi:
- Kampanya Önerisi:
- Beklenen Etki (Dönüşüm oranı & Ciro artışı):
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model_secimi,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30
    )

    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "GPT yanıtı alınamadı."


# PART 3 – Kampanya Dashboardu
def kampanyalari_getir():
    return generate_campaigns(veri)

if show_dashboard and not show_segment_dashboard:
    kampanyalar = kampanyalari_getir()

    if not kampanyalar:
        st.info("Şu anda anlamlı bir kampanya fırsatı bulunamadı.")
    else:
        kampanya_isimleri = [c["title"] for c in kampanyalar]
        secilen = st.selectbox("Bir kampanya seçin:", kampanya_isimleri)
        kampanya = next(c for c in kampanyalar if c["title"] == secilen)

        st.markdown(f"## 📦 {kampanya['title']}")
        st.write(kampanya['reason'])
        st.write(f"📅 Süre: {kampanya['duration_days']} gün")
        st.write(f"📉 Ortalama indirim: %{kampanya['average_discount']}")
        st.write(f"💰 Beklenen ciro: {kampanya['expected_revenue']} TL")
        st.write(f"📈 Tahmini tıklama artışı: +%{kampanya['expected_click_increase']}")
        st.write(f"🔁 ROI: {kampanya['roi']}x")

        with st.expander(f"📃 Ürün Listesi ({len(kampanya['products'])} ürün)"):
            for p in kampanya["products"]:
                st.write(f"- {p['name']} | {p['current_price']} TL → {p['new_price']} TL")

        kampanyasiz_revenue = []
        for _, row in enumerate(kampanya["products"]):
            try:
                base_price = float(str(row["current_price"]).replace(",", ".").replace(" TL", "").strip())
                base_sales = random.uniform(0.8, 1.2)
                daily_sale = base_price * base_sales
                kampanyasiz_revenue.append(round(daily_sale, 2))
            except:
                kampanyasiz_revenue.append(0)

        kampanyasiz_toplam = [
            round(sum(kampanyasiz_revenue) * (1 + random.uniform(-0.05, 0.05)), 2)
            for _ in range(kampanya["duration_days"])
        ]

 # Kampanyasız tahmini hesapla
        kampanyasiz_revenue = []
        for _, row in enumerate(kampanya["products"]):
            try:
                base_price = float(str(row["current_price"]).replace(",", ".").replace(" TL", "").strip())
                base_sales = random.uniform(0.8, 1.2)
                daily_sale = base_price * base_sales
                kampanyasiz_revenue.append(round(daily_sale, 2))
            except:
                kampanyasiz_revenue.append(0)

        kampanyasiz_toplam = [
            round(sum(kampanyasiz_revenue) * (1 + random.uniform(-0.05, 0.05)), 2)
            for _ in range(kampanya["duration_days"])
        ]

        # Grafik
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=list(range(1, kampanya["duration_days"] + 1)),
            y=kampanya["daily_revenue"],
            mode='lines+markers',
            name='Kampanyalı',
            line=dict(color='green')
        ))

        fig.add_trace(go.Scatter(
            x=list(range(1, kampanya["duration_days"] + 1)),
            y=kampanyasiz_toplam,
            mode='lines+markers',
            name='Kampanyasız',
            line=dict(color='orange', dash='dot')
        ))

        fig.update_layout(
            title="📊 Günlük Ciro Karşılaştırması (Kampanyalı vs. Kampanyasız)",
            xaxis_title="Gün",
            yaxis_title="Ciro (TL)",
            height=400,
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

        kampanyali_toplam = sum(kampanya["daily_revenue"])
        kampanyasiz_toplam_genel = sum(kampanyasiz_toplam)
        fark_tl = kampanyali_toplam - kampanyasiz_toplam_genel
        fark_yuzde = (fark_tl / kampanyasiz_toplam_genel) * 100 if kampanyasiz_toplam_genel else 0

        st.markdown("### 💹 Toplam Ciro Farkı")
        st.write(f"**Fark (TL):** {round(fark_tl)} TL")
        st.write(f"**Fark (%):** %{round(fark_yuzde, 2)}")


elif show_segment_dashboard and not show_dashboard:
    st.markdown("## 👥 Kullanıcı Bazlı Segment Kampanyaları")
    kullanici_verisi = load_user_interactions(uploaded_file)
    segmentler = generate_user_segments(kullanici_verisi, veri)

    if segmentler.empty:
        st.info("Anlamlı kullanıcı segmenti bulunamadı.")
    else:
        for _, row in segmentler.iterrows():
            kategori = row["kategori"]
            kullanıcı_sayısı = row["kullanıcı_sayısı"]
            görüntüleme = row["görüntüleme"]

            if kullanıcı_sayısı >= 200:
                st.subheader(f"🎯 Segment: {kategori} – {kullanıcı_sayısı} kullanıcı")
                st.markdown(
                    f"Bu segmentteki kullanıcılar şu şekilde etkileşimde bulunmuş:\n\n"
                    f"- 👁️ **{görüntüleme}** kez ürün görüntülemiş,\n"
                    f"- 🛒 **{row['sepete_ekleme']}** kez sepete eklemiş,\n"
                    f"- 🚪 **{row['çıkış']}** kez sayfayı terk etmiş.\n\n"
                    f"Ancak hiçbir kullanıcı bu kategoriye ait ürünlerden satın alma gerçekleştirmemiş."
                )


                merged = kullanici_verisi.merge(veri[['ürün_ismi', 'kategori']], left_on="product_id", right_on="ürün_ismi", how="left")
                segment_user_ids = merged[
                    (merged["kategori"] == kategori) &
                    (merged["action"].isin(["view", "add_to_cart", "exit"]))
                ]["user_id"].unique()

                segment_df = kullanici_verisi[kullanici_verisi["user_id"].isin(segment_user_ids)]

                st.download_button(
                    label=f"📥 '{kategori}' Segment Kullanıcılarını İndir",
                    data=segment_df.to_csv(index=False).encode("utf-8"),
                    file_name=f"segment_kullanicilar_{kategori}.csv",
                    mime="text/csv"
                )

            if st.button(f"💡 Kampanya Önerisi Al – {kategori}"):
                    with st.spinner("Kaira düşünüyor..."):
                        sepete_ekleme = row["sepete_ekleme"]
                        çıkış = row["çıkış"]
                        öneri = gpt_generate_user_campaign(kategori, kullanıcı_sayısı, görüntüleme, sepete_ekleme, çıkış)
                        st.success("📌 Kampanya Önerisi ve Açıklaması:")
                        st.markdown(öneri)
