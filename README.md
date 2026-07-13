# Fraud Detection and Claims Risk Assessment

An end-to-end data engineering, analytics, and machine learning pipeline for insurance claim fraud detection, customer risk profiling, and operational claims forecasting.

---

## Project Overview

This repository contains a modular and scalable solution to process raw insurance transaction records, identify data anomalies, build a structured star schema database, perform cohort and segmentation analysis, fit machine learning anomaly detection models, and project future claim volumes.

### Key Features
- **Data Profiling & Preprocessing**: Automated detection of missing values, negative inputs, invalid dates, and inconsistent text, followed by standardizing inputs.
- **Star Schema Database**: Normalization of the flat claims table into a central Fact Table and six Dimension Tables (DimCustomer, DimPolicy, DimLocation, DimAgent, DimClaimType, DimDate) inside SQLite.
- **26 Exploratory Data Analysis Charts**: Automatic generation of high-resolution plots mapping demographics, correlations, and financial risk distributions.
- **Customer Segmentation (RFM Analysis)**: Grouping policyholders into distinct value cohorts (VIP, High Value, Regular, At Risk, Dormant, High Fraud Risk) using Recency, Frequency, and Monetary scores.
- **Predictive Fraud Modeling**: Implementation of both deterministic business rules and unsupervised machine learning models (Isolation Forest, Local Outlier Factor, DBSCAN, One-Class SVM) to compute an ensemble **Fraud Risk Score (0-100)** and **Fraud Probability**.
- **90-Day Claims Forecasting**: Daily forecasting of claim counts, payout values, and fraud volumes using SARIMA and ARIMA models with confidence interval bands.
- **actuarial Cohort Retention Analysis**: Retention tracking matrices and heatmaps analyzing claims activity over time.
- **Power BI Layout Specification**: Detailed schema and DAX formulas library for a 7-page analytical dashboard.

---

## Folder Structure

```
Fraud_Detection_Analytics/
│
├── data/
│   ├── raw/                 # Contains Master_Insurance_Data.xlsx
│   └── processed/           # Contains cleaned CSV, customer segments, and SQLite DB
│
├── src/
│   ├── etl/                 # Profiling and Star Schema DB loader scripts
│   ├── preprocessing/       # Cleaning and feature engineering scripts
│   ├── eda/                 # Chart generation visualizer script
│   ├── segmentation/        # RFM and Product Performance scripts
│   ├── fraud_detection/     # ML anomaly models and rule-based detectors
│   ├── forecasting/         # ARIMA and SARIMA forecasting models
│   └── utils/               # Dataset generator and SQL verifier helpers
│
├── sql/
│   ├── create_star_schema.sql  # DDL schema definition script
│   └── queries_analytics.sql   # CTEs, views, and analytical window queries
│
├── reports/                 # Markdown reports (Profiling, Fraud, Forecasting, Cohort)
├── powerbi/                 # Power BI visual specs and DAX measure libraries
├── documentation/           # ER diagrams and system specifications
├── images/                  # Generated plots and figures
├── requirements.txt         # Python library dependencies
└── README.md                # Project walkthrough and documentation
```

---

## Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/Fraud_Detection_Analytics.git
   cd Fraud_Detection_Analytics
   ```

2. **Set Up virtual Environment (Recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage: Running the Pipeline

You can execute individual pipeline steps or run the entire workflow sequentially.

### 1. Generate Raw Data (Demo Mode)
If `Master_Insurance_Data.xlsx` is not present, generate the raw dataset:
```bash
python src/utils/data_generator.py
```

### 2. Profile and Clean Data
Profile raw data for quality anomalies and then clean and format:
```bash
python src/etl/profiling.py
python src/preprocessing/cleaner.py
```

### 3. Load Star Schema Database
Parse the cleaned CSV and load the star schema into SQLite:
```bash
python src/etl/star_schema_loader.py
```

### 4. Run Feature Engineering & Customer RFM Segmentation
Add indicators, calculate RFM scores, and segment customers:
```bash
python src/preprocessing/features.py
python src/segmentation/rfm.py
```

### 5. Run EDA Visualizations & Analytical Metrics
Generate 26 charts and save them in the `images/` directory:
```bash
python src/eda/visualizer.py
python src/segmentation/product_performance.py
python src/segmentation/cohort_analysis.py
```

### 6. Run ML Fraud Detection & 90-Day Forecasting
Fit Isolation Forest/SVM anomaly models, compute fraud risk scores, and forecast future claims:
```bash
python src/fraud_detection/detector.py
python src/forecasting/forecaster.py
```

### 7. Verify SQL Scripts
Test views, window functions, and CTEs against the SQLite DB:
```bash
python src/utils/test_sql.py
```

---

## Core Technologies
- **Data Engineering & ETL**: Python, Pandas, Numpy, Openpyxl, SQLite, SQLAlchemy.
- **Visualization**: Matplotlib, Seaborn, Plotly.
- **Machine Learning & Time-Series**: Scikit-Learn, Statsmodels.
- **Database & Business Intelligence**: ANSI SQL, Power BI (DAX).

---

## Results & Deliverables
Running the pipeline generates the following deliverables under the project root:
- **Clean Dataset**: [processed_insurance_data.csv](data/processed/processed_insurance_data.csv)
- **Star Schema Database**: [claims_analytics.db](data/processed/claims_analytics.db)
- **Data Profiling Report**: [data_profiling_report.md](reports/data_profiling_report.md)
- **EDA & Insights Report**: [eda_report.md](reports/eda_report.md)
- **Fraud Detection Report**: [fraud_detection_report.md](reports/fraud_detection_report.md)
- **Time-Series Forecasting Report**: [forecast_report.md](reports/forecast_report.md)
- **Cohort Retention Report**: [cohort_report.md](reports/cohort_report.md)
- **ER Diagram**: [er_diagram.md](documentation/er_diagram.md)
- **Power BI Spec**: [powerbi_dashboard_spec.md](powerbi/powerbi_dashboard_spec.md)

---

## License
Distributed under the MIT License. See `LICENSE` for more information.
