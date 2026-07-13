# Power BI Dashboard Specification & Model Design

This document details the professional Power BI architecture, data model, and visual layouts for the **Fraud Detection and Claims Risk Assessment** project.

---

## 1. Data Model & Relationships

The Power BI model follows a strict Star Schema as loaded in `claims_analytics.db`.

```
Fact_Claims [Many] ---> [1] DimCustomer (via Customer_Key)
Fact_Claims [Many] ---> [1] DimPolicy (via Policy_Key)
Fact_Claims [Many] ---> [1] DimLocation (via Location_Key)
Fact_Claims [Many] ---> [1] DimAgent (via Agent_Key)
Fact_Claims [Many] ---> [1] DimClaimType (via Claim_Type_Key)
Fact_Claims [Many] ---> [1] DimDate (via Claim_Date_Key)
```

- **Cross Filter Direction**: Single (Dimension filters Fact).
- **Date Table**: `DimDate` is marked as the official Date Table in Power BI for time-intelligence functions.

---

## 2. Global DAX Measures Library

Create a table `_Measures` to store all analytical calculations:

```dax
// 1. Portfolio KPIs
Total Customers = DISTINCTCOUNT(Fact_Claims[Customer_Key])

Total Policies = DISTINCTCOUNT(Fact_Claims[Policy_Key])

Total Premium = SUM(DimPolicy[Policy_Premium])

Total Claims = COUNT(Fact_Claims[Claim_Key])

Average Claim = AVERAGE(Fact_Claims[Claim_Amount])

// 2. Fraud Metrics
Fraud Cases = CALCULATE(COUNT(Fact_Claims[Claim_Key]), Fact_Claims[Fraud_Flag] = 1)

Fraud Rate = DIVIDE([Fraud Cases], [Total Claims], 0)

High Risk Customers = CALCULATE(DISTINCTCOUNT(Fact_Claims[Customer_Key]), Fact_Claims[Fraud_Risk_Score] >= 50)

// 3. Financial Performance
Loss Ratio = 
DIVIDE(
    CALCULATE(SUM(Fact_Claims[Claim_Amount]), Fact_Claims[Claim_Status] = "Approved"),
    [Total Premium],
    0
)

Claim Approval Rate = 
DIVIDE(
    CALCULATE(COUNT(Fact_Claims[Claim_Key]), Fact_Claims[Claim_Status] = "Approved"),
    [Total Claims],
    0
)

Claim Rejection Rate = 
DIVIDE(
    CALCULATE(COUNT(Fact_Claims[Claim_Key]), Fact_Claims[Claim_Status] = "Rejected"),
    [Total Claims],
    0
)

Average Claim Risk Score = AVERAGE(Fact_Claims[Fraud_Risk_Score])

// 4. Time Intelligence
Claims YTD = CALCULATE([Total Claims], DATESYTD(DimDate[Full_Date]))

Claims Prior Year = CALCULATE([Total Claims], DATEADD(DimDate[Full_Date], -1, YEAR))

Claims YoY Growth = DIVIDE([Claims YTD] - [Claims Prior Year], [Claims Prior Year], 0)
```

---

## 3. Dashboard Theme & Visual Design
- **Theme**: Cool Tech Dark / Elegant Corporate.
- **Color Palette**:
  - Primary Dark: `#111827` (Page background)
  - Card Fill: `#1F2937` (Container background)
  - Accents: `#3B82F6` (Deep blue), `#10B981` (Emerald green - approved), `#EF4444` (Coral red - fraud/rejections), `#F59E0B` (Amber yellow - pending/warnings).
- **Typography**: `Segoe UI` (Standard Power BI) / `Segoe UI Semibold` for Headers.

---

## 4. Page-by-Page Visual Specification

### Page 1: Executive Summary (Strategic View)
- **KPI Cards**:
  - `Total Customers`, `Total Premium`, `Total Claims`, `Loss Ratio` (with conditional color: green < 40%, red > 60%), `Fraud Rate` (red > 10%).
- **Charts**:
  - **Line and Clustered Column Chart**: Monthly Premiums Collected (column) vs Loss Ratio (line) over time.
  - **Tree Map**: Total Premium and Claims count by `Policy_Type`.
  - **Map Visual**: Claims Count bubble size and Loss Ratio by `Location_State` (US Map).
