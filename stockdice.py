
# coding: utf-8

# In[1]:


import pandas
import numpy
import os.path


def mc_to_float(cap):
  #if not cap:
  # return numpy.nan
  #if not cap.startswith('$'):
  #  return numpy.nan
  cap = cap[1:]
  multiplier = 1.0
  if cap.endswith('K'):
    multiplier = 1000.0
  elif cap.endswith('M'):
    multiplier = 1.0e6
  elif cap.endswith('B'):
    multiplier = 1.0e9
  elif cap.endswith('T'):
    multiplier =1.0e12

  return float(cap[:-1]) * multiplier


# In[4]:


nasdaq = pandas.read_csv(os.path.join('third_party', 'nasdaq', 'nasdaq.csv'))
nasdaq = nasdaq[nasdaq.MarketCap.notna()]
nasdaq = nasdaq.assign(MarketCap=nasdaq.MarketCap.apply(mc_to_float))


# In[5]:


nyse = pandas.read_csv(os.path.join('third_party', 'nasdaq', 'nyse.csv'))
nyse = nyse[nyse.MarketCap.notna()]
nyse = nyse.assign(MarketCap=nyse.MarketCap.apply(mc_to_float))


# In[6]:


amex = pandas.read_csv(os.path.join('third_party', 'nasdaq', 'amex.csv'))
amex = amex[amex.MarketCap.notna()]
amex = amex.assign(MarketCap=amex.MarketCap.apply(mc_to_float))


# In[7]:


nasdaq = nasdaq.assign(Market='nasdaq')
nyse = nyse.assign(Market='nyse')
amex = amex.assign(Market='amex')


# In[8]:


stocks = pandas.concat([nasdaq, nyse, amex])


# In[10]:


print(stocks.sample(weights=stocks.MarketCap))

