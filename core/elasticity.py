# --- core/elasticity.py ---
from typing import Dict
from .config import ELASTICITY_BY_CAT, HORIZON_DAYS

def pick_beta(row: Dict) -> float:
    cat = str(row.get("kategori", "")).lower()
    for k, v in ELASTICITY_BY_CAT.items():
        if k != "_default" and k in cat:
            return v
    return ELASTICITY_BY_CAT["_default"]

def demand_with_price_change(q0: float, p_old: float, p_new: float, beta: float, days: int = HORIZON_DAYS) -> float:
    """
    Log–log elastikiyet: q' = q0 * (p'/p)^beta, total = q' * days
    """
    if p_old <= 0 or p_new <= 0: 
        return 0.0
    factor = (p_new / p_old) ** beta
    return q0 * factor * days
