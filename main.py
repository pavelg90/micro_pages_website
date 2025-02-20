import os
import json
import time
import datetime
import asyncio
import math
import yfinance as yf

from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Path to the JSON file used for caching
CACHE_FILE = "cache_data.json"

# Cache expiration in seconds (86400 = 24 hours)
CACHE_EXPIRATION = 86400

# Dictionary of indices and their symbols
indices_symbols = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC"
}

# In-memory dictionary to hold the cache data while app is running
cache_data = {}

def read_cache():
    """Load cache data from disk into a Python dictionary."""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def write_cache(cache):
    """Persist the cache data to a JSON file on disk."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f)

@app.on_event("startup")
async def startup_event():
    """Load cache from disk when the server starts."""
    global cache_data
    cache_data = read_cache()

def fetch_data(symbol: str, start_date: datetime.datetime, end_date: datetime.datetime):
    """Blocking function to fetch data from yfinance."""
    return yf.download(symbol, start=start_date, end=end_date, progress=False)

async def get_index_annual_return(symbol: str, period_years: int = 10):
    """Return the cached CAGR value for the given symbol or fetch and cache it."""
    global cache_data
    now = time.time()

    # Check if we have a valid cached entry
    if symbol in cache_data:
        symbol_data = cache_data[symbol]
        if now - symbol_data["timestamp"] < CACHE_EXPIRATION:
            return symbol_data["data"]

    # Not in cache or expired; fetch new data
    loop = asyncio.get_event_loop()
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=period_years * 365)

    data = await loop.run_in_executor(None, fetch_data, symbol, start_date, end_date)
    if data.empty:
        return None

    price_column = "Adj Close" if "Adj Close" in data.columns else "Close"
    start_price = data[price_column].iloc[0]
    end_price = data[price_column].iloc[-1]
    cagr = (end_price / start_price) ** (1 / period_years) - 1
    cagr_value = float(cagr * 100)  # Convert to float

    # Update cache in memory
    cache_data[symbol] = {
        "timestamp": now,
        "data": cagr_value
    }
    # Write updated cache to disk
    write_cache(cache_data)

    return cagr_value

async def get_indices_data():
    """Retrieve or fetch the CAGR for each index and return as a dict."""
    tasks = []
    for symbol in indices_symbols.values():
        tasks.append(asyncio.create_task(get_index_annual_return(symbol)))
    results = await asyncio.gather(*tasks)
    return {name: val for (name, _), val in zip(indices_symbols.items(), results)}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    indices = await get_indices_data()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "indices": indices
        }
    )

@app.post("/calculate", response_class=HTMLResponse)
async def calculate(
    request: Request,
    investment_type: str = Form(...),
    initial_amount: float = Form(...),
    monthly_contribution: float = Form(...),
    annual_interest: float = Form(...),
    years: int = Form(...)
):
    """
    Compound interest calculation with monthly compounding.
    A = P(1 + r/n)^(n*t) + PMT * [((1 + r/n)^(n*t) - 1) / (r/n)]
    """

    n = 12
    r = annual_interest / 100
    t = years
    P = initial_amount
    PMT = monthly_contribution

    if r > 0:
        final_amount = P * (1 + r / n) ** (n * t) + PMT * (((1 + r / n) ** (n * t) - 1) / (r / n))
    else:
        final_amount = P + PMT * n * t

    return templates.TemplateResponse(
        "calculator.html",
        {
            "request": request,
            "investment_type": investment_type,
            "initial_amount": initial_amount,
            "monthly_contribution": monthly_contribution,
            "annual_interest": annual_interest,
            "years": years,
            "final_amount": round(final_amount, 2)
        }
    )


