
from pathlib import Path
import json, pandas as pd, streamlit as st
import plotly.express as px
ROOT=Path(__file__).resolve().parent
D=ROOT/"data/processed"
st.set_page_config(page_title="FX Signal Lab",page_icon="📈",layout="wide")
st.title("📈 FX Signal Lab | Multi-Pair Research & Simulation")
st.caption("Historical-data research prototype • Paper trading only • Not investment advice")
required=["FactSignals.csv","FactTrades.csv","FactMonteCarlo.csv","Backtest.csv"]
if not all((D/f).exists() for f in required):
    st.error("Processed files missing. Run: python src/pipeline.py"); st.stop()
sig=pd.read_csv(D/"FactSignals.csv",parse_dates=["DateTime"])
trades=pd.read_csv(D/"FactTrades.csv",parse_dates=["EntryDateTime","ExitDateTime"])
mc=pd.read_csv(D/"FactMonteCarlo.csv")
bt=pd.read_csv(D/"Backtest.csv",parse_dates=["DateTime"])
pairs=sorted(sig.PairName.unique())
pair=st.sidebar.selectbox("Currency pair",["All"]+pairs)
if pair!="All":
    sig=sig[sig.PairName==pair]; bt=bt[bt.PairName==pair]
c1,c2,c3,c4=st.columns(4)
c1.metric("Signals",f"{len(sig):,}")
c2.metric("BUY",int(sig.Final_Signal.isin(["BUY","STRONG_BUY"]).sum()))
c3.metric("SELL",int(sig.Final_Signal.isin(["SELL","STRONG_SELL"]).sum()))
c4.metric("Latest signal",str(sig.sort_values("DateTime").Final_Signal.iloc[-1]))
st.subheader("Signal monitoring")
left,right=st.columns([1.4,1])
with left:
    fig=px.line(sig.sort_values("DateTime"),x="DateTime",y="Close",title="Close price")
    st.plotly_chart(fig,use_container_width=True)
with right:
    counts=sig.Final_Signal.value_counts().rename_axis("Signal").reset_index(name="Count")
    st.plotly_chart(px.pie(counts,names="Signal",values="Count",title="Signal mix"),use_container_width=True)
st.subheader("Latest signal details")
cols=["DateTime","PairName","Close","TA_Score","ML_Prob_Up","TA_Signal","ML_Signal","RL_Signal","Final_Signal","Confidence"]
st.dataframe(sig.sort_values("DateTime",ascending=False)[cols].head(30),use_container_width=True)
st.subheader("Paper backtest")
bt=bt.sort_values("DateTime")
if len(bt):
    st.plotly_chart(px.line(bt,x="DateTime",y="EquityCurve",title="Illustrative equity curve (starting capital 100,000)"),use_container_width=True)
    st.metric("Ending equity",f"{bt.EquityCurve.iloc[-1]:,.2f}")
st.subheader("Historical trade log")
t1,t2,t3=st.columns(3)
t1.metric("Closed trades",len(trades))
t2.metric("Win rate",f"{(trades.PnL>0).mean():.1%}")
t3.metric("Net P&L",f"{trades.PnL.sum():,.2f}")
st.dataframe(trades.sort_values("EntryDateTime",ascending=False).head(30),use_container_width=True)
st.subheader("Monte Carlo portfolio risk")
r=json.loads((D/"risk_summary.json").read_text())
a,b,c,d=st.columns(4)
a.metric("Scenarios",r["scenario_count"]); b.metric("95% VaR loss",f"{r['var_95_loss']:,.0f}")
c.metric("95% CVaR loss",f"{r['cvar_95_loss']:,.0f}"); d.metric("Worst scenario",f"{r['worst_pnl']:,.0f}")
st.plotly_chart(px.histogram(mc,x="PortfolioPnL",nbins=45,title="Monte Carlo portfolio P&L distribution"),use_container_width=True)
st.info("Dataset scope: the supplied OHLCV file contains 500 hourly EUR/USD bars. The separate trade log contains 150 historical/sample trades across five pairs; the Monte Carlo file contains 1,000 portfolio scenarios. No live feed is connected.")
