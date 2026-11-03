# Power BI Implementation Guide

## Import
Import these CSVs from `data/processed/`: FactSignals, FactMarketData, FactTrades, FactMonteCarlo, Backtest, DimCurrencyPair, DimDate, DimStrategy, DimSession. Set DateTime/Date fields to Date/Time and numeric fields to Decimal Number.

## Relationships
- DimCurrencyPair[PairID] 1:* FactSignals[PairID]
- DimCurrencyPair[PairID] 1:* FactMarketData[PairID]
- DimCurrencyPair[PairID] 1:* FactTrades[PairID]
- DimDate[DateKey] 1:* FactSignals[DateKey]
- DimDate[DateKey] 1:* FactMarketData[DateKey]
- DimDate[DateKey] 1:* FactTrades[DateKey]
- DimDate[DateKey] 1:* Backtest[DateKey]
- DimStrategy[StrategyName] 1:* FactTrades[StrategyName]
Use single-direction filtering from dimensions to facts. FactMonteCarlo is a portfolio-scenario fact and has no pair dimension key.

## Six report pages
1. **Signal Overview:** KPI cards for Total Signals, Buy Signals, Sell Signals, Average Confidence, Latest Close; signal count by pair and trend line.
2. **Pair Analysis:** Pair slicer, close-price trend, TA score, RSI and signal mix.
3. **Strategy Performance:** Total Trade PnL, Win Rate, Profit Factor, Gross Profit/Loss, strategy and direction breakdown.
4. **Risk Management:** Monte Carlo VaR 95, CVaR 95, worst/best scenario, portfolio P&L histogram.
5. **Session Analysis:** London/New York/overlap counts and signal mix by session flags.
6. **Backtest & Model Validation:** Equity curve, backtest hit ratio, return volatility and Random Forest holdout accuracy (from model_metrics.json).

## DAX
Open `FX_Signal_Lab_DAX_Measures.dax` and create measures in Power BI (Modeling > New measure). The complete catalog is also available as a CSV. The file contains 175 measures.

## Validation
Compare Power BI cards with `trade_summary.json` and `risk_summary.json`. Check that date slicers filter all date-linked fact tables. Do not compare the historical trade-log P&L with the OHLCV signal backtest as if they were the same set of trades.
