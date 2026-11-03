
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import TimeSeriesSplit
import joblib, json

ROOT = Path(__file__).resolve().parents[1]
INP, OUT, MODELS = ROOT/"data/input", ROOT/"data/processed", ROOT/"models"
OUT.mkdir(exist_ok=True); MODELS.mkdir(exist_ok=True)

def rsi(s, n=14):
    d=s.diff(); g=d.clip(lower=0).rolling(n).mean(); l=(-d.clip(upper=0)).rolling(n).mean()
    return 100 - 100/(1+g/l.replace(0,np.nan))
def add_features(df):
    x=df.sort_values("DateTime").copy()
    x["DateTime"]=pd.to_datetime(x["DateTime"])
    x["Return_1"]=x.Close.pct_change()
    for n in [5,10,20,60]:
        x[f"Return_{n}"]=x.Close.pct_change(n)
    x["EMA_10"]=x.Close.ewm(span=10,adjust=False).mean()
    x["EMA_50"]=x.Close.ewm(span=50,adjust=False).mean()
    x["SMA_20"]=x.Close.rolling(20).mean()
    x["RSI_14"]=rsi(x.Close)
    ef=x.Close.ewm(span=12,adjust=False).mean(); es=x.Close.ewm(span=26,adjust=False).mean()
    x["MACD"]=ef-es; x["MACD_Signal"]=x.MACD.ewm(span=9,adjust=False).mean()
    x["MACD_Hist"]=x.MACD-x.MACD_Signal
    mid=x.Close.rolling(20).mean(); sd=x.Close.rolling(20).std()
    x["BB_Upper"]=mid+2*sd; x["BB_Lower"]=mid-2*sd
    x["BB_pctB"]=(x.Close-x.BB_Lower)/(x.BB_Upper-x.BB_Lower)
    x["BB_BW"]=(x.BB_Upper-x.BB_Lower)/mid
    prev=x.Close.shift()
    tr=pd.concat([x.High-x.Low,(x.High-prev).abs(),(x.Low-prev).abs()],axis=1).max(axis=1)
    x["ATR_14"]=tr.rolling(14).mean()
    x["Volatility_20"]=x.Return_1.rolling(20).std()*np.sqrt(24*365)
    x["Volume_Ratio"]=x.Volume/x.Volume.rolling(20).mean()
    x["Hour"]=x.DateTime.dt.hour
    x["Is_London"]=x.Hour.between(8,16).astype(int)
    x["Is_NY"]=x.Hour.between(13,21).astype(int)
    x["Is_Overlap"]=x.Hour.between(13,16).astype(int)
    return x

def composite_signal(x):
    score=np.zeros(len(x))
    score += np.where(x.EMA_10>x.EMA_50, .25, -.25)
    score += np.where(x.RSI_14<30,.20,np.where(x.RSI_14>70,-.20,0))
    score += np.where(x.MACD_Hist>0,.20,-.20)
    score += np.where(x.Close<x.BB_Lower,.15,np.where(x.Close>x.BB_Upper,-.15,0))
    score += np.where(x.Close>x.SMA_20,.20,-.20)
    x["TA_Score"]=score
    x["TA_Signal"]=np.select([score>=.4,score>=.2,score<=-.4,score<=-.2],
        ["STRONG_BUY","BUY","STRONG_SELL","SELL"],default="HOLD")
    return x

def qlearn_agent(x, episodes=35, alpha=.12, gamma=.95, eps=.15):
    # Compact tabular Q-learning policy over trend/RSI/volatility states.
    z=x.copy()
    z["TrendState"]=np.where(z.EMA_10>z.EMA_50,1,0)
    z["RSIState"]=pd.cut(z.RSI_14,[-np.inf,30,70,np.inf],labels=[0,1,2]).astype(float)
    z["VolState"]=pd.qcut(z.Volatility_20.rank(method="first"),3,labels=False,duplicates="drop")
    z[["RSIState","VolState"]]=z[["RSIState","VolState"]].fillna(1)
    q={}
    def state(i): return (int(z.TrendState.iloc[i]),int(z.RSIState.iloc[i]),int(z.VolState.iloc[i]))
    n=len(z)
    if n<30: return np.array([0]*n),q
    rng=np.random.default_rng(42)
    for _ in range(episodes):
        pos=0
        for i in range(25,n-1):
            s=state(i); q.setdefault(s,np.zeros(3))
            a=int(rng.integers(3)) if rng.random()<eps else int(np.argmax(q[s]))
            newpos={0:0,1:1,2:-1}[a]
            ret=(z.Close.iloc[i+1]/z.Close.iloc[i]-1)
            reward=(newpos*ret*10000)- (0.15*abs(newpos-pos))
            ns=state(i+1); q.setdefault(ns,np.zeros(3))
            q[s][a]+=alpha*(reward+gamma*np.max(q[ns])-q[s][a])
            pos=newpos
    acts=[]
    for i in range(n):
        s=state(i) if i>=25 else (0,1,1)
        acts.append(int(np.argmax(q.get(s,np.zeros(3)))))
    return np.array(acts),q

