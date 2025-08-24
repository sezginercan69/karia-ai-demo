# --- core/optimizer.py ---
from typing import Dict, List, Tuple
from .config import MIN_MARGIN, DISCOUNT_GRID, PRICE_UP_MULTS, EPS_PROFIT, HORIZON_DAYS
from .elasticity import demand_with_price_change

def _to_float(x) -> float:
    if x is None: return 0.0
    if isinstance(x, (int, float)): return float(x)
    s = str(x).replace("TL","").replace("₺","").replace(",",".").strip()
    try: return float(s)
    except: return 0.0

def _guard_price(cost: float, p_new: float) -> bool:
    return p_new >= cost * (1.0 + MIN_MARGIN)

def _score_candidate(row: Dict, q0: float, p_new: float, beta: float) -> Dict:
    p = _to_float(row.get("mevcut_fiyat", row.get("mevcut fiyat")))
    c = _to_float(row.get("ürün_maliyeti", row.get("urun_maliyeti")))
    stock = _to_float(row.get("stok_miktarı", row.get("stok_miktari", 0)))

    units = min(demand_with_price_change(q0, p, p_new, beta, HORIZON_DAYS), stock)
    profit = units * (p_new - c)

    base_units = min(q0 * HORIZON_DAYS, stock)
    base_profit = base_units * (p - c)
    inc_profit = profit - base_profit

    revenue = units * p_new
    return {"units": units, "profit": profit, "inc_profit": inc_profit, "revenue": revenue}

def _pick_best(cands: List[Dict], p_now: float) -> Dict:
    """
    1) En yüksek kâr
    2) Kâr ~eşitse (EPS_PROFIT) → en yüksek ciro
    3) Hâlâ eşitse → en çok adet
    4) Hâlâ eşitse → mevcut fiyata en yakın (stabilite)
    """
    cands = sorted(cands, key=lambda x: (x["profit"], x["revenue"], x["units"], -abs(x["p_new"]-p_now)), reverse=True)
    if len(cands) <= 1:
        return cands[0]
    top = cands[0]
    for cand in cands[1:]:
        if abs(top["profit"] - cand["profit"]) <= EPS_PROFIT:
            if cand["revenue"] > top["revenue"] + 1e-6:
                top = cand
            elif abs(cand["revenue"] - top["revenue"]) <= 1e-6 and cand["units"] > top["units"] + 1e-6:
                top = cand
            elif abs(cand["revenue"] - top["revenue"]) <= 1e-6 and abs(cand["units"] - top["units"]) <= 1e-6 and abs(cand["p_new"]-p_now) < abs(top["p_new"]-p_now):
                top = cand
    return top

def choose_price(row: Dict, q0: float, beta: float) -> Tuple[Dict, List[Dict]]:
    """
    Tek ürün için tek karar (deterministik).
    Mevcut fiyat güvenli tabanın altındaysa 'fiyat artışı modu'; değilse 'indirim modu'.
    """
    p = _to_float(row.get("mevcut_fiyat", row.get("mevcut fiyat")))
    c = _to_float(row.get("ürün_maliyeti", row.get("urun_maliyeti")))

    candidates: List[Dict] = []

    # Fiyat artışı modu (zarar/çok düşük marj)
    if p < c * (1 + MIN_MARGIN):
        for m in PRICE_UP_MULTS:
            p_new = round(p * m, 2)
            if not _guard_price(c, p_new):
                continue
            sc = _score_candidate(row, q0, p_new, beta)
            sc.update({"p_new": p_new, "mode": "price_up", "discount_pct": 0.0, "roi": None})
            candidates.append(sc)
    else:
        # İndirim modu
        for d in DISCOUNT_GRID:
            p_new = round(p * (1 - d), 2)
            if not _guard_price(c, p_new):
                continue
            sc = _score_candidate(row, q0, p_new, beta)
            # ROI: sadece indirimde hesaplıyoruz
            units = sc["units"]
            disc_cost = max(p - p_new, 0.0) * units
            roi = (sc["inc_profit"] / disc_cost) if disc_cost > 0 else None
            sc.update({"p_new": p_new, "mode": "discount", "discount_pct": round(d*100, 1), "roi": roi})
            candidates.append(sc)

        # Hiç aday kalmadıysa, mevcut fiyatı koru
        if not candidates:
            sc = _score_candidate(row, q0, p, beta)
            sc.update({"p_new": round(p,2), "mode": "hold", "discount_pct": 0.0, "roi": None})
            candidates.append(sc)

    best = _pick_best(candidates, p_now=p)
    return best, candidates
