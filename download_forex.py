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

import aiohttp

from helpers import *


FMP_FOREX = "https://financialmodelingprep.com/api/v3/fx?apikey={apikey}"


@retry_fmp
async def download_forex(session, out):
    url = FMP_FOREX.format(apikey=FMP_API_KEY)
    async with session.get(url) as resp:
        resp_json = await check_status(resp)
        for forex in resp_json:
            ticker = forex.get("ticker")
            bid = forex.get("bid")
            ask = forex.get("ask")
            out.write(f"{ticker},{bid},{ask}\n")


async def main():
    csv_path = FMP_DIR / "forex.csv"
    with open(csv_path, "w") as out:
        async with aiohttp.ClientSession() as session:
            await download_forex(session, out)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
