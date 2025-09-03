USE_LGBM    = True    # LightGBM'den ürün-beta kullan (öğrenilmiş beta varsa)
USE_CAUSAL  = True    # CausalImpact uplift ile q0'ı kampanyasız hale düzelt
USE_ORTOOLS = False   # Kampanya seçimi (şimdilik kapalı)
# --- core/config.py ---
HORIZON_DAYS = 5                 # simülasyon ufku (gün)
MIN_MARGIN = 0.10                # güvenli taban (guard): fiyat >= maliyet * (1 + 0.10)

# İndirim ve fiyat artışı adayları (deterministik grid)
DISCOUNT_GRID = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
PRICE_UP_MULTS = [1.00, 1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.40, 1.50]

# Kategori varsayılan elastikiyetleri (beta < 0)
ELASTICITY_BY_CAT = {
    "tişört": -1.8, "tisort": -1.8, "t-shirt": -1.8,
    "jean": -1.6, "pantolon": -1.6,
    "sneaker": -1.2, "ayakkabı": -1.2, "ayakkabi": -1.2,
    "aksesuar": -1.5,
    "_default": -1.5,
}

EPS_PROFIT = 50.0  # kârlar yakınsa: ciro → adet → fiyat stabilitesi ile kır
