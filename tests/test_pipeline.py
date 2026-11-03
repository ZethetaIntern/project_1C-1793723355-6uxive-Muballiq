from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def test_expected_outputs_exist():
    for name in ["FactSignals.csv","FactTrades.csv","FactMonteCarlo.csv","DimCurrencyPair.csv","DimDate.csv","Backtest.csv"]:
        assert (ROOT/"data/processed"/name).exists()
def test_signal_output_has_expected_values():
    df=pd.read_csv(ROOT/"data/processed/FactSignals.csv")
    assert len(df)==440
    assert set(df.Final_Signal.unique()).issubset({"STRONG_BUY","BUY","HOLD","SELL","STRONG_SELL"})
def test_pair_dimension_covers_trade_pairs():
    dim=pd.read_csv(ROOT/"data/processed/DimCurrencyPair.csv")
    trades=pd.read_csv(ROOT/"data/processed/FactTrades.csv")
    assert set(trades.PairName).issubset(set(dim.PairName))
def test_monte_carlo_count():
    df=pd.read_csv(ROOT/"data/processed/FactMonteCarlo.csv")
    assert len(df)==1000
