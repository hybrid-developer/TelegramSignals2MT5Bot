# parser.py
import re
from typing import Dict, Any, Optional
from config import SYMBOL_MAP

class SignalParser:
    def __init__(self, default_symbol: str = "XAUUSD"):
        self.default_symbol = default_symbol

    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        full_text = " ".join(lines)
        full_lower = full_text.lower()

        is_update = "next msg" in full_lower or full_lower.startswith("tp")

        action = "BUY" if "buy" in full_lower else "SELL" if "sell" in full_lower else None
        if not action and not is_update:
            return None

        order_type = "LIMIT" if "limit" in full_lower else "STOP" if "stop" in full_lower else "MARKET"

        tokens = full_text.split()
        symbol = None
        for tok in tokens:
            t = tok.upper()
            if t in SYMBOL_MAP:
                symbol = SYMBOL_MAP[t]
                break
            if re.match(r"^[A-Z]{3,6}\d*$", t):
                symbol = t
                break
        symbol = symbol or self.default_symbol

        # Entry price
        m_at = re.search(r"@\s*([0-9]+(?:\.[0-9]+)?)", full_text)
        if m_at:
            entry_price = float(m_at.group(1))
        else:
            m_range = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*-\s*([0-9]+(?:\.[0-9]+)?)", full_text)
            if m_range:
                entry_price = (float(m_range.group(1)) + float(m_range.group(2))) / 2
            else:
                prices = re.findall(r"\b\d+(?:\.\d+)?\b", full_text)
                entry_price = float(prices[0]) if prices else None

        # SL
        m_sl = re.search(r"\bsl[:\s]*([0-9]+(?:\.[0-9]+)?)", full_lower)
        sl = float(m_sl.group(1)) if m_sl else None

        # TPs
        tps = []
        for m in re.finditer(r"\btp\d*[:\s]*([0-9]+(?:\.[0-9]+)?)", full_lower):
            tps.append(float(m.group(1)))
        tps.sort() if action=="BUY" else tps.sort(reverse=True)

        return {
            "is_update": is_update,
            "action": action,
            "order_type": order_type,
            "symbol": symbol,
            "entry": entry_price,
            "sl": sl,
            "tps": tps,
            "raw": text
        }