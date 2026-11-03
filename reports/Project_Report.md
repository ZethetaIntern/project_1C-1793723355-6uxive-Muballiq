# FX Signal Lab — Final Project Report

## Executive summary
FX Signal Lab is a reproducible research prototype for generating multi-indicator Forex signals and evaluating them in a paper-trading environment. It combines technical analysis, a Random Forest classifier, a tabular Q-learning policy, a consensus layer, a transparent backtest, Monte Carlo portfolio risk analysis and a Power BI semantic model.

The project follows the supplied Zetheta brief's core framing: Meridian FX Capital is a fictional trading firm and FX Signal Lab is its multi-currency signal research platform. The brief calls for reinforcement learning, technical analysis, machine learning, risk decomposition and performance attribution. This implementation delivers those components with the uploaded sample datasets and explicitly documents data coverage limits.

## 1. Business problem and objectives
FX markets operate across global sessions and currency pairs. Analysts need a repeatable workflow to combine trend, momentum and volatility signals, quantify uncertainty, compare strategy behaviour and communicate results to trading and risk stakeholders. The objective is not to promise profitable trades. It is to create an auditable analytical workflow that can be tested, challenged and extended.

Objectives:
1. Clean and validate the supplied OHLCV, trade-log and Monte Carlo files.
2. Calculate momentum, trend, volatility and session features.
3. Produce weighted TA signals.
4. Train a supervised direction classifier using a time-ordered split.
5. Train a reinforcement-learning policy in a simplified market environment.
6. Combine component outputs into a final research signal.
7. Estimate strategy behaviour after a simple spread cost.
8. Summarise tail risk using the supplied Monte Carlo scenarios.
9. Expose results in Streamlit and Power BI.

## 2. Dataset inventory and scope
| File | Rows | Use |
|---|---:|---|
| forex_price_data.csv | 500 | Hourly OHLCV; EUR/USD only |
| trade_log.csv | 150 | Closed historical/sample trades across five pairs |
| mc_scenarios.csv | 1,000 | Portfolio-level stress/scenario P&L |

The OHLCV sample spans 2023-01-01 00:00 through 2023-01-21 19:00. It contains EUR/USD only. The trade log contains EUR/USD, GBP/USD, USD/JPY, USD/INR and AUD/USD records. The Monte Carlo file contains pair-level P&L columns for EUR/USD, USD/JPY and GBP/USD plus portfolio P&L. The project does not synthesize missing OHLCV for pairs that are not present.

## 3. Data preparation and quality
The pipeline parses timestamps, orders bars chronologically, computes rolling features, removes rows where feature windows are incomplete, and writes normalized analytical tables. The input CSV files are preserved unchanged under `data/input/`. The processed feature table contains 440 eligible rows after rolling-window warm-up. The target is next-bar direction and the model uses a chronological 80/20 split to avoid random shuffling across time.

## 4. Feature engineering
The pipeline calculates:
- Returns over 1, 5, 10, 20 and 60 bars.
- EMA 10 and EMA 50 for trend direction.
- RSI 14 for momentum.
- MACD, MACD signal and histogram.
- Bollinger upper/lower bands, percent-B and bandwidth.
- ATR 14 and annualised rolling volatility.
- Volume ratio and London, New York and overlap session flags.

All indicators are derived from the supplied OHLCV columns. The data are hourly, so the return feature names in code refer to bars rather than calendar days.

## 5. Technical-analysis signal engine
The composite TA score uses a weighted vote:
- EMA trend crossover: 25%.
- RSI extreme condition: 20%.
- MACD histogram sign: 20%.
- Bollinger breakout/reversion condition: 15%.
- Price relative to the 20-bar average: 20%.

Scores are mapped to STRONG_BUY, BUY, HOLD, SELL or STRONG_SELL using thresholds. The score is a rule-based research feature, not a probability of profit.

## 6. Supervised machine learning
A Random Forest classifier predicts whether the next close is above the current close. It uses the engineered return, momentum, volatility, volume and session features. The training sample is the first 80% of eligible rows; the final 20% is held out chronologically. The model is saved as `models/random_forest.joblib`.

Observed holdout accuracy on this small supplied sample: **46.6%** (88 holdout rows). This is below a level that would justify deployment. It is reported honestly as a baseline diagnostic, not a successful trading edge. A larger, multi-regime dataset and walk-forward testing are required.

## 7. Reinforcement-learning component
A compact tabular Q-learning agent learns an action policy over discretized trend, RSI and volatility states. Actions are FLAT, LONG and SHORT. Reward is the next-bar directional return scaled for readability, less a penalty when the position changes. The policy is trained over repeated passes through the historical sequence with exploration and a discount factor.

This is a lightweight RL baseline rather than PPO. The supplied OHLCV sample has only 500 rows, so a small tabular implementation is easier to inspect and reproduce. The original brief describes PPO/DQN/A2C examples; a PPO implementation should be considered only after acquiring substantially more data and validating a Gymnasium-compatible environment.

## 8. Consensus signal
The final layer combines TA, ML and RL:
- A strong directional consensus produces STRONG_BUY or STRONG_SELL.
- A strong TA vote with no opposing ML vote can produce BUY or SELL.
- Otherwise the output is HOLD.

Confidence is a transparent heuristic built from TA score magnitude and distance of the ML probability from 0.5. It is not a calibrated probability. It should not be interpreted as the chance that a trade will be profitable.

