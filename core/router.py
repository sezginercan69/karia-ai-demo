# --- core/router.py ---
from typing import Dict, List
from .config import HORIZON_DAYS, MIN_MARGIN, EPS_PROFIT
from .baseline import forecast_baseline
from .elasticity import pick_beta
from .optimizer import choose_price

def _to_float(x) -> float:
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return 0.0

def _explain_decision(row: Dict, base: Dict, best: Dict, candidates: List[Dict], guard_min: float, beta: float) -> str:
    """
    Deterministik açıklama: neden bu MOD ve neden bu FİYAT?
    LLM kullanılmaz; tamamen sayılara dayanır.
    """
    p = _to_float(row.get("mevcut_fiyat", row.get("mevcut fiyat")))
    c = _to_float(row.get("ürün_maliyeti", row.get("urun_maliyeti")))
    q0 = base["q0"]
    base_units = base["units"]
    base_profit = base_units * max(p - c, 0)

    # Optimizer ile aynı öncelik: kâr → ciro → adet → fiyata yakınlık
    cands_sorted = sorted(
        candidates,
        key=lambda x: (x["profit"], x["revenue"], x["units"], -abs(x["p_new"] - p)),
        reverse=True,
    )
    second = cands_sorted[1] if len(cands_sorted) > 1 else None

    # --- MOD gerekçesi ---
    if p < guard_min and best["mode"] != "discount":
        mod_reason = (
            f"Mevcut fiyat ({p:.2f} TL), güvenli tabanın ({guard_min:.2f} TL) altında. "
            f"Zararı önlemek için **Fiyat Artışı** modu seçildi."
        )
    elif best["mode"] == "hold":
        mod_reason = (
            "İndirim senaryoları mevcut fiyata göre kârı artırmadığı için "
            "**Fiyatı Koru** seçildi."
        )
    else:
        mod_reason = (
            f"Mevcut fiyat güvenli tabanın üzerinde ({p:.2f} ≥ {guard_min:.2f}). "
            f"İndirim adayları değerlendirildi ve beklenen kârı en çok artıran seçenek seçildi."
        )

    # --- Fiyat gerekçesi ---
    p_new = best["p_new"]
    profit = best["profit"]
    inc_profit = best["inc_profit"]
    revenue = best["revenue"]
    demand_factor = (p_new / p) ** beta if p > 0 and p_new > 0 else 1.0

    tie_reason = ""
    if second:
        dp = profit - second["profit"]
        if abs(dp) <= EPS_PROFIT:
            if best["revenue"] > second["revenue"] + 1e-6:
                tie_reason = "Kârlar yaklaşık eşit olduğundan **ciro** daha yüksek olan tercih edildi."
            elif abs(best["revenue"] - second["revenue"]) <= 1e-6 and best["units"] > second["units"] + 1e-6:
                tie_reason = "Kâr ve ciro yaklaşık eşit olduğundan **adet** daha yüksek olan tercih edildi."
            else:
                tie_reason = "Kâr, ciro ve adet çok yakın olduğundan **mevcut fiyata en yakın** seçenek tercih edildi."
        else:
            tie_reason = "Bu fiyat, diğer adaylara göre **en yüksek beklenen kârı** sağlıyor."

    guard_note = ""
    if abs(p_new - guard_min) < 1e-6:
        guard_note = "Seçilen fiyat güvenli tabana eşittir; zarar riski olmaması için kısıt bağlayıcıdır."

    if best["mode"] == "discount":
        price_reason = (
            f"Önerilen indirim **%{best['discount_pct']}** ile yeni fiyat **{p_new:.2f} TL**. "
            f"Fiyat değişimi {beta:+.2f} elastikiyetle talebi ≈ **{demand_factor:.2f}×** etkiler; "
            f"5 günde beklenen adet **{best['units']:.2f}**, kâr **{profit:.2f} TL**. "
            f"Baz kâra göre inkremental kâr **{inc_profit:.2f} TL**. {tie_reason}"
        )
        if best.get("roi") is not None:
            price_reason += f" İndirim ROI’si ≈ **{best['roi']:.3f}**."
    elif best["mode"] == "price_up":
        price_reason = (
            f"Yeni fiyat **{p_new:.2f} TL** (guard ≥ {guard_min:.2f}). "
            f"Fiyat artışı talebi {beta:+.2f} elastikiyetle baskılar (≈{demand_factor:.2f}×); "
            f"ancak birim kâr arttığı için toplam kâr **{profit:.2f} TL**’ye çıkar. "
            f"{tie_reason} {guard_note}"
        )
    else:  # hold
        price_reason = (
            f"Mevcut fiyat **{p:.2f} TL** korunuyor; alternatif indirimlerde beklenen kâr, mevcut duruma göre artmıyor. "
            f"5 gün kârı ≈ **{base_profit:.2f} TL**. {tie_reason}"
        )

    bullets = [
        f"**Mod gerekçesi:** {mod_reason}",
        f"**Fiyat gerekçesi:** {price_reason}",
    ]
    if guard_note and best["mode"] != "price_up":
        bullets.append(f"**Not:** {guard_note}")
    return "\n\n".join(f"- {b}" for b in bullets)

def run_for_product(row: Dict) -> Dict:
    """
    Tek ürün için karar + deterministik açıklama metni.
    """
    base = forecast_baseline(row, horizon_days=HORIZON_DAYS)
    beta = pick_beta(row)
    best, candidates = choose_price(row, q0=base["q0"], beta=beta)

    p = _to_float(row.get("mevcut_fiyat", row.get("mevcut fiyat")))
    c = _to_float(row.get("ürün_maliyeti", row.get("urun_maliyeti")))
    guard_min = round(c * (1 + MIN_MARGIN), 2)  # şu an config’te markup %10 politikası

    explanation = _explain_decision(row, base, best, candidates, guard_min, beta)

    return {
        "mode": best["mode"],
        "recommended_price": round(best["p_new"], 2),
        "discount_pct": best.get("discount_pct", 0.0),
        "expected_units_5g": round(best["units"], 2),
        "expected_revenue_5g": round(best["revenue"], 2),
        "expected_profit_5g": round(best["profit"], 2),
        "expected_inc_profit_5g": round(best["inc_profit"], 2),
        "roi": None if best.get("roi") is None else round(best["roi"], 3),
        "guard_min_price": guard_min,
        "beta": beta,
        "q0_per_day": round(base["q0"], 3),
        "explanation": explanation,   # deterministik açıklama
    }
