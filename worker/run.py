import os, time, requests
from datetime import datetime

API_BASE = os.getenv("API_BASE", "http://localhost:8080")
TARGETS = os.getenv("TARGETS", "https://example.com,https://github.com").split(",")
INTERVAL_SEC = int(os.getenv("INTERVAL_SEC", "60"))

def ping(url: str):
    try:
        r = requests.get(url, timeout=10)
        ms = r.elapsed.total_seconds() * 1000.0
        return ms, r.status_code
    except Exception:
        return None, None

def loop():
    while True:
        for u in [t.strip() for t in TARGETS if t.strip()]:
            ms, code = ping(u)
            # Demo: print results. Upgrade to Postgres write in production.
            print(f"[{datetime.utcnow().isoformat()}] {u} -> ms={ms} code={code}")
        time.sleep(INTERVAL_SEC)

if __name__ == "__main__":
    loop()
