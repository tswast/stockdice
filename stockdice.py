#!/usr/bin/env python
# coding: utf-8
# Copyright 2018 Banana Juice LLC
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

import pathlib

import numpy
import pandas


DIR = pathlib.Path(__file__).parent
FMP_DIR = DIR / "third_party" / "financialmodelingprep.com"


quote_path = FMP_DIR / "quote.csv"
quote = pandas.read_csv(quote_path, header=None, names=["symbol", "market_cap"])
income_path = FMP_DIR / "income-statement.csv"
income = pandas.read_csv(
    income_path, header=None, names=["symbol", "profit", "revenue", "currency"],
)
balance_sheet_path = FMP_DIR / "balance-sheet-statement.csv"
balance_sheet = pandas.read_csv(
    balance_sheet_path, header=None, names=["symbol", "book", "currency"],
)
screen = quote.merge(
    income.merge(balance_sheet, how="outer", on="symbol",), how="outer", on="symbol",
).fillna(value=0)
screen_ones = numpy.ones(len(screen.index))

# Even weight seemed to skew too heavily towards value. Place a more weight in
# market cap, since market risk is the main factor I want to target.
screen["average"] = numpy.exp(
    (1.0 / 9.0)
    * (
        numpy.log(numpy.fmax(screen_ones, screen["book"]))
        + numpy.log(numpy.fmax(screen_ones, screen["profit"]))
        + numpy.log(numpy.fmax(screen_ones, screen["revenue"]))
        + 6 * numpy.log(numpy.fmax(screen_ones, screen["market_cap"]))
    )
)

symbol = screen.sample(weights=screen["average"])
print(symbol)