## 9. Backtesting approach
The paper backtest maps final signals to long, short or flat positions. Strategy return is the position multiplied by the next-bar close-to-close return, less a spread-based turnover penalty when the position changes. The output includes equity curve, gross return, cost return and net strategy return.

Limitations: the supplied file has OHLC bars and a spread field, but no executable bid/ask quotes, order book, financing/swap, market impact or broker fills. The simplified cost approximation is not a production FX execution model. The result is an educational illustration only.

## 10. Trade-log analysis
The supplied trade log has 150 records and is kept separate from the OHLCV backtest. Summary statistics:
- Win rate: **56.0%**
- Total P&L: **1,915.00** (source currency/unit as supplied; no currency conversion assumed)
- Average P&L: **12.77**
- Profit factor: **1.03**

The trade log is sample history, not generated fills from the signal engine. The source data does not provide enough context to assert that the historical trades were executed by this model.

## 11. Monte Carlo risk analysis
The supplied scenario file contains 1,000 portfolio P&L scenarios. Results:
- Mean scenario P&L: **4,871.34**
- Median scenario P&L: **1,472.13**
- 95% VaR loss: **165,865.70**
- 95% CVaR loss: **198,183.87**
- Worst scenario: **-269,801.36**
- Best scenario: **375,103.83**

VaR is reported as the positive magnitude of the 5th percentile loss. CVaR is the average loss in scenarios at or below that percentile. These figures inherit the assumptions and units of the supplied Monte Carlo file; they are not independently calibrated forecasts.

## 12. Power BI semantic model
The model contains FactSignals, FactMarketData, FactTrades and FactMonteCarlo, plus DimCurrencyPair, DimDate, DimStrategy and DimSession. Recommended one-to-many relationships:
- DimCurrencyPair[PairID] → FactSignals[PairID] and FactMarketData[PairID].
- DimCurrencyPair[PairName] → FactTrades[PairName] (or add a PairID key to FactTrades during ingestion).
- DimDate[DateKey] → FactSignals[DateKey], FactMarketData[DateKey], Backtest[DateKey] and FactTrades[DateKey].
- DimStrategy[StrategyName] → FactTrades[StrategyName].
- DimSession[Session] can be used as a disconnected slicer unless a session key is added to facts.

The DAX library contains **175 measures** covering signal counts, confidence, trade P&L, win rate, profit factor, pair attribution, time intelligence, backtest behaviour and Monte Carlo risk. See `powerbi/PowerBI_Guide.md`.

## 13. Dashboard design
Six suggested Power BI pages:
1. Signal Overview — signal counts, confidence, latest signal, pair and date slicers.
2. Pair Analysis — pair-level signal mix, price and indicator comparison.
3. Strategy Performance — P&L, win rate, profit factor, long/short attribution.
4. Risk Management — VaR, CVaR, scenario distribution and drawdown indicators.
5. Session Analysis — London, New York and overlap signal frequency.
6. Backtest & Model Validation — equity curve, holdout accuracy and strategy return diagnostics.

The included Streamlit application provides an immediately runnable operational view of the processed outputs. A native `.pbix` is not included because Power BI Desktop's proprietary project authoring format is not generated in this Python runtime; the CSV model tables, DAX library and build guide are included for import into Power BI Desktop.

## 14. System workflow
1. Place source files in `data/input/`.
2. Run `python src/pipeline.py`.
3. Inspect processed tables and JSON summaries in `data/processed/`.
4. Run `streamlit run app.py` for the local dashboard.
5. Import processed CSVs into Power BI Desktop.
6. Create relationships from the model guide.
7. Add measures from the DAX file and build the six pages.
8. Validate totals against the JSON summaries.

## 15. Testing and validation
The pipeline has been executed successfully against the uploaded files. It produced 440 feature-complete rows, 150 trade records, 1,000 Monte Carlo scenarios and the Power BI dimension/fact exports. A basic automated test suite checks data presence, row counts and output schema. The numerical model result is intentionally reported without overclaiming predictive value.

## 16. Security, ethics and responsible use
No credentials, broker API keys or account details are required. The application does not submit orders. Do not connect it to a funded brokerage account. Currency trading is leveraged and can result in rapid losses. Use the project for learning, analysis and demo trading only.

## 17. Known limitations and next steps
- OHLCV data coverage is only EUR/USD and only 500 hourly bars.
- ML holdout accuracy is approximately 46.6%; it does not demonstrate predictive edge.
- RL is tabular Q-learning, not PPO, and has not been validated across market regimes.
- The trade log has unknown base currency semantics and is not joined to signal-generated fills.
- Monte Carlo scenarios are supplied rather than calibrated from the OHLCV sample.
- Transaction cost modelling is simplified.
- Confidence is heuristic, not calibrated.
- No live market feed, broker execution, alerting or order management exists.

Recommended next steps are to collect several years of clean hourly/daily OHLCV for all target pairs, use walk-forward validation, include bid/ask and swap costs, run ablation tests, compare PPO/DQN against simple baselines, calibrate confidence, add position limits and run a paper-trading trial before considering any production use.

## 18. Conclusion
FX Signal Lab demonstrates an end-to-end analytical architecture for multi-source FX research: feature engineering, technical signals, supervised learning, reinforcement learning, backtesting, portfolio stress analysis and BI reporting. The implementation is reproducible and transparent about where the sample data do not support stronger conclusions.
