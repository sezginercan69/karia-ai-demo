# --- core/baseline.py ---
from typing import Dict
from .config import HORIZON_DAYS

def _to_float(x) -> float:
    if x is None: return 0.0
    if isinstance(x, (int, float)): return float(x)
    s = str(x).replace("TL","").replace("₺","").replace(",",".").strip()
    try: return float(s)
    except: return 0.0

def estimate_q0(row: Dict) -> float:
    """
    Günlük baz talep (kampanyasız). Şimdilik satış_hızı kolonunu kullanıyoruz.
    Gerekirse burada SARIMAX/Prophet’e geçeriz.
    """
    for c in ("satış_hızı", "satis_hizi", "satishizi"):
        if c in row: return _to_float(row[c])
    return 0.0

def forecast_baseline(row: Dict, horizon_days: int = HORIZON_DAYS) -> Dict:
    """
    Kampanyasız dünyada (mevcut fiyatla) toplam adet ve ciro tahmini.
    """
    q0 = estimate_q0(row)
    p  = _to_float(row.get("mevcut_fiyat", row.get("mevcut fiyat")))
    stock = _to_float(row.get("stok_miktarı", row.get("stok_miktari", 0)))
    units = min(q0 * horizon_days, stock)
    revenue = units * p
    return {"q0": q0, "units": units, "revenue": revenue}
