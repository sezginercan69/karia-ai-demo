# --- core/router.py ---
from typing import Dict
from .config import HORIZON_DAYS, MIN_MARGIN
from .baseline import forecast_baseline
from .elasticity import pick_beta
from .optimizer import choose_price

def run_for_product(row: Dict) -> Dict:
    """
    Tek ürün için tam karar.
    UI kartı bu çıktıyı gösterir; sayılar deterministik.
    """
    base = forecast_baseline(row, horizon_days=HORIZON_DAYS)
    beta = pick_beta(row)
    best, _ = choose_price(row, q0=base["q0"], beta=beta)

    p = float(str(row.get("mevcut_fiyat", row.get("mevcut fiyat"))).replace(",",".") or 0)
    c = float(str(row.get("ürün_maliyeti", row.get("urun_maliyeti"))).replace(",",".") or 0)
    guard_min = round(c * (1 + MIN_MARGIN), 2)

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
    }
