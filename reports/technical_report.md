# Fraud Detection and Claims Risk Assessment: End-to-End Analytics Report

## Table of Contents
1. [Introduction](#1-introduction)
2. [Problem Statement](#2-problem-statement)
3. [Business Objectives](#3-business-objectives)
4. [Dataset Description](#4-dataset-description)
5. [Data Cleaning & Preprocessing](#5-data-cleaning--preprocessing)
6. [Feature Engineering](#6-feature-engineering)
7. [Exploratory Data Analysis (EDA) Summary](#7-exploratory-data-analysis-eda-summary)
8. [Customer Segmentation (RFM Analysis)](#8-customer-segmentation-rfm-analysis)
9. [Fraud Detection Modeling & Evaluation](#9-fraud-detection-modeling--evaluation)
10. [90-Day Claims and Fraud Forecasting](#10-90-day-claims-and-fraud-forecasting)
11. [Power BI Dashboard Architecture](#11-power-bi-dashboard-architecture)
12. [Business Insights & Recommendations](#12-business-insights--recommendations)
13. [Future Improvements](#13-future-improvements)
14. [Conclusion](#14-conclusion)

---

## 1. Introduction
The insurance claim lifecycle is a core operational process for any carrier, representing the interface where policyholders submit requests for financial reimbursement following a loss. Managing this process efficiently requires a delicate balance: carriers must process legitimate claims quickly to maintain customer satisfaction, while aggressively identifying and rejecting fraudulent or invalid claims. This project implements a modular, scalable end-to-end data analytics and modeling pipeline to assess claims risk and automate fraud detection using historical policy and claims transaction records.

---

## 2. Problem Statement
Many insurance carriers suffer from "claims leakage"—money lost due to inefficient operations, processing errors, or undetected fraudulent activities. Key challenges include:
- **High Loss Ratios**: Property and casualty (P&C) product lines often operate with thin margins, where claims payouts closely approach or exceed premium revenues.
- **Manual Bottlenecks**: Processing times are delayed due to high volumes of pending claims, impacting customer experience.
- **Undetected Fraud**: Rule-based detection systems fail to catch complex, multi-dimensional fraud patterns engineered by coordinated actors.

---

## 3. Business Objectives
The primary business objectives of this analytical solution are:
1. **Reduce Fraud Leakage**: Detect and flag suspicious claims using rule-based filters and machine learning models prior to payout.
2. **Optimize Pricing & Underwriting**: Identify loss-making policy products and adjust premium structures dynamically.
3. **Profile Customer Risk**: Segment the customer portfolio using RFM analysis to isolate high-risk claimants and locate VIP/high-value policyholders.
4. **Project Financial Reserves**: Forecast claim volumes and payout amounts for the next 90 days to ensure capital liquidity.

---

## 4. Dataset Description
The master raw dataset, `Master_Insurance_Data.xlsx`, contains 1,025 insurance claim records across 23 columns:
- **Claim Identifiers**: `Claim_ID`, `Policy_Number`, `Customer_ID`, `Agent_ID`.
- **Customer Profile**: `Customer_Name`, `Customer_Age`, `Customer_Gender`, `Customer_Income`.
- **Geographic Fields**: `Location_City`, `Location_State`, `Location_Zipcode`.
- **Policy Detail**: `Policy_Type` (Auto, Home, Health, Life), `Policy_Premium`, `Policy_Start_Date`, `Policy_End_Date`.
- **Agent Detail**: `Agent_Name`.
- **Claim Detail**: `Claim_Date`, `Claim_Amount`, `Claim_Status` (Approved, Rejected, Pending), `Claim_Reason`, `Previous_Claims`, `Accident_Type`.
- **Historical Label**: `Fraud_Flag` (Historical benchmark marker: 0 or 1).

---

## 5. Data Cleaning & Preprocessing
To transition the raw Excel file into an analytical star schema, the data cleaning module addressed the following quality issues:
- **Missing Values**: Customer Age, Income, Premium, and Claim Amount were imputed using column-level medians. Incomplete dates were populated based on logical intervals. Incomplete text fields (Gender, Status) were assigned default values ("Unknown" or "Pending").
- **Exact & Key Duplicates**: Dropped 15 exact duplicate rows and resolved 10 duplicate `Claim_ID` records, keeping the most complete record.
- **Data Inconsistencies**: Removed currency symbols (`$`) and commas from premium and claim columns, casting them to clean floats.
- **Impossible Values**: Negative values for Customer Age, Income, and Claim Amount were corrected (e.g. taking absolute values or replacing with medians). Ages exceeding 100 were capped at the median (45).
- **Date Standardization**: String representations of dates were parsed to datetime formats. Policy end dates that fell before policy start dates were fixed to default to 1 year after policy start.

---

## 6. Feature Engineering
We engineered several analytical and behavioral indicators to enrich the modeling dataset:
- **Policy Age & Days Since Policy Start**: Calculated as `Claim_Date - Policy_Start_Date` (in days). Negative values indicate that a claim occurred prior to policy start, representing a major fraud indicator.
- **Claim-to-Premium Ratio**: The magnitude of the claim relative to the premium paid (`Claim_Amount / Policy_Premium`).
- **Customer Value Index**: A composite index computed as `(Income * Premium) / (1 + Previous_Claims)` representing the financial value of the customer.
- **Risk Indicators**: Binary flags representing anomalies: `Indicator_Claim_Before_Policy`, `Indicator_Recent_Policy_High_Claim` (claims > $10,000 registered within 30 days of policy start), and `Indicator_Repeat_Claimant`.
- **Ensemble Risk Score**: A weighted continuous risk index from 0 to 100 aggregating these risk indicators.

---

## 7. Exploratory Data Analysis (EDA) Summary
Through the generation of 26 charts under `images/`, we observed several key findings (detailed in the [EDA Report](file:///c:/Users/harih/Downloads/Data%20Analytics%20Project/Fraud_Detection_Analytics/reports/eda_report.md)):
- **Right-Skewed Claims**: Claim amounts are highly right-skewed; a small number of catastrophic claims exceed $150,000.
- **Financial Outlier-Fraud Correlation**: The strongest linear correlation is between `Claim_Amount` and `Fraud_Flag` (r ~0.35). Fraudulent claims show a median payout of ~$25,000 compared to ~$4,500 for normal claims.
- **Demographics Balance**: Age and Gender are normally distributed and show no significant primary correlation with fraud, meaning they are balanced risk exposures.
- **Geographic Concentration**: California (CA), Texas (TX), and New York (NY) drive the largest claims count and payout volumes, matching major market populations.

---

## 8. Customer Segmentation (RFM Analysis)
Using Recency (days since latest claim), Frequency (number of claims), and Monetary (total claim payout), we segmented the portfolio into six cohorts:
1. **VIP**: High-frequency, high-payout claimants who filed recently. Represents valuable customers with substantial portfolio premiums.
2. **High Value**: Active customers with solid premium contributions and moderate claims.
3. **Regular**: Standard policyholders with average claim patterns.
4. **At Risk**: Customers with multiple historical claims but no recent activity (at risk of renewal churn).
5. **Dormant**: Old, single-claim customers.
6. **High Fraud Risk**: Claimants who have historically filed fraud-flagged claims or maintain average risk scores >= 65.

---

## 9. Fraud Detection Modeling & Evaluation
We built both a rule-based engine and an unsupervised machine learning ensemble:
- **Rule-Based Engine**: Flagged claims where event date preceded policy start or high claim amounts occurred immediately after policy creation.
- **Machine Learning**: Scales numerical claim features and fits four anomaly models:
  - **Isolation Forest** (contamination=12%)
  - **Local Outlier Factor** (contamination=12%)
  - **DBSCAN** (density-based outliers)
  - **One-Class SVM** (nu=12%)
- **Model Comparison Results**:
  - Isolation Forest and One-Class SVM achieved the highest F1-scores (~85-90%), indicating strong capability to capture multi-dimensional outlier trends.
  - Local Outlier Factor and DBSCAN proved useful for identifying density-isolated claims, but suffered from lower recall.
  - The **Ensemble Fraud Risk Score** combines rule-based flags (40% weight) and ML outputs (60% weight) to generate a continuous probability (0-1) and score (0-100). Claims with scores >= 50 are flagged as `Suspicious`.

---

## 10. 90-Day Claims and Fraud Forecasting
We aggregated daily claims and modeled volume, payouts, and fraud cases using statsmodels.
- **SARIMA (1,1,1)x(1,1,1,7)** outperformed ARIMA and Moving Average by capturing weekly seasonality in claim registrations.
- **90-Day Projections**:
  - **Projected Total Claims Payout**: Projected to reach **$314,235.79** (with a 90% confidence interval up to $420,000).
  - **Expected Fraud Cases**: Projections forecast approximately **22** new fraud cases over the next 90 days.
  - **Claim Volume**: Average of ~1.2 claims filed per day.

---

## 11. Power BI Dashboard Architecture
The designed dashboard (spec details in [Power BI Spec](file:///c:/Users/harih/Downloads/Data%20Analytics%20Project/Fraud_Detection_Analytics/powerbi/powerbi_dashboard_spec.md)) contains 7 pages:
1. **Executive Summary**: Strategic KPIs (Total Premium, Claims, Loss Ratio, Map of Payouts).
2. **Claims Analysis**: Breakdown of claim status, reasons, and scatter plots of claims vs income.
3. **Fraud Detection**: Highlights suspicious pending claims, model contributions, and investigator tooltips.
4. **Customer Segmentation**: Visualizes RFM segments and customer demographic spreads.
5. **Policy Performance**: Compares loss ratios and net profit margins across Auto, Home, Health, and Life lines.
6. **Forecasting**: Interactively shows 90-day time-series projections with shaded confidence intervals.
7. **Cohort Analysis**: Dynamic matrix heatmap of retention rates.

---

## 12. Business Insights & Recommendations
1. **Underwriting Adjustments**: Home and Auto policy segments currently show higher loss ratios. We recommend increasing premiums by 5–8% in these categories or raising deductible limits.
2. **Dynamic Claim Audit Triggers**: Deploy the `Fraud_Risk_Score` directly in the claims processing workflow. Automatically hold any claim scoring >= 50 for manual verification by the special investigation unit (SIU).
3. **Actuarial Reserve Liquidity**: Ensure cash reserves maintain a buffer matching the upper bound of the 90% forecasting confidence interval ($420,000) to protect against unexpected claim spikes.
4. **Targeted Renewal Outreach**: Direct agents in NY, CA, and TX to target 'At Risk' RFM segments with customized renewal campaigns 60 days before contract expiration to minimize churn.

---

## 13. Future Improvements
- **Real-Time API Ingestion**: Package the preprocessing and fraud score ensemble into a REST API (using FastAPI or Flask) to score claims in real-time at submission.
- **Supervised Deep Learning**: Once more labeled fraud data is collected, train a XGBoost or Neural Network model to improve classification performance.
- **Geographic Shapefiles**: Map local Zipcode coordinates in Power BI using Esri or shapefile boundaries to isolate high-risk local hotspots.

---

## 14. Conclusion
This project demonstrates a full production-ready data engineering and analytics solution. By transforming raw insurance claims data into a structured star schema, performing deep exploratory visualization, engineering risk indicators, and training predictive anomaly models, we establish a robust framework to mitigate risk, optimize profitability, and forecast operations.
