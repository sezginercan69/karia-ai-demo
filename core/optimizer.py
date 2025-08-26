# --- core/optimizer.py ---
from typing import Dict, List, Tuple
from .config import HORIZON_DAYS, MIN_MARGIN, DISCOUNT_GRID, PRICE_UP_MULTS

def _to_float(x) -> float:
    try:
        s = str(x).replace("TL", "").replace("₺", "").replace(",", ".").strip()
        return float(s)
    except Exception:
        return 0.0

def _guard_min_price(cost: float) -> float:
    if cost <= 0:
        return 0.0
    return cost * (1.0 + MIN_MARGIN)  # markup politikası (config’te %10 yaptınız)

def _score_candidate(row: Dict, q0: float, p_now: float, p_new: float, beta: float) -> Dict:
    """
    Aday fiyat için 5 günlük adet/ciro/kâr ve inkremental kâr hesaplar.
    """
    c = _to_float(row.get("ürün_maliyeti", row.get("urun_maliyeti")))
    # Talep tepkisi: (p_new / p_now)^beta  (p_now=0 ise bölünmeyi engelle)
    denom = p_now if p_now > 0 else 1e-6
    demand_factor = (p_new / denom) ** beta if p_new > 0 else 0.0

    units_per_day = max(q0 * demand_factor, 0.0)
    units_5g = units_per_day * HORIZON_DAYS

    revenue = p_new * units_5g
    profit = (p_new - c) * units_5g

    # Baz (mevcut fiyat) 5g kârı
    base_units_5g = (q0 * HORIZON_DAYS)
    base_profit_5g = (p_now - c) * base_units_5g

    inc_profit = profit - base_profit_5g

    return {
        "p_new": round(p_new, 2),
        "units": units_5g,
        "revenue": revenue,
        "profit": profit,
        "inc_profit": inc_profit,
    }

def _pick_best(cands: List[Dict], p_now: float) -> Dict:
    """
    Seçim önceliği: kâr → ciro → adet → fiyata yakınlık (mevcut fiyata daha yakın olan).
    """
    if not cands:
        # Emniyetli dönüş (asla boş dönmeyelim)
        return {
            "p_new": round(p_now, 2),
            "units": 0.0,
            "revenue": 0.0,
            "profit": 0.0,
            "inc_profit": 0.0,
            "mode": "fallback",
            "discount_pct": 0.0,
            "roi": None,
        }

    cands_sorted = sorted(
        cands,
        key=lambda x: (x["profit"], x["revenue"], x["units"], -abs(x["p_new"] - p_now)),
        reverse=True,
    )
    return cands_sorted[0]

def choose_price(row: Dict, q0: float, beta: float) -> Tuple[Dict, List[Dict]]:
    """
    Ana seçim fonksiyonu: indirim / fiyat artışı adaylarını üretir, en iyisini seçer.
    """
    p = _to_float(row.get("mevcut_fiyat", row.get("mevcut fiyat")))
    c = _to_float(row.get("ürün_maliyeti", row.get("urun_maliyeti")))
    guard_min = round(_guard_min_price(c), 2)

    candidates: List[Dict] = []

    # --- FİYAT ARTIŞI MODU ---
    if p < guard_min:
        for m in PRICE_UP_MULTS:
            p_new = round(p * m, 2)
            if p_new < guard_min:
                continue
            sc = _score_candidate(row, q0, p_now=p, p_new=p_new, beta=beta)
            sc.update({"mode": "price_up", "discount_pct": 0.0, "roi": None})
            candidates.append(sc)

        # Grid guard'a yetişmeyebilir; guard'ı zorunlu aday ekle
        if not any(abs(x["p_new"] - guard_min) < 1e-9 for x in candidates) and guard_min > 0:
            sc = _score_candidate(row, q0, p_now=p, p_new=guard_min, beta=beta)
            sc.update({"mode": "price_up", "discount_pct": 0.0, "roi": None})
            candidates.append(sc)

    # --- İNDİRİM MODU ---
    else:
        for d in DISCOUNT_GRID:
            p_new = round(p * (1.0 - d), 2)
            if p_new < guard_min:
                continue
            sc = _score_candidate(row, q0, p_now=p, p_new=p_new, beta=beta)
            units = sc["units"]
            disc_cost = max(p - p_new, 0.0) * units  # indirim maliyeti ~ birim indirim × adet
            roi = (sc["inc_profit"] / disc_cost) if disc_cost > 0 else None
            sc.update({"mode": "discount", "discount_pct": round(d * 100, 1), "roi": roi})
            candidates.append(sc)

        # Mevcut fiyatı (hold) HER ZAMAN aday yap → negatif inkremental kâr önerilmez
        sc_hold = _score_candidate(row, q0, p_now=p, p_new=p, beta=beta)
        sc_hold.update({"mode": "hold", "discount_pct": 0.0, "roi": None})
        candidates.append(sc_hold)

    # --- Fallback: yine de aday yoksa en az guard veya mevcut fiyatı kullan ---
    if not candidates:
        p_new = guard_min if (guard_min > 0 and p < guard_min) else (p if p > 0 else guard_min)
        p_new = round(p_new, 2)
        sc = _score_candidate(row, q0, p_now=p, p_new=p_new, beta=beta)
        sc.update({"mode": "fallback", "discount_pct": 0.0, "roi": None})
        candidates.append(sc)

    best = _pick_best(candidates, p_now=p)
    return best, candidates
