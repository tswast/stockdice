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

import itertools
import pathlib
import ftplib


DIR = pathlib.Path(__file__).parent
NASDAQ_DIR = DIR / "third_party" / "ftp.nasdaqtrader.com"


def download_symbol_directory():
    """
    https://quant.stackexchange.com/a/1862/55288
    https://stackoverflow.com/a/11573946/101923
    """
    ftp = ftplib.FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("Symboldirectory")
    with open(NASDAQ_DIR / "nasdaqlisted.txt", "wb") as handle:
        ftp.retrbinary("RETR nasdaqlisted.txt", handle.write)
    with open(NASDAQ_DIR / "otherlisted.txt", "wb") as handle:
        ftp.retrbinary("RETR otherlisted.txt", handle.write)
    ftp.close()


def load_nasdaq_symbols():
    with open(NASDAQ_DIR / "nasdaqlisted.txt", "r") as nasdaq_file:
        is_header = True
        for line in nasdaq_file:
            if is_header:
                is_header = False
                continue
            yield line.split("|")[0]


def load_other_symbols():
    with open(NASDAQ_DIR / "otherlisted.txt", "r") as nasdaq_file:
        is_header = True
        for line in nasdaq_file:
            parts = line.split("|")
            etf_col = parts[4]

            if is_header:
                assert etf_col == "ETF"
                is_header = False
                continue

            is_etf = etf_col == "Y"
            if not is_etf:
                yield parts[0]


def write_all_symbols():
    all_symbols = itertools.chain(load_nasdaq_symbols(), load_other_symbols())
    with open(NASDAQ_DIR / "allsymbols.txt", "w") as symbols_file:
        for symbol in all_symbols:
            symbols_file.write(symbol + "\n")


if __name__ == "__main__":
    download_symbol_directory()
    write_all_symbols()
