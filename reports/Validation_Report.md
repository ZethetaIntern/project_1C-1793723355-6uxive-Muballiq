# Validation Report

## Run status
- Pipeline executed successfully using the three supplied CSV files.
- Price input: 500 rows, one pair (EUR/USD), no missing values in supplied columns.
- Feature output: 440 rows after rolling-window warm-up.
- Trade log: 150 rows, all marked closed in the supplied file.
- Monte Carlo: 1,000 scenarios.

## Model evaluation
- Random Forest chronological holdout: 88 observations.
- Holdout accuracy: 46.59%.
- Interpretation: this is a weak baseline result and is not evidence of a tradable predictive edge.
- RL policy: Q-learning policy generated and serialized; no claim of out-of-sample profitability is made.

## Supplied trade-log summary
- Win rate: 56.0%.
- Total P&L: 1,915.00.
- Average P&L: 12.77.
- Profit factor: 1.03.

## Supplied Monte Carlo summary
- 95% VaR loss: 165,865.70.
- 95% CVaR loss: 198,183.87.
- Worst scenario P&L: -269,801.36.
- Best scenario P&L: 375,103.83.

## Known caveats
The input OHLCV has only EUR/USD, while the trade log includes five pairs. These tables must remain separate for attribution. Monte Carlo scenarios are supplied stress scenarios and were not recalibrated from OHLCV. No live data or broker execution is implemented.
