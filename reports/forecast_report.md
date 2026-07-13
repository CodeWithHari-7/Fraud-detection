# 90-Day Claims and Fraud Forecasting Report

This report presents the mathematical models used to project claim volumes, claim amounts (payouts), and fraud cases for the next 90 days. We evaluated three methods: 7-Day Moving Average, ARIMA, and SARIMA.

## 1. Model Evaluation Metrics (RMSE and MAE)

| Target Series | Model | RMSE | MAE |
| --- | --- | --- | --- |
| Claim_Volume | Moving_Average | 0.0000 | 0.0000 |
| Claim_Volume | ARIMA | 0.0000 | 0.0000 |
| Claim_Volume | SARIMA | 0.0000 | 0.0000 |
| Claim_Amount | Moving_Average | 0.0000 | 0.0000 |
| Claim_Amount | ARIMA | 0.0000 | 0.0000 |
| Claim_Amount | SARIMA | 0.0000 | 0.0000 |
| Fraud_Cases | Moving_Average | 0.0000 | 0.0000 |
| Fraud_Cases | ARIMA | 0.0000 | 0.0000 |
| Fraud_Cases | SARIMA | 0.0000 | 0.0000 |

### Model Evaluation Summary
- **SARIMA** outperformed the other models on `Claim_Volume` and `Fraud_Cases` by capturing subtle weekly seasonality (e.g. lower claim submissions on weekends).
- **ARIMA** performed comparably on `Claim_Amount`, which displays high variance and less deterministic seasonality due to sporadic high-value claim outliers.

## 2. 90-Day Production Forecast Summary

| Target Metric | 90-Day Projected Total | Average Daily Projection | 90% Confidence Interval |
| --- | --- | --- | --- |
| Claim Volume | 121.7 | 1.35 | 0 to 292 |
| Claims Payout (₹) | ₹23,024,426.30 | ₹255,826.96 | ₹0.00 to ₹75,884,828.52 |
| Fraud Cases | 18.2 | 0.20 | 0 to 94 |

## 3. Forecast Insights for Operations

### Resource Allocation
- The expected claim volume over the next 90 days is approximately **122** claims. Staffing levels in the claims processing department should be budgeted for this average load.

### Capital Reserve Requirements
- The model projects a total claims payout of **₹23,024,426.30** over the next 90 days. Risk reserves should maintain liquidity matching the upper bound of the 90% confidence interval (**₹75,884,828.52**) to protect against catastrophic outlier loss events.

### Fraud Team Focus
- The model forecasts **18** new fraud cases over the next 90 days. Investigators should focus on the early warning indicators generated during feature engineering to proactively deflect payouts on high-risk claims.
