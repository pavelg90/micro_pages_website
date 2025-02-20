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
import pandas as pd

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

CACHE_FILE = "cache_data.json"
CACHE_EXPIRATION = 86400  # 24 hours

indices_symbols = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC"
}

cache_data = {}

def read_cache():
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def write_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f)

@app.on_event("startup")
async def startup_event():
    global cache_data
    cache_data = read_cache()

def fetch_data(symbol: str, start_date: datetime.datetime, end_date: datetime.datetime):
    return yf.download(symbol, start=start_date, end=end_date, progress=False, threads=False)

async def get_index_annual_return(symbol: str, period_years: int = 10):
    global cache_data
    now = time.time()

    if symbol in cache_data:
        symbol_data = cache_data[symbol]
        if symbol_data.get("symbol") == symbol and (now - symbol_data["timestamp"] < CACHE_EXPIRATION):
            return symbol_data["data"]

    loop = asyncio.get_event_loop()
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=period_years * 365)

    data = await loop.run_in_executor(None, fetch_data, symbol, start_date, end_date)
    if data.empty:
        return None

    price_column = "Adj Close" if "Adj Close" in data.columns else "Close"
    # Check if data[price_column] is a DataFrame with one column or a Series:
    if isinstance(data[price_column], pd.DataFrame):
        start_price = data[price_column].iloc[0, 0]
        end_price = data[price_column].iloc[-1, 0]
    else:
        start_price = data[price_column].iloc[0]
        end_price = data[price_column].iloc[-1]
    cagr = (end_price / start_price) ** (1 / period_years) - 1
    cagr_value = float(cagr * 100)

    cache_data[symbol] = {
        "timestamp": now,
        "data": cagr_value,
        "symbol": symbol
    }
    write_cache(cache_data)
    return cagr_value

async def get_indices_data():
    tasks = []
    for symbol in indices_symbols.values():
        tasks.append(asyncio.create_task(get_index_annual_return(symbol)))
    results = await asyncio.gather(*tasks)

    # Match each symbol back to the correct index name in order
    return {name: val for (name, _), val in zip(indices_symbols.items(), results)}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    indices = await get_indices_data()
    return templates.TemplateResponse("index.html", {"request": request, "indices": indices})