def run():
    raw=pd.read_csv(INP/"forex_price_data.csv")
    x=add_features(raw)
    x=composite_signal(x)
    feat=["Return_1","Return_5","Return_10","Return_20","Return_60","RSI_14","MACD_Hist","BB_pctB","BB_BW","ATR_14","Volatility_20","Volume_Ratio","Is_London","Is_NY","Is_Overlap"]
    x["Target"]=(x.Close.shift(-1)>x.Close).astype(int)
    clean=x.dropna(subset=feat).copy()
    # Chronological holdout; never shuffle time series.
    split=max(int(len(clean)*.8),1)
    train,test=clean.iloc[:split],clean.iloc[split:]
    ml_signal=pd.Series(index=clean.index,dtype="object")
    metrics={}
    if len(train)>30 and len(test)>5 and train.Target.nunique()>1:
        rf=RandomForestClassifier(n_estimators=250,max_depth=6,min_samples_leaf=3,class_weight="balanced",random_state=42)
        rf.fit(train[feat],train.Target)
        pred=rf.predict(test[feat])
        prob=rf.predict_proba(clean[feat])[:,list(rf.classes_).index(1)]
        clean["ML_Prob_Up"]=prob
        clean["ML_Signal"]=np.select([prob>=.58,prob<=.42],["BUY","SELL"],default="HOLD")
        metrics={"holdout_accuracy":float(accuracy_score(test.Target,pred)),"train_rows":len(train),"test_rows":len(test),"features":feat}
        joblib.dump(rf,MODELS/"random_forest.joblib")
    else:
        clean["ML_Prob_Up"]=.5; clean["ML_Signal"]="HOLD"
        metrics={"holdout_accuracy":None,"note":"Insufficient rows/classes for a reliable holdout classifier."}
    actions,q=qlearn_agent(clean)
    clean["RL_Action"]=pd.Series(actions,index=clean.index).map({0:"FLAT",1:"LONG",2:"SHORT"})
    clean["RL_Signal"]=clean.RL_Action.map({"FLAT":"HOLD","LONG":"BUY","SHORT":"SELL"})
    clean["Final_Signal"]=np.select([
        (clean.TA_Score>=.2)&(clean.ML_Signal=="BUY")&(clean.RL_Signal=="BUY"),
        (clean.TA_Score<=-.2)&(clean.ML_Signal=="SELL")&(clean.RL_Signal=="SELL"),
        (clean.TA_Score>=.4)&(clean.ML_Signal!="SELL"),
        (clean.TA_Score<=-.4)&(clean.ML_Signal!="BUY")
    ],["STRONG_BUY","STRONG_SELL","BUY","SELL"],default="HOLD")
    clean["Confidence"]=np.clip(.45+.35*np.abs(clean.TA_Score)+.2*np.abs(clean.ML_Prob_Up-.5)*2,0,1)
    clean["SignalID"]=np.arange(1,len(clean)+1)
    clean["DateKey"]=clean.DateTime.dt.strftime("%Y%m%d").astype(int)
    clean["PairID"]=clean.PairID.astype(int)
    clean.to_csv(OUT/"FactSignals.csv",index=False)
    clean.to_csv(OUT/"FactMarketData.csv",index=False)
    # Transparent one-bar-ahead paper backtest, position changes charged spread each change.
    bt=clean.copy()
    pos=bt.Final_Signal.map({"STRONG_BUY":1,"BUY":1,"STRONG_SELL":-1,"SELL":-1,"HOLD":0}).fillna(0)
    bt["Position"]=pos
    bt["NextReturn"]=bt.Close.pct_change().shift(-1)
    bt["GrossReturn"]=bt.Position*bt.NextReturn
    bt["CostReturn"]=(bt.Position!=bt.Position.shift()).astype(int)*(bt.Spread/10000)
    bt["StrategyReturn"]=bt.GrossReturn-bt.CostReturn
    bt["EquityCurve"]=(1+bt.StrategyReturn.fillna(0)).cumprod()*100000
    bt["BacktestPnL"]=bt.StrategyReturn.fillna(0)*100000
    bt.to_csv(OUT/"Backtest.csv",index=False)
    # Input trade log and MC scenario data are retained and normalized for Power BI.
    trades=pd.read_csv(INP/"trade_log.csv")
    trades["EntryDateTime"]=pd.to_datetime(trades.EntryDateTime)
    trades["ExitDateTime"]=pd.to_datetime(trades.ExitDateTime)
    trades["DateKey"]=trades.EntryDateTime.dt.strftime("%Y%m%d").astype(int)
    trades["TradeID"]=trades.TradeID.astype(int)
    pair_dim=pd.read_csv(OUT/"DimCurrencyPair.csv")
    known=set(pair_dim.PairName)
    for pair_name in sorted(set(trades.PairName)-known):
        new_id=int(pair_dim.PairID.max())+1 if len(pair_dim) else 1
        pair_dim.loc[len(pair_dim)]={"PairID":new_id,"PairName":pair_name,
            "BaseCurrency":pair_name.split("/")[0],"QuoteCurrency":pair_name.split("/")[1],
            "Region":"Asian EM" if pair_name=="USD/INR" else "G10 / Major"}
    pair_map=dict(zip(pair_dim.PairName,pair_dim.PairID))
    trades["PairID"]=trades.PairName.map(pair_map).astype(int)
    pair_dim.to_csv(OUT/"DimCurrencyPair.csv",index=False)
    trades.to_csv(OUT/"FactTrades.csv",index=False)
    # Shared date dimension spans both the price history and the supplied trade log.
    all_dates=pd.date_range(min(clean.DateTime.min().date(),trades.EntryDateTime.min().date()),
                            max(clean.DateTime.max().date(),trades.EntryDateTime.max().date()),freq="D")
    dates=pd.DataFrame({"Date":all_dates})
    dates["DateKey"]=dates.Date.dt.strftime("%Y%m%d").astype(int)
    dates["Year"]=dates.Date.dt.year; dates["Quarter"]="Q"+dates.Date.dt.quarter.astype(str)
    dates["Month"]=dates.Date.dt.month; dates["MonthName"]=dates.Date.dt.month_name()
    dates["DayOfWeek"]=dates.Date.dt.day_name()
    dates.to_csv(OUT/"DimDate.csv",index=False)
    mc=pd.read_csv(INP/"mc_scenarios.csv")
    mc.to_csv(OUT/"FactMonteCarlo.csv",index=False)
    strategies=pd.DataFrame({"StrategyName":sorted(trades.StrategyName.unique())})
    strategies["StrategyID"]=np.arange(1,len(strategies)+1)
    strategies.to_csv(OUT/"DimStrategy.csv",index=False)
    sessions=pd.DataFrame({"Session":["Asia","London","New York","London-New York Overlap","Other"],"SessionSort":[1,2,3,4,5]})
    sessions.to_csv(OUT/"DimSession.csv",index=False)
    # Risk summary from supplied Monte Carlo scenarios.
    p=mc.PortfolioPnL
    risk={"scenario_count":len(mc),"mean_pnl":float(p.mean()),"median_pnl":float(p.median()),
          "var_95_loss":float(-p.quantile(.05)),"cvar_95_loss":float(-p[p<=p.quantile(.05)].mean()),
          "worst_pnl":float(p.min()),"best_pnl":float(p.max())}
    trade_summary={"trade_count":len(trades),"win_rate":float((trades.PnL>0).mean()),
                   "total_pnl":float(trades.PnL.sum()),"avg_pnl":float(trades.PnL.mean()),
                   "profit_factor":float(trades.loc[trades.PnL>0,"PnL"].sum()/abs(trades.loc[trades.PnL<0,"PnL"].sum()))}
    (OUT/"model_metrics.json").write_text(json.dumps(metrics,indent=2))
    (OUT/"risk_summary.json").write_text(json.dumps(risk,indent=2))
    (OUT/"trade_summary.json").write_text(json.dumps(trade_summary,indent=2))
    (MODELS/"q_learning_policy.json").write_text(json.dumps({str(k):v.tolist() for k,v in q.items()},indent=2))
    print("Pipeline complete",len(clean),metrics,risk,trade_summary)
if __name__=="__main__": run()
