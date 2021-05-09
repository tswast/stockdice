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
import pathlib
import logging
import time

import aiohttp
import pandas
import numpy
import math
import requests
import toml


DIR = pathlib.Path(__file__).parent
NASDAQ_DIR = DIR / "third_party" / "ftp.nasdaqtrader.com"
FMP_DIR = DIR / "third_party" / "financialmodelingprep.com"


with open(DIR / "environment.toml") as config_file:
    config = toml.load(config_file)

FMP_API_KEY = config["FMP_API_KEY"]
FMP_QUOTE = "https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={apikey}"
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


async def download_book_value(session, symbol):
    """
    https://codingandfun.com/how-to-calculate-price-book-ratio-with-python/
    """
    url = FMP_BALANCE_SHEET.format(symbol=symbol, apikey=FMP_API_KEY)
    async with session.get(url) as resp:
        resp_json = await resp.json()
        book_value = None
        if resp_json:
            book_value = resp_json[0].get("totalStockholdersEquity")
        if book_value is None:
            logging.warning(f"no book value for {symbol}")
            return 1
        return book_value


async def download_market_cap(session, symbol):
    url = FMP_QUOTE.format(symbol=symbol, apikey=FMP_API_KEY)
    async with session.get(url) as resp:
        resp_json = await resp.json()
        market_cap = None
        if resp_json:
            market_cap = resp_json[0].get("marketCap")
        if market_cap is None:
            logging.warning(f"no market cap for {symbol}")
            return 1
        return market_cap


def geometric_mean(a, b):
    return math.exp(0.5 * (math.log(a) + math.log(b)))


async def append_values(session, symbol, out):
    book = await download_book_value(session, symbol)
    market_cap = await download_market_cap(session, symbol)
    average = geometric_mean(max(1, book), max(1, market_cap))
    out.write(
        f"{symbol},{book},{market_cap},{average}\n"
    )


async def main():
    # all_symbols = load_symbols()[:1]
    all_symbols = load_symbols()

    with open(FMP_DIR / "values.csv", "w") as out:
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
                await append_values(session, symbol, out)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
