# news.py
# News filter is disabled via config. Never blocks trading.

def high_impact_news_soon(symbol=None, minutes_ahead=30):
    """
    News filter is disabled. Always returns False (safe to trade).
    """
    import config
    if not getattr(config, "NEWS_FILTER_ENABLED", False):
        return False

    import requests
    from datetime import datetime, timedelta
    import pytz

    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        now = datetime.now(pytz.UTC)
        for event in data:
            if (event.get('impact') == 'High' and
                symbol in event.get('title', '') and
                now <= datetime.fromisoformat(
                    event['date'].replace('Z', '+00:00')
                ) <= now + timedelta(minutes=minutes_ahead)):
                return True
        return False
    except:
        return False