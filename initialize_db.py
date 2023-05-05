#!/usr/bin/env python
# coding: utf-8
# Copyright 2023 Banana Juice LLC
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
import sys

import pandas

from helpers import *


def create_quote():
    DB.execute("DROP TABLE quotes;")
    DB.execute("""
    CREATE TABLE quotes(
    symbol STRING PRIMARY KEY,
    market_cap_usd REAL,
    last_updated_us INTEGER
    );
    """)


def load_quote(quote_path):
    quote = pandas.read_csv(quote_path, header=None, names=["symbol", "market_cap_usd"], index_col="symbol")
    quote = quote.groupby(quote.index).last()
    quote.to_sql("quotes", DB, if_exists="append")


def create_balance_sheet():
    DB.execute("DROP TABLE balance_sheets;")
    DB.execute("""
    CREATE TABLE balance_sheets(
    symbol STRING PRIMARY KEY,
    book REAL,
    currency STRING,
    last_updated_us INTEGER
    );
    """)


def load_balance_sheet(balance_sheet_path):
    balance_sheet = pandas.read_csv(
        balance_sheet_path,
        header=None,
        names=["symbol", "book", "currency"],
        index_col="symbol",
    )
    balance_sheet = balance_sheet.groupby(balance_sheet.index).last()
    balance_sheet.to_sql("balance_sheets", DB, if_exists="append")


def create_income():
    DB.execute("DROP TABLE incomes;")
    DB.execute("""
    CREATE TABLE incomes(
    symbol STRING PRIMARY KEY,
    profit REAL,
    revenue REAL,
    currency STRING,
    last_updated_us INTEGER
    );
    """)


def load_income(income_path):
    income = pandas.read_csv(
        income_path,
        header=None,
        names=["symbol", "profit", "revenue", "currency"],
        index_col="symbol",
    )
    income = income.groupby(income.index).last()
    income.to_sql("incomes", DB, if_exists="append")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    args = parser.parse_args()
    command = args.command
    if command == "quote":
        csv_path = FMP_DIR / "quote.csv"
        create_quote()
        load_quote(csv_path)
    elif command == "balance-sheet":
        csv_path = FMP_DIR / "balance-sheet-statement.csv"
        create_balance_sheet()
        load_balance_sheet(csv_path)
    elif command == "income":
        csv_path = FMP_DIR / "income-statement.csv"
        create_income()
        load_income(csv_path)
    else:
        sys.exit("expected {quote,balance-sheet,income}")
    

