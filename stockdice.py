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

import pandas
import numpy


def mc_to_float(cap):
    if not cap:
        return numpy.nan
    if not cap.startswith('$'):
        return numpy.nan
    cap = cap[1:]
    multiplier = 1.0
    if cap.endswith('K'):
        multiplier = 1000.0
    elif cap.endswith('M'):
        multiplier = 1.0e6
    elif cap.endswith('B'):
        multiplier = 1.0e9
    elif cap.endswith('T'):
        multiplier = 1.0e12

    try:
        return float(cap[:-1]) * multiplier
    except ValueError:
        print(cap)
        raise


# In[4]:

screen_path = pathlib.Path("third_party") / "tdameritrade" / "screen.csv"
screen = pandas.read_csv(screen_path)
screen = screen.assign(MarketCap=screen.MarketCap.apply(mc_to_float))
print(len(screen.index))
screen = screen[screen.MarketCap.notna()]
print(len(screen.index))

# In[10]:

# Weight by square root of market cap to shift portfolio towards "value"
print(screen.sample(weights=screen.MarketCap.apply(numpy.sqrt)))

