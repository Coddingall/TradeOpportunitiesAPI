# trade_opportunities_api.py

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import PlainTextResponse
from functools import wraps
import time

app = FastAPI()

# === In-memory session and rate limiter ===
requests_log = {}

def rate_limiter(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        user = kwargs.get("user", "guest")
        now = time.time()
        window = 60  # seconds
        max_requests = 5

        if user not in requests_log:
            requests_log[user] = []
        requests_log[user] = [ts for ts in requests_log[user] if now - ts < window]

        if len(requests_log[user]) >= max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        requests_log[user].append(now)
        return await func(*args, **kwargs)
    return wrapper

# === Basic authentication ===
def authenticate_user(authorization: str = Header(default="guest")):
    if authorization != "guest":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "guest"

# === Simulated data fetch and analysis ===
def fetch_market_data(sector: str) -> str:
    # Replace with web scraping or API fetching logic
    return f"Latest trends and market updates for the {sector} sector in India."

def analyze_with_gemini(sector: str, market_data: str) -> str:
    # Simulated AI-generated markdown report
    return f"""
# Market Analysis Report: {sector.title()}

## Sector Overview
{market_data}

## Trade Opportunities
- Increased demand in domestic markets.
- Export potential due to international interest.
- Government policies and subsidies enhancing sector growth.

*Generated using AI*
"""

# === Main endpoint ===
@app.get("/analyze/{sector}", response_class=PlainTextResponse)
@rate_limiter
async def analyze_sector(sector: str, user: str = Depends(authenticate_user)):
    try:
        market_data = fetch_market_data(sector)
        report = analyze_with_gemini(sector, market_data)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

