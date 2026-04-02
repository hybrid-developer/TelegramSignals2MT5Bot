# ai_filter.py
import config


def score_signal(signal):
    entry = signal.get("entry")
    sl = signal.get("sl")
    tps = signal.get("tps", [])

    if entry is None:
        return 0.0

    if config.AI_REQUIRE_SL and not sl:
        return 0.0

    if config.AI_REQUIRE_TP and not tps:
        return 0.0

    if not sl or not tps:
        return 0.0

    risk = abs(entry - sl)
    if risk == 0:
        return 0.0

    rewards = [abs(tp - entry) for tp in tps if tp is not None]
    if not rewards:
        return 0.0

    rr = min(rewards) / risk
    score = rr / config.AI_SCORE_DIVISOR

    if len(tps) > 1:
        score += config.AI_BONUS_MULTIPLE_TPS

    return min(score, 1.0)


def is_a_plus(signal):
    if not config.AI_FILTER_ENABLED:
        return True

    score = score_signal(signal)
    print(f"AI score: {score:.2f} | min required: {config.AI_MIN_SCORE:.2f}")
    return score >= config.AI_MIN_SCORE
