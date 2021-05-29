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


__all__ = [
    "DIR",
    "NASDAQ_DIR",
    "FMP_DIR",
    "FMP_API_KEY",
    "RateLimitError",
    "retry_fmp",
    "check_status",
]
