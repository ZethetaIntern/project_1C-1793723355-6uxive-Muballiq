# Independent R summary of the supplied Monte Carlo scenarios
args <- commandArgs(trailingOnly=TRUE)
input <- if (length(args)>=1) args[1] else "data/input/mc_scenarios.csv"
output <- if (length(args)>=2) args[2] else "data/processed/r_monte_carlo_summary.csv"
mc <- read.csv(input)
p <- mc$PortfolioPnL
q05 <- as.numeric(quantile(p, 0.05, na.rm=TRUE))
summary <- data.frame(
  ScenarioCount=length(p),
  MeanPnL=mean(p, na.rm=TRUE),
  MedianPnL=median(p, na.rm=TRUE),
  VaR95Loss=-q05,
  CVaR95Loss=-mean(p[p <= q05], na.rm=TRUE),
  WorstPnL=min(p, na.rm=TRUE),
  BestPnL=max(p, na.rm=TRUE)
)
write.csv(summary, output, row.names=FALSE)
print(summary)
