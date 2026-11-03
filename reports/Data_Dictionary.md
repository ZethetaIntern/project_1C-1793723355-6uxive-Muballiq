# Data Dictionary

## FactSignals / FactMarketData
- SignalID: unique signal row ID.
- DateTime: timestamp of hourly candle.
- PairID / PairName: currency-pair identifiers.
- Open, High, Low, Close, Volume, Spread: supplied market fields.
- Return_1/5/10/20/60: close returns over bar lags.
- EMA_10, EMA_50, SMA_20: trend indicators.
- RSI_14, MACD, MACD_Signal, MACD_Hist: momentum indicators.
- BB_Upper, BB_Lower, BB_pctB, BB_BW: Bollinger measures.
- ATR_14, Volatility_20, Volume_Ratio: risk/activity features.
- Is_London, Is_NY, Is_Overlap: hour-derived session flags.
- TA_Score, TA_Signal: weighted rule-based technical output.
- ML_Prob_Up, ML_Signal: Random Forest output.
- RL_Action, RL_Signal: Q-learning action mapped to a signal.
- Final_Signal: consensus signal.
- Confidence: heuristic score, not calibrated probability.
- DateKey: YYYYMMDD date key.

## FactTrades
TradeID, PairID, PairName, StrategyName, SignalType, Direction, EntryPrice, ExitPrice, EntryDateTime, ExitDateTime, PositionSize, PnL, PnL_Pips, HoldingDays, Commission, IsOpen, DateKey.

## FactMonteCarlo
ScenarioID, ParallelShift, VolShock, CorrShock, EURUSD_PnL, USDJPY_PnL, GBPUSD_PnL, PortfolioPnL.

## Dimensions
- DimCurrencyPair: PairID, PairName, BaseCurrency, QuoteCurrency, Region.
- DimDate: DateKey, Date, Year, Quarter, Month, MonthName, DayOfWeek.
- DimStrategy: StrategyID, StrategyName.
- DimSession: Session, SessionSort.
