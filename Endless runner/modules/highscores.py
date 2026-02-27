# highscores.py
import json
from datetime import datetime, date

DEFAULT_FILE = "highscore.json"
TOPN_DAILY = 30
TOPN_MONTHLY = 5
TOPN_YEARLY = 5
TOPN_ALLTIME = 5

def _empty_store():
    return {"history": [], "daily": {}, "monthly": {}, "yearly": {}, "alltime": []}

def _asc_insert_cap(lst, entry, key="score", cap=5):
    lst.append(entry)
    i = len(lst) - 1
    while i > 0 and lst[i][key] < lst[i - 1][key]:
        lst[i], lst[i - 1] = lst[i - 1], lst[i]
        i -= 1
    if len(lst) > cap:
        extras = len(lst) - cap
        kept = i >= extras
        del lst[:extras]
        i = (i - extras) if kept else None
    return i

def load_store(file=DEFAULT_FILE):
    try:
        with open(file, "r") as f:
            data = json.load(f)
    except Exception:
        return _empty_store()

    # Migrate old single-value format: {"high_score": X}
    if isinstance(data, dict) and "high_score" in data:
        entry = {
            "name": "Unknown",
            "score": float(data["high_score"]),
            "date": date.today().isoformat(),
            "energy_kj": float(data["high_score"]),
            "duration_sec": 0,
            "avg_power_w": None,
            "avg_speed": None,
        }
        store = _empty_store()
        add_score(store, entry, persist=False)
        return store

    # Migrate old flat list format: [ {name, score, date}, ... ]
    if isinstance(data, list):
        store = _empty_store()
        for e in data:
            norm = {
                "name": e.get("name", "Unknown"),
                "score": float(e.get("score", 0.0)),
                "date": e.get("date", date.today().isoformat()),
                "energy_kj": float(e.get("energy_kj", e.get("score", 0.0))),
                "duration_sec": int(e.get("duration_sec", 0)),
                "avg_power_w": e.get("avg_power_w", None),
                "avg_speed": e.get("avg_speed", None),
            }
            add_score(store, norm, persist=False)
        return store

    # Structured store → normalize by rebuilding buckets from history
    if isinstance(data, dict):
        store = _empty_store()
        for e in data.get("history", []):
            norm = {
                "name": e.get("name", "Unknown"),
                "score": float(e.get("score", 0.0)),
                "date": e.get("date", date.today().isoformat()),
                "energy_kj": float(e.get("energy_kj", e.get("score", 0.0))),
                "duration_sec": int(e.get("duration_sec", 0)),
                "avg_power_w": e.get("avg_power_w", None),
                "avg_speed": e.get("avg_speed", None),
            }
            add_score(store, norm, persist=False)
        return store

    return _empty_store()

def save_store(store, file=DEFAULT_FILE):
    try:
        with open(file, "w") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _bucket_keys(datestr):
    return datestr, datestr[:7], datestr[:4]  # day, month, year

def add_score(store, entry, persist=True, file=DEFAULT_FILE):
    store, _ = add_score_with_ranks(store, entry, persist=persist, file=file)
    return store

def add_score_with_ranks(store, entry, persist=True, file=DEFAULT_FILE):
    e = {
        "name": entry.get("name", "Unknown"),
        "score": float(entry.get("score", 0.0)),
        "date": entry.get("date", date.today().isoformat()),
        "energy_kj": float(entry.get("energy_kj", entry.get("score", 0.0))),
        "duration_sec": int(entry.get("duration_sec", 0)),
        "avg_power_w": entry.get("avg_power_w", None),
        "avg_speed": entry.get("avg_speed", None),
    }

    store["history"].append(e)

    day_key, month_key, year_key = _bucket_keys(e["date"])

    daily = store["daily"].setdefault(day_key, [])
    di = _asc_insert_cap(daily, e, key="score", cap=TOPN_DAILY)

    monthly = store["monthly"].setdefault(month_key, [])
    mi = _asc_insert_cap(monthly, e, key="score", cap=TOPN_MONTHLY)

    yearly = store["yearly"].setdefault(year_key, [])
    yi = _asc_insert_cap(yearly, e, key="score", cap=TOPN_YEARLY)

    alltime = store.setdefault("alltime", [])
    ai = _asc_insert_cap(alltime, e, key="score", cap=TOPN_ALLTIME)

    if persist:
        save_store(store, file=file)

    def idx_to_rank(idx, bucket):
        return None if idx is None else (len(bucket) - idx)  # 1 = best

    ranks = {
        "daily_rank": idx_to_rank(di, daily),
        "monthly_rank": idx_to_rank(mi, monthly),
        "yearly_rank": idx_to_rank(yi, yearly),
        "alltime_rank": idx_to_rank(ai, alltime),
    }
    return store, ranks

def today_key(now=None):
    now = now or datetime.now()
    return now.date().isoformat()

def month_key(now=None):
    now = now or datetime.now()
    return now.strftime("%Y-%m")

def year_key(now=None):
    now = now or datetime.now()
    return now.strftime("%Y")

def _top_from_bucket(bucket, n=5, highest_first=True):
    tail = bucket[-min(n, len(bucket)):]
    return list(reversed(tail)) if highest_first else tail

def top_today(store, n=5, highest_first=True, now=None):
    bucket = store["daily"].get(today_key(now), [])
    return _top_from_bucket(bucket, n=n, highest_first=highest_first)

def top_month(store, n=5, highest_first=True, now=None):
    bucket = store["monthly"].get(month_key(now), [])
    return _top_from_bucket(bucket, n=n, highest_first=highest_first)

def top_year(store, n=5, highest_first=True, now=None):
    bucket = store["yearly"].get(year_key(now), [])
    return _top_from_bucket(bucket, n=n, highest_first=highest_first)

def top_alltime(store, n=5, highest_first=True):
    bucket = store.get("alltime", [])
    return _top_from_bucket(bucket, n=n, highest_first=highest_first)

def best_today_score(store, now=None):
    t = top_today(store, n=1, highest_first=True, now=now)
    return t[0]["score"] if t else 0.0

def best_alltime_score(store):
    t = top_alltime(store, n=1, highest_first=True)
    return t[0]["score"] if t else 0.0