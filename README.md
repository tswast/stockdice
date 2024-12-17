# stockdice

Choose stocks randomly, weighted by market cap

Company list CSV file is exported from a TD Ameritrade stock screen.

## Setup

Clone the repository. Alternatively, [fork this repository](https://github.com/tswast/stockdice/fork) and clone your own copy.

```
git clone https://github.com/tswast/stockdice.git
cd stockdice
```

Setup a Python development environment.

```
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Initialize the local database.

```
python initialize_db.py all
```

Get an API key for [Financial Modeling Prep](https://site.financialmodelingprep.com/). Because this script downloads values in bulk, a paid plan is required.

1. Sign up for an account. I'm using the "Starter" plan for personal use.
2. Go to your [dashboard](https://site.financialmodelingprep.com/developer/docs/dashboard) and get an API key.
3. Create a copy of the environment "toml" file. `cp environment-EXAMPLE.toml environment.toml`
4. Replace the API key in `environment.toml` with your own.

### [Optional] Choose your formula

In this stock picker, I'm weighting about 50% on market cap and the rest on an arbitrary-ish formula to shift towards "value". To change to a purely market cap weighted picker, change the [formula to compute the "average" column in stockdice.py](https://github.com/tswast/stockdice/blob/977ad90827136bd8d78db653051139a8eb67bf58/stockdice.py#L90-L98) to just `numpy.fmax(screen_ones, screen["market_cap"])`.

## Usage

To use this random stock picker, first download the list of stocks from NASDAQ using FTP.

```
source venv/bin/activate
python download_symbol_directory.py
```

Next, download foreign exchange rates. This is needed to convert reported revenue and other numbers to USD used in the "value" part of the formula. Market caps are USD, so this step is not needed if you simplify the formula as stated in the setup steps above.

```
python download_forex.py
```

Note: Occasionally, I need to update the `CURRENCIES` set and re-run if a new currency is encountered when downloading values in the next steps.

Next, download the values for `quote` (used to calculate market cap), `balance-sheet`, and `incomes` (for revenue). These can be done in parallel (e.g. in separate terminal windows).

```
python download_values.py quote
python download_values.py balance-sheet
python download_values.py income
```

Sometimes these will fail (usually because of rate limiting). Restart the command within 24 hours and it will resume where it left off.

Pick a stock.

```
python stockdice.py
```

This will print out a symbol, as well as additional information about the stock. Purchase a selection of this stock. For example, purchase $1,000 of each stock chosen so that the weighting of your portfolio approaches that of the formula. It is helpful to use a broker which sells partial shares so that you can get as close to an even amout per stock as possible.

## Disclaimer

The Content is for informational purposes only, you should not construe
any such information or other material as legal, tax, investment,
financial, or other advice. Nothing contained on our Site constitutes a
solicitation, recommendation, endorsement, or offer by me or any third
party service provider to buy or sell any securities or other financial
instruments.
