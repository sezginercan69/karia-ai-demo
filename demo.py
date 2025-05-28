import os
import streamlit as st
import pandas as pd
import requests
import random
import matplotlib.pyplot as plt

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

# Veri yükleme
@st.cache_data
def load_data(file):
    df = pd.read_excel(file, engine="openpyxl")
    df.columns = df.columns.astype(str)
    df = df.dropna(subset=["ürün_ismi"])
    df["ürün_ismi"] = df["ürün_ismi"].astype(str)
    return df

veri = load_data(uploaded_file)

# Sol panel – Ürün ve model seçimi
st.sidebar.header("Ürün Seçimi")
secim = st.sidebar.selectbox("Bir ürün seçin:", veri["ürün_ismi"].unique())
secili_urun = veri[veri["ürün_ismi"] == secim].iloc[0]

st.sidebar.header("Model Seçimi")
model_secimi = st.sidebar.selectbox(
    "Bir model seçin:",
    ["openai/gpt-3.5-turbo", "openai/gpt-4o-mini"]
)

show_dashboard = st.sidebar.checkbox("📊 Kampanya Dashboardu Göster", value=False)

if not show_dashboard:
    # Ürün bilgisi gösterimi
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

    # Prompt
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

    if st.button("💡 Karia’dan Öneri Al"):
        with st.spinner(f"{model_secimi} modeliyle yanıt alınıyor..."):
            headers = {
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model_secimi,
                "messages": [
                    {"role": "system", "content": "Sen bir e-ticaret karar destek yapay zekasısın."},
                    {"role": "user", "content": prompt}
                ]
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            if response.status_code == 200:
                yanit = response.json()
                st.markdown("---")
                st.subheader("📤 Karia'nın Yanıtı")
                st.write(yanit["choices"][0]["message"]["content"])
            else:
                st.error(f"❌ API Hatası: {response.status_code}\n{response.text}")
else:
    st.markdown("---")
    st.subheader("📊 Otomatik Kampanya Simülasyonu")

    def generate_campaigns(df):
        campaigns = []
        duration_days = 5

        # Farklı kurallara göre kampanyalar oluştur
        conditions = [
            (df["stok_miktarı"] > 100) & (df["satış_hızı"] < 1),
            (df["tıklama_satış_oranı"] < 0.05) & (df["kategori_dönüşüm_oranı"] > 0.1),
            (df["ürün_yaşı"] > 90) & (df["stok_miktarı"] > 50)
        ]
        names = ["Stok Temelli Kampanya", "Düşük Dönüşüm Odaklı", "Yaşlı Ürünleri Hızlandır"]
        reasons = [
            "Stok fazlası olup satışı yavaş olan ürünleri eritmek için oluşturuldu.",
            "Tıklama oranı yüksek ama dönüşüm düşük ürünleri harekete geçirmek için önerildi.",
            "Uzun süredir satılmayan ürünlerin stok maliyetini azaltmak hedeflenmiştir."
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
            daily_revenue = []

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

            # Ortalama indirim yüzdesini doğru şekilde hesapla
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

    kampanyalar = generate_campaigns(veri)

    if not kampanyalar:
        st.info("Şu anda anlamlı bir kampanya fırsatı bulunamadı.")
    else:
        kampanya_isimleri = [c["title"] for c in kampanyalar]
        secilen = st.selectbox("Bir kampanya seçin:", kampanya_isimleri)
        kampanya = next(c for c in kampanyalar if c["title"] == secilen)

        st.markdown(f"**📦 {kampanya['title']}**")
        st.write(kampanya['reason'])
        st.write(f"📅 Süre: {kampanya['duration_days']} gün")
        st.write(f"📉 Ortalama indirim: %{kampanya['average_discount']}")
        st.write(f"💰 Beklenen ciro: {kampanya['expected_revenue']} TL")
        st.write(f"📈 Tahmini tıklama artışı: +%{kampanya['expected_click_increase']}")
        st.write(f"🔁 ROI: {kampanya['roi']}x")

        with st.expander(f"📃 Ürün Listesi ({len(kampanya['products'])} ürün)"):
            for p in kampanya["products"]:
                st.write(f"- {p['name']} | {p['current_price']} TL → {p['new_price']} TL")

        st.markdown("---")
        import plotly.graph_objects as go

        st.subheader("📊 Günlük Ciro Tahmini")

# Kampanyasız tahmini hesapla
kampanyasiz_revenue = []
for _, row in enumerate(kampanya["products"]):
    try:
        base_price = float(str(row["current_price"]).replace(",", ".").replace(" TL", "").strip())
        base_sales = random.uniform(0.8, 1.2)  # varsayılan satış hızı x çarpanı
        daily_sale = base_price * base_sales
        kampanyasiz_revenue.append(round(daily_sale, 2))
    except:
        kampanyasiz_revenue.append(0)

kampanyasiz_toplam = [round(sum(kampanyasiz_revenue) * (1 + random.uniform(-0.05, 0.05)), 2) for _ in range(kampanya["duration_days"])]
# Yeni birleşik grafik
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
# Ciro farkı hesaplama ve gösterme
kampanyali_toplam = sum(kampanya["daily_revenue"])
kampanyasiz_toplam_genel = sum(kampanyasiz_toplam)
fark_tl = kampanyali_toplam - kampanyasiz_toplam_genel
fark_yuzde = (fark_tl / kampanyasiz_toplam_genel) * 100 if kampanyasiz_toplam_genel else 0

st.markdown("### 💹 Toplam Ciro Farkı")
st.write(f"**Fark (TL):** {round(fark_tl)} TL")
st.write(f"**Fark (%):** %{round(fark_yuzde, 2)}")

