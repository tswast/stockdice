#!/usr/bin/env python
# coding: utf-8
# Copyright 2021 Banana Juice LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import functools
import pathlib
import logging
import time
import sys

import aiohttp
import toml


DIR = pathlib.Path(__file__).parent
NASDAQ_DIR = DIR / "third_party" / "ftp.nasdaqtrader.com"
FMP_DIR = DIR / "third_party" / "financialmodelingprep.com"


with open(DIR / "environment.toml") as config_file:
    config = toml.load(config_file)

FMP_API_KEY = config["FMP_API_KEY"]
FMP_QUOTE = "https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={apikey}"
FMP_INCOME_STATEMENT = "https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit=1&apikey={apikey}"
FMP_BALANCE_SHEET = "https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?period=quarter&limit=1&apikey={apikey}"

BATCH_SIZE = 10
BATCH_WAIT = 1
RATE_LIMIT_STATUS = 429
RATE_LIMIT_SECONDS = "X-Rate-Limit-Retry-After-Seconds"
RATE_LIMIT_MILLISECONDS = "X-Rate-Limit-Retry-After-Milliseconds"


def load_symbols():
    all_symbols = []

    with open(NASDAQ_DIR / "allsymbols.txt", "r") as handle:
        for line in handle:
            all_symbols.append(line.strip())

    return all_symbols


class RateLimitError(Exception):
    def __init__(self, seconds, millis):
        self.seconds = seconds
        self.millis = millis


def retry(async_fn):
    @functools.wraps(async_fn)
    async def wrapped(*args):
        while True:
            try:
                value = await async_fn(*args)
            except RateLimitError as exp:
                await asyncio.sleep(exp.seconds + (exp.millis / 1000.0))
            except:
                raise
            else:
                return value

    return wrapped


async def check_status(resp):
    if resp.status == RATE_LIMIT_STATUS:
        raise RateLimitError(1, 0)
    resp_json = await resp.json()
    if RATE_LIMIT_SECONDS in resp_json or RATE_LIMIT_MILLISECONDS in resp_json:
        raise RateLimitError(
            float(resp_json.get(RATE_LIMIT_SECONDS, 0)),
            float(resp_json.get(RATE_LIMIT_MILLISECONDS, 0)),
        )
    return resp_json


@retry
async def download_annual_revenue(session, symbol, out):
    """
    https://www.ftserussell.com/research/factor-exposure-indexes-value-factor

    Earnings Yield, Cash Flow Yield and Sales to Price (most performance)
    """
    url = FMP_INCOME_STATEMENT.format(symbol=symbol, apikey=FMP_API_KEY)
    async with session.get(url) as resp:
        resp_json = await check_status(resp)
        profit = None
        revenue = None
        if resp_json:
            profit = resp_json[0].get("grossProfit")
            revenue = resp_json[0].get("revenue")
        if revenue is None:
            logging.warning(f"no revenue for {symbol}")
            revenue = 0
        if profit is None:
            logging.warning(f"no profit for {symbol}")
            profit = 0
        out.write(f"{symbol},{profit},{revenue}\n")


@retry
async def download_book_value(session, symbol, out):
    """
    https://codingandfun.com/how-to-calculate-price-book-ratio-with-python/

    https://www.ftserussell.com/research/factor-exposure-indexes-value-factor

    Book to Price (most diversified)
    """
    url = FMP_BALANCE_SHEET.format(symbol=symbol, apikey=FMP_API_KEY)
    async with session.get(url) as resp:
        resp_json = await resp.json()
        book_value = None
        if resp_json:
            book_value = resp_json[0].get("totalStockholdersEquity")
        if book_value is None:
            logging.warning(f"no book value for {symbol}")
            book_value = 0
        out.write(f"{symbol},{book_value}\n")


@retry
async def download_market_cap(session, symbol, out):
    url = FMP_QUOTE.format(symbol=symbol, apikey=FMP_API_KEY)
    async with session.get(url) as resp:
        resp_json = await resp.json()
        market_cap = None
        if resp_json:
            market_cap = resp_json[0].get("marketCap")
        if market_cap is None:
            logging.warning(f"no market cap for {symbol}")
            market_cap = 0
        out.write(f"{symbol},{market_cap}\n")


async def main(csv_path, download_fn):
    # all_symbols = load_symbols()[:1]
    all_symbols = load_symbols()

    with open(csv_path, "w") as out:
        async with aiohttp.ClientSession() as session:
            batch_index = 0
            batch_start = time.monotonic()
            for symbol in all_symbols:
                # Rate limit!
                if batch_index >= BATCH_SIZE:
                    batch_time = time.monotonic() - batch_start()
                    remaining = BATCH_WAIT - batch_time
                    if remaining > 0:
                        await asyncio.sleep(remaining)
                    batch_start = time.monotonic()
                    batch_index = 0
                await download_fn(session, symbol, out)


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "quote":
        csv_path = FMP_DIR / "quote.csv"
        download_fn = download_market_cap
    elif command == "balance-sheet":
        csv_path = FMP_DIR / "balance-sheet-statement.csv"
        download_fn = download_book_value
    elif command == "income":
        csv_path = FMP_DIR / "income-statement.csv"
        download_fn = download_annual_revenue
    else:
        sys.exit("expected {quote,balance-sheet,income}")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(csv_path, download_fn))
