# FX Signal Lab — Forex Trading Signal Research Project

**Project type:** quantitative-finance research and paper-trading simulation  
**Organization scenario:** Meridian FX Capital (fictional)  
**Stack:** Python, pandas, NumPy, scikit-learn, tabular Q-learning, Streamlit, Plotly, Power BI / DAX

## 1. What is included
- Multi-indicator technical analysis: EMA crossover, RSI, MACD, Bollinger Bands, ATR, volatility and session flags.
- Weighted technical-analysis score and BUY / SELL / HOLD classifications.
- Random Forest next-bar direction classifier with chronological holdout evaluation.
- Tabular Q-learning agent with LONG / SHORT / FLAT actions and reward based on next-bar return less a turnover penalty.
- Consensus signal layer combining TA, ML and RL votes.
- Illustrative paper backtest with spread-based turnover cost.
- Monte Carlo portfolio risk summary (95% VaR and CVaR) from the supplied scenarios.
- Streamlit dashboard and Power BI-ready fact/dimension CSVs.
- DAX measure library (120 measures), model relationship guide, project report and validation notes.

## 2. Dataset scope and important limitations
The uploaded `forex_price_data.csv` contains **500 hourly EUR/USD candles only** (2023-01-01 to 2023-01-21 19:00). After rolling-indicator warm-up, 440 rows are eligible for signal modelling. It does not contain historical OHLCV for the other pairs.
The uploaded `trade_log.csv` contains 150 closed trades across EUR/USD, GBP/USD, USD/JPY, USD/INR and AUD/USD. It is retained as a separate trade-history fact table; it is not used to fabricate OHLCV for those pairs.
The uploaded `mc_scenarios.csv` contains 1,000 precomputed portfolio scenarios and is used for the portfolio risk page.
This is **not a live trading system**. It has no broker integration, order routing, live quote feed or guaranteed profitability. Historical results and model scores do not predict future returns. Use demo/paper trading only.

## 3. Quick start (Windows)
1. Extract the ZIP.
2. Install Python 3.10 or newer.
3. Double-click `run_project.bat`, or run the commands below in PowerShell:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python src\pipeline.py
   streamlit run app.py
   ```
4. Open the local Streamlit URL shown in the terminal (normally `http://localhost:8501`).

## 4. Quick start (macOS/Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/pipeline.py
streamlit run app.py
```

## 5. Project architecture
`data/input/` contains the original supplied CSVs. `src/pipeline.py` performs feature engineering, TA scoring, model fitting, Q-learning, backtesting, dimension generation and risk calculations. Outputs are written to `data/processed/`. `app.py` reads those outputs and displays the dashboard. `powerbi/` contains DAX measures and a Power BI build guide.

## 6. Reproducibility
The pipeline uses fixed random seeds for the Random Forest and Q-learning exploration. It splits the time series chronologically (80% train / 20% test); it does not shuffle observations. The next-bar target is created from the following close. The reported holdout accuracy is a small-sample research metric, not evidence of a production-ready edge.

## 7. Main outputs
- `FactSignals.csv`, `FactMarketData.csv`, `FactTrades.csv`, `FactMonteCarlo.csv`, `Backtest.csv`
- `DimCurrencyPair.csv`, `DimDate.csv`, `DimStrategy.csv`, `DimSession.csv`
- `model_metrics.json`, `risk_summary.json`, `trade_summary.json`
- `powerbi/FX_Signal_Lab_DAX_Measures.dax` (120 measures)
- `reports/Project_Report.md`, `reports/PowerBI_Guide.md`, `reports/Validation_Report.md`

## 8. Risk controls and interpretation
Signals are research outputs. A production extension should add bid/ask executable prices, realistic per-pair pip values, financing/swap, slippage, event calendars, position limits, stop-loss logic, walk-forward validation, out-of-sample periods and a paper-trading approval process. Never infer that a BUY/SELL label is a recommendation to trade.
