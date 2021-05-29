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

from helpers import *

FMP_FOREX = "https://financialmodelingprep.com/api/v3/fx?apikey={apikey}"

# Note: CNY is reported value for some incomes, but not available in Forex API.
# CNH is related and tracks closely, but has more volatility.
# https://www.nasdaq.com/articles/cnh-vs-cny-differences-between-two-yuan-2018-09-12

# TODO: test the direction is evaluated correctly. USD/CNH, but EUR/USD.
# TODO: use average of bid/ask?

