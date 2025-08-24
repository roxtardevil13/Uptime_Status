from typing import Dict, List
from datetime import datetime, timedelta

_DB: Dict[str, List[dict]] = {}

def add_ping(url: str, ms: float | None, code: int | None) -> None:
    _DB.setdefault(url, []).append({"ts": datetime.utcnow().isoformat(), "ms": ms, "code": code})
    if len(_DB[url]) > 1000:
        _DB[url] = _DB[url][-1000:]

def get_targets() -> list[str]:
    return list(_DB.keys())

def recent(url: str, within_minutes: int = 60) -> List[dict]:
    cutoff = datetime.utcnow() - timedelta(minutes=within_minutes)
    out = []
    for r in _DB.get(url, []):
        if datetime.fromisoformat(r["ts"]) >= cutoff:
            out.append(r)
    return out

def metrics_summary(url: str, within_minutes: int = 60) -> dict:
    rows = recent(url, within_minutes)
    if not rows:
        return {"url": url, "count": 0, "uptime_pct": 0.0, "p95_ms": None, "last_status": None}
    oks = [1 for r in rows if r.get("code") and 200 <= r["code"] < 400]
    lat = sorted([r["ms"] for r in rows if r.get("ms") is not None])
    p95 = lat[int(0.95 * (len(lat) - 1))] if lat else None
    return {
        "url": url,
        "count": len(rows),
        "uptime_pct": round(100.0 * len(oks) / len(rows), 2) if rows else 0.0,
        "p95_ms": p95,
        "last_status": rows[-1]["code"] if rows else None,
        "updatedAt": rows[-1]["ts"] if rows else None
    }
