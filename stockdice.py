
# coding: utf-8

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

print(screen.sample(weights=screen.MarketCap))