- **Slicers**: `Policy_Type`, `Location_State`, `Date[Year]`.

### Page 2: Claims Analysis (Operational View)
- **KPI Cards**:
  - `Total Claims`, `Average Claim`, `Claim Approval Rate`, `Claim Rejection Rate`.
- **Charts**:
  - **Donut Chart**: Claims Volume by `Claim_Status` (Approved, Pending, Rejected).
  - **Bar Chart (Horizontal)**: Top 10 `Claim_Reason` by Claim Volume and Total Amount.
  - **Scatter Plot**: Claim Amount vs Customer Income, grouped/colored by `Claim_Status`.
  - **Grid**: Table listing individual claims detail (drill-through target).
- **Interactive Slicers**: `Claim_Status`, `Claim_Reason`, `Accident_Type`.

### Page 3: Fraud Detection (Risk Management View)
- **KPI Cards**:
  - `Fraud Cases`, `Fraud Rate`, `High Risk Customers`, `Average Claim Risk Score`.
- **Charts**:
  - **Bar Chart**: Anomaly count by Model Type (`Isolation Forest`, `LOF`, `DBSCAN`, `One-Class SVM`) compared to ground truth.
  - **Scatter Plot**: Claim Amount vs Fraud Risk Score (flagging `Suspicious_Flag` in bright red).
  - **Table Visual**: Top 50 highest-risk pending claims (fields: `Claim_ID`, `Customer_Name`, `Claim_Amount`, `Fraud_Risk_Score`, `Reason`).
- **Drill-Through Action**: Right-click claim row to open a "Fraud Investigator Tooltip" showing individual model anomaly contributions.

### Page 4: Customer Segmentation (Marketing/Underwriting View)
- **KPI Cards**:
  - `Total Customers`, `Average Customer Income`, `Average Customer Age`.
- **Charts**:
  - **Clustered Column Chart**: Number of Customers and Avg Claim Amount by `Customer_Segment` (VIP, High Value, Regular, At Risk, Dormant, High Fraud Risk).
  - **Box Plot Custom Visual**: Customer Age distribution within each Customer Segment.
  - **Matrix Table**: Customer Segments (Rows) vs Policy Types (Columns) displaying count of customers and sum of premiums.
- **Slicers**: `Customer_Gender`, `Customer_Segment`.

### Page 5: Policy Performance (Portfolio View)
- **KPI Cards**:
  - `Total Policies`, `Total Premium Collected`, `Average Policy Premium`.
- **Charts**:
  - **Clustered Bar Chart**: Loss Ratio and Net Profit by `Policy_Type` (Auto, Home, Health, Life).
  - **Line Chart**: Premium Growth Trends YoY.
  - **Scatter Plot**: Policy Premium vs Claim Payout, with diagonal line indicating break-even (`Claims = Premium`).
- **Slicers**: `Policy_Type`, `DimDate[Year]`.

### Page 6: Forecasting (Finance View)
- **KPI Cards**:
  - `Projected 90-Day Claims Payout`, `Projected 90-Day Claim Volume`, `Projected 90-Day Fraud Cases`.
- **Charts**:
  - **Line Chart with Forecast Shading**: Daily Claims Payout (Actual historical + 90-Day Forecast Mean with 90% Confidence Interval bands).
  - **KPI Grid**: Table showing forecasted monthly values for the next 3 months.
- **Slicers**: None (Uses static prediction output from `claims_forecast_90d.csv`).

### Page 7: Cohort Analysis (Actuarial View)
- **Visuals**:
  - **Matrix Table Heatmap**: `Cohort_Month` (Rows) vs `Cohort_Index` (Columns, 0 to 12) with conditional formatting showing claim activity retention rate (styled as blue gradient).
  - **Line Chart**: Cohort Retention Curve (Average activity rate across months).
- **Slicers**: `Policy_Type`, `Location_State`.

---

## 5. Advanced Navigation and Features

- **Drill Through**: Slicers allow users to select a customer or agent on any page and click a button to drill through to a detailed "Customer Risk Profile" page.
- **Tooltips**: Custom tooltip pages showing:
  - Mini bar chart of claim history when hovering over a customer name.
  - Model anomaly breakdown when hovering over a suspicious claim ID.
- **Bookmarks**:
  - Toggle between **Table View** and **Visual View** on the Claims Analysis page.
  - Reset all filters button.
