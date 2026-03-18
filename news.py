# news.py - High impact news filter for trading bot
import requests
from datetime import datetime, timedelta
import pytz  # pip install pytz if needed

def high_impact_news_soon(symbol=None, minutes_ahead=30):
    """
    Check if high-impact news for symbol is within next X minutes.
    Returns True if news soon (avoid trading), False otherwise.
    """
    # Forex Factory RSS (or use economic calendar API)
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        now = datetime.now(pytz.UTC)
        
        for event in data:
            if (event.get('impact') == 'High' and
                symbol in event.get('title', '') and
                now <= datetime.fromisoformat(event['date'].replace('Z', '+00:00')) <= now + timedelta(minutes=minutes_ahead)):
                return True
        return False
    except:
        return False  # Safe default: assume no news if API fails
