from fastapi import FastAPI, Query
from typing import List
from storage import get_targets, metrics_summary

app = FastAPI(title="Uptime API")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/targets", response_model=List[str])
def targets():
    return get_targets()


@app.get("/metrics")
def metrics(url: str = Query(..., description="URL to summarize"), minutes: int = 60):
    return metrics_summary(url, within_minutes=minutes)
