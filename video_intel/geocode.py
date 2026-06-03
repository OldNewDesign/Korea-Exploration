"""Turn location text into coordinates. Uses the Google Geocoding API when a
key is set (best for messy / Korean addresses), otherwise OpenStreetMap's free
Nominatim service. Results are cached in SQLite, so each place is looked up only
once. Respects per-provider rate limits."""
import json
import time
import urllib.parse
import urllib.request
from . import config, store

_last = [0.0]


def _interval():
    # Google tolerates higher QPS; Nominatim asks for <=1/sec.
    return 0.05 if config.use_google_geocode() else config.GEO_MIN_INTERVAL


def _rate_limit():
    iv = _interval()
    dt = time.time() - _last[0]
    if dt < iv:
        time.sleep(iv - dt)
    _last[0] = time.time()


def _clean(q):
    q = (q or "").replace("\u2014", ",").replace("\u2013", ",")
    return " ".join(q.split()).strip(" ,")


def _candidates(q):
    """Try the full string first, then a simplified region-only version."""
    cands = [q]
    parts = [p.strip() for p in q.split(",") if p.strip()]
    if len(parts) > 2:
        cands.append(", ".join(parts[-2:]))   # e.g. "Gangnam-gu, Seoul"
    return cands


def _query_google(q):
    url = "https://maps.googleapis.com/maps/api/geocode/json?" + urllib.parse.urlencode(
        {"address": q, "key": config.GOOGLE_MAPS_API_KEY}
    )
    with urllib.request.urlopen(url, timeout=20) as resp:
        data = json.load(resp)
    status = data.get("status")
    if status == "OK" and data.get("results"):
        r = data["results"][0]
        loc = r["geometry"]["location"]
        return float(loc["lat"]), float(loc["lng"]), r.get("formatted_address", "")
    if status in ("OVER_QUERY_LIMIT", "REQUEST_DENIED", "INVALID_REQUEST"):
        raise RuntimeError(f"Google geocode {status}: {data.get('error_message','')}")
    return None  # ZERO_RESULTS


def _query_nominatim(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": 1}
    )
    req = urllib.request.Request(url, headers={"User-Agent": config.GEO_USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        arr = json.load(resp)
    if arr:
        return float(arr[0]["lat"]), float(arr[0]["lon"]), arr[0].get("display_name", "")
    return None


def _query(q):
    return _query_google(q) if config.use_google_geocode() else _query_nominatim(q)


def geocode(location):
    """Return (lat, lng, display_name) or None. Uses + fills the cache."""
    q = _clean(location)
    if not q:
        return None

    cached = store.geocache_get(q)
    if cached is not None:
        return (cached[1], cached[2], cached[3]) if cached[0] == "hit" else None

    result = None
    for cand in _candidates(q):
        _rate_limit()
        try:
            result = _query(cand)
        except Exception:
            result = None
        if result:
            break

    if result:
        store.geocache_set(q, result[0], result[1], result[2])
        return result
    store.geocache_set(q, None, None, "")   # remember the miss
    return None
