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
import functools

import toml


DIR = pathlib.Path(__file__).parent
NASDAQ_DIR = DIR / "third_party" / "ftp.nasdaqtrader.com"
FMP_DIR = DIR / "third_party" / "financialmodelingprep.com"

with open(DIR / "environment.toml") as config_file:
    config = toml.load(config_file)

FMP_API_KEY = config["FMP_API_KEY"]

RATE_LIMIT_STATUS = 429
RATE_LIMIT_SECONDS = "X-Rate-Limit-Retry-After-Seconds"
RATE_LIMIT_MILLISECONDS = "X-Rate-Limit-Retry-After-Milliseconds"

forex_to_usd = None

class RateLimitError(Exception):
    def __init__(self, seconds, millis):
        self.seconds = seconds
        self.millis = millis


def retry_fmp(async_fn):
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


def load_forex():
    global forex_to_usd
    forex_to_usd = {"USD": 1.0}
    csv_path = FMP_DIR / "forex.csv"

    with open(csv_path) as forex_csv:
        for line in forex_csv:
            line = line.strip()
            ticker, bid, ask = line.split(",")
            # Use average of bid/ask for simplicity.
            price = (float(bid) + float(ask)) / 2.0
            from_curr, to_curr = ticker.split("/")

            if to_curr == "USD":
                forex_to_usd[from_curr] = price
            elif from_curr == "USD":
                forex_to_usd[to_curr] = 1.0 / price

    # CNY is reported value for some incomes and balance sheets, but not
    # available in Forex API. CNH is related and tracks closely, but has more
    # volatility.
    # https://www.nasdaq.com/articles/cnh-vs-cny-differences-between-two-yuan-2018-09-12
    forex_to_usd["CNY"] = forex_to_usd["CNH"]


def to_usd(curr, value):
    if forex_to_usd is None:
        load_forex()

    if curr == "None":
        # Assume USD? None usually corresponds to no reported value, anyway.
        return value

    return forex_to_usd[curr] * value

__all__ = [
    "DIR",
    "NASDAQ_DIR",
    "FMP_DIR",
    "FMP_API_KEY",
    "RateLimitError",
    "retry_fmp",
    "check_status",
    "to_usd",
]
