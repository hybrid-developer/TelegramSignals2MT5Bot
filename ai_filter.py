# ai_filter.py
def score_signal(signal):
    entry=signal["entry"]
    sl=signal["sl"]
    tps=signal["tps"]
    if not sl or not tps: return 0
    rr=min([abs(tp-entry) for tp in tps])/abs(entry-sl)
    score=rr/2
    if len(tps)>1: score+=0.1
    return min(score,1.0)

def is_a_plus(signal):
    return score_signal(signal)>=0.7