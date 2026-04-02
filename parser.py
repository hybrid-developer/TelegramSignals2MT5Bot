import re
from typing import Dict, Any, Optional, List
from config import SYMBOL_MAP

IGNORE_TOKENS = {
    "BUY", "SELL", "LIMIT", "STOP", "MARKET",
    "SL", "TP", "TP1", "TP2", "TP3", "TP4", "TP5",
    "AREA", "ENTRY"
}


class SignalParser:
    def __init__(self, default_symbol: str = "XAUUSD", open_tp_offset: float = 50.0):
        self.default_symbol = default_symbol
        self.open_tp_offset = open_tp_offset

    def normalize_symbol(self, token: str) -> Optional[str]:
        if not token:
            return None

        t = token.upper().strip()

        if t in IGNORE_TOKENS:
            return None

        if t in SYMBOL_MAP:
            return SYMBOL_MAP[t]

        if t == "GOLD":
            return "XAUUSD"

        if re.fullmatch(r"[A-Z]{6}", t):
            return t

        return None

    def _extract_symbol(self, text: str) -> str:
        tokens = re.findall(r"[A-Za-z]{3,10}", text)
        for tok in tokens:
            symbol = self.normalize_symbol(tok)
            if symbol:
                return symbol
        return self.default_symbol

    def _extract_entry(self, lines: List[str], full_text: str) -> tuple[Optional[float], Optional[float], Optional[float]]:
        entry_min = None
        entry_max = None
        entry_price = None

        m_at = re.search(r"@\s*([0-9]+(?:\.[0-9]+)?)", full_text, re.IGNORECASE)
        if m_at:
            entry_price = float(m_at.group(1))
            return entry_price, None, None

        m_range = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*-\s*([0-9]+(?:\.[0-9]+)?)", full_text)
        if m_range:
            entry_min = float(m_range.group(1))
            entry_max = float(m_range.group(2))
            entry_price = (entry_min + entry_max) / 2
            return entry_price, entry_min, entry_max

        first_line = lines[0] if lines else full_text
        nums = re.findall(r"\b\d+(?:\.\d+)?\b", first_line)
        if nums:
            entry_price = float(nums[0])

        return entry_price, None, None

    def _extract_sl(self, text: str) -> Optional[float]:
        m_sl = re.search(r"\bsl\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
        return float(m_sl.group(1)) if m_sl else None

    def _parse_tp_value(self, raw_value: str) -> Optional[float]:
        if not raw_value:
            return None

        value = raw_value.strip().lower()

        if value in {"open", "open tp", "runner", "running", "hold", "leave open"}:
            return None

        m = re.search(r"([0-9]+(?:\.[0-9]+)?)", value)
        return float(m.group(1)) if m else None

    def _extract_tps(self, lines: List[str], action: str) -> List[float]:
        tp_map: Dict[int, Optional[float]] = {}

        for line in lines:
            m_tp = re.match(r"^\s*tp(\d+)\s*[:\-]\s*(.+?)\s*$", line, re.IGNORECASE)
            if m_tp:
                tp_index = int(m_tp.group(1))
                tp_value_raw = m_tp.group(2)
                tp_map[tp_index] = self._parse_tp_value(tp_value_raw)

        if not tp_map:
            return []

        ordered_indices = sorted(tp_map.keys())
        ordered_tps = [tp_map[i] for i in ordered_indices]

        filled_tps: List[Optional[float]] = []
        prev_tp: Optional[float] = None

        for tp in ordered_tps:
            if tp is None:
                if prev_tp is None:
                    filled_tps.append(None)
                else:
                    if action == "SELL":
                        derived_tp = prev_tp - self.open_tp_offset
                    else:
                        derived_tp = prev_tp + self.open_tp_offset
                    filled_tps.append(float(derived_tp))
                    prev_tp = float(derived_tp)
            else:
                filled_tps.append(float(tp))
                prev_tp = float(tp)

        final_tps = [tp for tp in filled_tps if tp is not None]

        if action == "BUY":
            final_tps.sort()
        elif action == "SELL":
            final_tps.sort(reverse=True)

        return final_tps

    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None

        lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
        full_text = " ".join(lines)
        full_lower = full_text.lower()

        is_update = "next msg" in full_lower or full_lower.startswith("tp")

        action = "BUY" if "buy" in full_lower else "SELL" if "sell" in full_lower else None
        if not action and not is_update:
            return None

        order_type = "LIMIT" if "limit" in full_lower else "STOP" if "stop" in full_lower else "MARKET"

        symbol = self._extract_symbol(full_text)

        entry_price, entry_min, entry_max = self._extract_entry(lines, full_text)
        sl = self._extract_sl(full_text)
        tps = self._extract_tps(lines, action) if action else []

        return {
            "is_update": is_update,
            "action": action,
            "order_type": order_type,
            "symbol": symbol,
            "entry": entry_price,
            "entry_min": entry_min,
            "entry_max": entry_max,
            "sl": sl,
            "tps": tps,
            "raw": text
        }
