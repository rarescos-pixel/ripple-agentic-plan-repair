from __future__ import annotations
import os, statistics, time, httpx

BASE = os.getenv("RIPPLE_SMOKE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
COUNT = int(os.getenv("RIPPLE_LATENCY_SAMPLES", "100"))

with httpx.Client(timeout=5.0) as c:
    samples=[]
    for _ in range(COUNT):
        t=time.perf_counter(); r=c.get(BASE+"/healthz"); r.raise_for_status(); samples.append((time.perf_counter()-t)*1000)
    ordered=sorted(samples)
    p50=statistics.median(samples); p95=ordered[max(0,int(len(ordered)*0.95)-1)]
    print(f"health samples={COUNT} p50_ms={p50:.2f} p95_ms={p95:.2f} max_ms={max(samples):.2f}")
