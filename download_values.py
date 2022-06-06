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

import argparse
import asyncio
import logging
import time
import sys

import aiohttp

from helpers import *


FMP_QUOTE = "https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={apikey}"
FMP_INCOME_STATEMENT = "https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit=1&apikey={apikey}"
FMP_BALANCE_SHEET = "https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?period=quarter&limit=1&apikey={apikey}"

BATCH_SIZE = 10
BATCH_WAIT = 1


def load_symbols():
    all_symbols = []

    with open(NASDAQ_DIR / "allsymbols.txt", "r") as handle:
        for line in handle:
            all_symbols.append(line.strip())

    all_symbols.sort()
    return all_symbols


@retry_fmp
async def download_income(session, symbol, out):
    """
    https://www.ftserussell.com/research/factor-exposure-indexes-value-factor

    Earnings Yield, Cash Flow Yield and Sales to Price (most performance)
    """
    url = FMP_INCOME_STATEMENT.format(symbol=symbol, apikey=FMP_API_KEY)
    async with session.get(url) as resp:
        resp_json = await check_status(resp)
        profit = None
        revenue = None
        currency = None
        if resp_json:
            profit = resp_json[0].get("grossProfit")
            revenue = resp_json[0].get("revenue")
            currency = resp_json[0].get("reportedCurrency")
        if revenue is None:
            logging.warning(f"no revenue for {symbol}")
            revenue = 0
        if profit is None:
            logging.warning(f"no profit for {symbol}")
            profit = 0
        out.write(f"{symbol},{profit},{revenue},{currency}\n")


@retry_fmp
async def download_balance_sheet(session, symbol, out):
    """
    https://codingandfun.com/how-to-calculate-price-book-ratio-with-python/

    https://www.ftserussell.com/research/factor-exposure-indexes-value-factor

    Book to Price (most diversified)
    """
    url = FMP_BALANCE_SHEET.format(symbol=symbol, apikey=FMP_API_KEY)
    async with session.get(url) as resp:
        resp_json = await check_status(resp)
        book_value = None
        currency = None
        if resp_json:
            book_value = resp_json[0].get("totalStockholdersEquity")
            currency = resp_json[0].get("reportedCurrency")
        if book_value is None:
            logging.warning(f"no book value for {symbol}")
            book_value = 0
        out.write(f"{symbol},{book_value},{currency}\n")


@retry_fmp
async def download_market_cap(session, symbol, out):
    url = FMP_QUOTE.format(symbol=symbol, apikey=FMP_API_KEY)
    async with session.get(url) as resp:
        resp_json = await check_status(resp)
        market_cap = None
        if resp_json:
            market_cap = resp_json[0].get("marketCap")
        if market_cap is None:
            logging.warning(f"no market cap for {symbol}")
            market_cap = 0
        out.write(f"{symbol},{market_cap}\n")


async def main(csv_path, download_fn, start_symbol=None):
    # all_symbols = load_symbols()[:1]
    all_symbols = load_symbols()

    with open(csv_path, "w") as out:
        async with aiohttp.ClientSession() as session:
            batch_index = 0
            batch_start = time.monotonic()
            for symbol in all_symbols:
                # Assume symbols are in alphabetical order.
                if start_symbol is not None and symbol < start_symbol:
                    continue

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--start")
    parser.add_argument("command")
    args = parser.parse_args()
    command = args.command
    if command == "quote":
        csv_path = FMP_DIR / "quote.csv"
        download_fn = download_market_cap
    elif command == "balance-sheet":
        csv_path = FMP_DIR / "balance-sheet-statement.csv"
        download_fn = download_balance_sheet
    elif command == "income":
        csv_path = FMP_DIR / "income-statement.csv"
        download_fn = download_income
    else:
        sys.exit("expected {quote,balance-sheet,income}")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(csv_path, download_fn, start_symbol=args.start))
