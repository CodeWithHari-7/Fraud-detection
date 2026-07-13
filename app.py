import os
import re
import random
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import datetime
import pytz
import subprocess
import sys

# --- Page Config ---
st.set_page_config(
    page_title="Claims Risk & Fraud Analytics Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Path Configurations ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "processed_insurance_data.csv")
PRODUCT_PERF_PATH = os.path.join(BASE_DIR, "data", "processed", "product_performance.csv")
FORECAST_PATH = os.path.join(BASE_DIR, "data", "processed", "claims_forecast_90d.csv")
CUSTOMER_SEG_PATH = os.path.join(BASE_DIR, "data", "processed", "customer_segments.csv")
COHORT_PIVOT_PATH = os.path.join(BASE_DIR, "data", "processed", "cohort_pivot.csv")

# --- Indian Formatting Helpers ---
def format_inr(val):
    if pd.isna(val):
        return "₹0"
    return f"₹{val:,.0f}"

def get_ist_time():
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.datetime.now(tz).strftime("%d/%m/%Y, %I:%M:%S %p")

# --- Robust Column Mapping Logic ---
def map_excel_to_pipeline_format(df):
    def normalize_name(s):
        return re.sub(r'[^a-z0-9]', '', str(s).lower())
    
    col_mapping = {}
    for col in df.columns:
        norm = normalize_name(col)
        col_mapping[norm] = col
        
    rules = [
        ("Claim_ID", ["claimid", "claimnumber", "claimno"]),
        ("Customer_ID", ["customerid", "custid"]),
        ("Policy_Number", ["policyid", "policynumber", "policyno"]),
        ("Agent_ID", ["agentid"]),
        ("Claim_Date", ["claimdate", "date"]),
        ("Claim_Amount", ["claimamount", "claimamt"]),
        ("Policy_Premium", ["annualpremium", "premium", "policypremium"]),
        ("Claim_Status", ["claimstatus", "status"]),
        ("Fraud_Flag", ["fraudlabel", "fraudflag", "isfraud", "fraud"]),
        ("Location_State", ["region", "state", "locationstate"])
    ]
    
    mapped_sources = {}
    for target, sources in rules:
        for src in sources:
            if src in col_mapping:
                mapped_sources[target] = col_mapping[src]
                break
                
    if "Claim_ID" not in mapped_sources:
        if "Claim_ID" in df.columns:
            return df
        return df
        
    np.random.seed(42)
    random.seed(42)
    
    mapped_data = []
    first_names = ["John", "Jane", "Robert", "Mary", "Michael", "Linda", "David", "Elizabeth", "William", "Barbara", 
                   "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    city_map = {
        "East": ("New York", "NY", "10001"),
        "West": ("Los Angeles", "CA", "90001"),
        "South": ("Houston", "TX", "77001"),
        "North": ("Chicago", "IL", "60601")
    }
    
    policy_type_map = {
        "Collision": "Auto",
        "Theft": "Auto",
        "Fire": "Home",
        "Natural": "Life",
        "Medical": "Health"
    }
    
    reason_map = {
        "Collision": "Collision",
        "Theft": "Theft",
        "Fire": "Fire",
        "Natural": "Natural Death",
        "Medical": "Medical Procedure"
    }
    
    accident_map = {
        "Collision": "Multi Vehicle",
        "Theft": "Theft",
        "Fire": "Fire",
        "Natural": "Natural Disaster",
        "Medical": "Medical Treatment"
    }
    
    for idx, row in df.iterrows():
        region_col = mapped_sources.get("Location_State")
        region = row[region_col] if region_col else "East"
        city_info = city_map.get(region, ("New York", "NY", "10001"))
        
        claim_type = row["ClaimType"] if "ClaimType" in df.columns else "Collision"
        policy_type = policy_type_map.get(claim_type, "Auto")
        claim_reason = reason_map.get(claim_type, claim_type)
        accident_type = accident_map.get(claim_type, "Single Vehicle")
        
        cust_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        age = int(np.random.normal(45, 15))
        age = max(18, min(85, age))
        gender = random.choice(["Male", "Female"])
        income = float(np.random.normal(60000, 20000))
        income = max(15000, min(150000, income))
        
        date_col = mapped_sources.get("Claim_Date")
        claim_date_str = str(row[date_col]) if date_col else str(pd.Timestamp.now())
        try:
            claim_date = pd.to_datetime(claim_date_str)
        except Exception:
            claim_date = pd.Timestamp.now()
            
        policy_start = claim_date - pd.Timedelta(days=random.randint(30, 365))
        policy_end = policy_start + pd.Timedelta(days=365)
        
        prev_col = "PreviousClaims" if "PreviousClaims" in df.columns else None
        prev_claims = int(row[prev_col]) if prev_col and not pd.isna(row[prev_col]) else random.randint(0, 5)
        
        prem_col = mapped_sources.get("Policy_Premium")
        premium = float(row[prem_col]) if prem_col else 500.0
        
        amt_col = mapped_sources.get("Claim_Amount")
        claim_amt = float(row[amt_col]) if amt_col else 0.0
        
        status_col = mapped_sources.get("Claim_Status")
        status = str(row[status_col]) if status_col else "Approved"
        
        fraud_col = mapped_sources.get("Fraud_Flag")
        fraud_flag = int(row[fraud_col]) if fraud_col and not pd.isna(row[fraud_col]) else 0
        
        mapped_data.append({
            "Claim_ID": str(row[mapped_sources["Claim_ID"]]),
            "Customer_ID": str(row[mapped_sources["Customer_ID"]]) if "Customer_ID" in mapped_sources else f"CUST{idx}",
            "Customer_Name": cust_name,
            "Customer_Age": age,
            "Customer_Gender": gender,
            "Customer_Income": income,
            "Location_City": city_info[0],
            "Location_State": city_info[1],
            "Location_Zipcode": city_info[2],
            "Policy_Number": str(row[mapped_sources["Policy_Number"]]) if "Policy_Number" in mapped_sources else f"POL{idx}",
            "Policy_Type": policy_type,
            "Policy_Start_Date": policy_start.strftime("%Y-%m-%d"),
            "Policy_End_Date": policy_end.strftime("%Y-%m-%d"),
            "Policy_Premium": premium,
            "Agent_ID": str(row[mapped_sources["Agent_ID"]]) if "Agent_ID" in mapped_sources else f"AGT{idx}",
            "Agent_Name": f"Agent {random.choice(first_names)} {random.choice(last_names)}",
            "Claim_Date": claim_date.strftime("%Y-%m-%d"),
            "Claim_Amount": claim_amt,
            "Claim_Status": status,
            "Claim_Reason": claim_reason,
            "Previous_Claims": prev_claims,
            "Accident_Type": accident_type,
            "Fraud_Flag": fraud_flag
        })
        
    return pd.DataFrame(mapped_data)

# --- Sidebar UI ---
st.sidebar.markdown(f"## 🛡️ Claims Analytics")
st.sidebar.markdown(f"⏱️ **IST Clock**: {get_ist_time()}")

tab = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Executive Summary",
        "🔍 Claims Analysis",
        "📈 Policy Performance",
        "🕵️ Fraud Detection",
        "🔮 Claims Forecasting",
        "👥 Cohort Retention",
        "📥 Upload Center"
    ]
)

# Load base data
@st.cache_data
def load_data():
    if not os.path.exists(PROCESSED_DATA_PATH):
        return None
    return pd.read_csv(PROCESSED_DATA_PATH)

df = load_data()

if df is None:
    st.error("No processed data found. Please go to the 'Upload Center' tab to upload your raw Excel file and run the pipeline.")
else:
    # --- Tab 1: Executive Summary ---
    if tab == "📊 Executive Summary":
        st.title("📊 Executive Summary")
        st.markdown("Real-time portfolio metrics, loss ratios, and risk concentrations.")
        
        # Calculate KPI Metrics
        unique_pol = df.drop_duplicates(subset=["Policy_Number"])
        approved_claims = df[df["Claim_Status"] == "Approved"]
        
        total_premium = unique_pol["Policy_Premium"].sum()
        total_claims_paid = approved_claims["Claim_Amount"].sum()
        loss_ratio = (total_claims_paid / total_premium * 100) if total_premium > 0 else 0.0
        
        total_claims = len(df)
        fraud_cases = df["Fraud_Flag"].sum()
        fraud_rate = (fraud_cases / total_claims * 100) if total_claims > 0 else 0.0
        
        avg_claim = df["Claim_Amount"].mean()
        high_risk_cust = df[df["Risk_Score"] >= 50]["Customer_ID"].nunique()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Premium Collected", format_inr(total_premium))
        col2.metric("Total Claims Paid", format_inr(total_claims_paid))
        col3.metric("Portfolio Loss Ratio", f"{loss_ratio:.1f}%")
        col4.metric("Average Claim Payout", format_inr(avg_claim))
        
        col1_2, col2_2, col3_2, col4_2 = st.columns(4)
        col1_2.metric("Total Policies", f"{len(unique_pol):,}")
        col2_2.metric("Total Claims Processed", f"{total_claims:,}")
        col3_2.metric("Flagged Fraud Cases", f"{fraud_cases:,}")
        col4_2.metric("Fraud Rate", f"{fraud_rate:.2f}%")
        
        st.markdown("---")
        st.markdown("### Risk Concentration Dashboard")
        
        # Layout metrics side-by-side
        g1, g2 = st.columns(2)
        
        # State Claim Distribution Map/Chart
        state_claims = df.groupby("Location_State")["Claim_Amount"].sum().reset_index()
        fig_state = px.bar(
            state_claims, 
            x="Location_State", 
            y="Claim_Amount", 
            title="Total Claim Payouts by State (INR)",
            labels={"Claim_Amount": "Total Claims Paid (INR)", "Location_State": "State"},
            color_discrete_sequence=["#1f77b4"]
        )
        fig_state.update_layout(template="plotly_dark")
        g1.plotly_chart(fig_state, use_container_width=True)
        
        # Policy Type Popularity Pie
        policy_popularity = unique_pol["Policy_Type"].value_counts().reset_index()
        policy_popularity.columns = ["Policy Type", "Count"]
        fig_pie = px.pie(
            policy_popularity, 
            values="Count", 
            names="Policy Type", 
            title="Policy Portfolio Distribution",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_layout(template="plotly_dark")
        g2.plotly_chart(fig_pie, use_container_width=True)

    # --- Tab 2: Claims Analysis ---
    elif tab == "🔍 Claims Analysis":
        st.title("🔍 Claims Search & Risk Validation Grid")
        st.markdown("Sort, search, and audit dynamic claim records.")
        
        search_query = st.text_input("🔍 Search by Customer Name or Claim ID:", "")
        
        # Filter data
        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df["Customer_Name"].str.contains(search_query, case=False, na=False) |
                filtered_df["Claim_ID"].str.contains(search_query, case=False, na=False)
            ]
            
        st.markdown(f"Showing **{len(filtered_df)}** claims matching query.")
        
        display_cols = ["Claim_ID", "Customer_Name", "Policy_Type", "Claim_Amount", "Claim_Status", "Fraud_Risk_Score", "Location_State", "Claim_Date"]
        claims_grid = filtered_df[display_cols].sort_values("Fraud_Risk_Score", ascending=False)
        
        # Format Claim Amount in Grid
        claims_grid["Claim_Amount"] = claims_grid["Claim_Amount"].apply(format_inr)
        
        st.dataframe(claims_grid, use_container_width=True, height=500)

    # --- Tab 3: Policy Performance ---
    elif tab == "📈 Policy Performance":
        st.title("📈 Policy Product Profitability Analysis")
        st.markdown("Assess net profits, premiums, and loss ratios across policy categories.")
        
        if os.path.exists(PRODUCT_PERF_PATH):
            perf_df = pd.read_csv(PRODUCT_PERF_PATH)
            
            st.markdown("### Product Comparison Matrix")
            # Format matrix
            matrix_df = perf_df.copy()
            matrix_df["Total_Premium_Collected"] = matrix_df["Total_Premium_Collected"].apply(format_inr)
            matrix_df["Total_Claims_Paid"] = matrix_df["Total_Claims_Paid"].apply(format_inr)
            matrix_df["Net_Profit"] = matrix_df["Net_Profit"].apply(format_inr)
            matrix_df["Average_Claim_Amount_Paid"] = matrix_df["Average_Claim_Amount_Paid"].apply(format_inr)
            matrix_df["Loss_Ratio"] = (matrix_df["Loss_Ratio"] * 100).round(2).apply(lambda x: f"{x}%")
            
            st.dataframe(matrix_df, use_container_width=True)
            
            st.markdown("---")
            g1, g2 = st.columns(2)
            
            # Net Operating Underwriting Profit
            fig_prof = px.bar(
                perf_df, 
                x="Policy_Type", 
                y="Net_Profit", 
                title="Underwriting Profitability Comparison (INR)",
                labels={"Net_Profit": "Net Operating Underwriting Profit (INR)", "Policy_Type": "Policy Type"},
                color="Policy_Type"
            )
            fig_prof.update_layout(template="plotly_dark")
            g1.plotly_chart(fig_prof, use_container_width=True)
            
            # Loss Ratio
            fig_loss = px.bar(
                perf_df, 
                x="Policy_Type", 
                y="Loss_Ratio", 
                title="Loss Ratio Comparison",
                labels={"Loss_Ratio": "Loss Ratio (Decimals)", "Policy_Type": "Policy Type"},
                color="Policy_Type"
            )
            fig_loss.update_layout(template="plotly_dark")
            g2.plotly_chart(fig_loss, use_container_width=True)
        else:
            st.warning("Product performance data is missing. Please run the pipeline.")

    # --- Tab 4: Fraud Detection ---
    elif tab == "🕵️ Fraud Detection":
        st.title("🕵️ Outlier Machine Learning & Fraud Risk Scoring")
        st.markdown("Calculated scores mapping rule-based logic and ensemble ML models (Isolation Forest, LOF, DBSCAN, OCSVM).")
        
        suspicious_df = df[df["Suspicious_Flag"] == 1].sort_values("Fraud_Risk_Score", ascending=False)
        
        st.markdown(f"### Suspicious Claims Pending SIU Verification ({len(suspicious_df)} cases)")
        
        suspicious_grid = suspicious_df[["Claim_ID", "Customer_ID", "Policy_Type", "Claim_Amount", "Fraud_Risk_Score", "Fraud_Probability", "Claim_Reason"]].copy()
        suspicious_grid["Claim_Amount"] = suspicious_grid["Claim_Amount"].apply(format_inr)
        
        st.dataframe(suspicious_grid, use_container_width=True, height=400)
        
        # Layout anomaly comparisons
        st.markdown("---")
        st.markdown("### Ensemble Model Voting Agreement")
        
        model_cols = ["ML_IsoForest", "ML_LOF", "ML_DBSCAN", "ML_OCSVM"]
        model_sums = {col.replace("ML_", ""): int((df[col] == -1).sum()) for col in model_cols}
        
        models_df = pd.DataFrame(list(model_sums.items()), columns=["Model", "Flagged Anomalies"])
        
        fig_models = px.bar(
            models_df, 
            x="Model", 
            y="Flagged Anomalies", 
            title="Comparison of Flagged Outliers by Model",
            color="Model",
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_models.update_layout(template="plotly_dark")
        st.plotly_chart(fig_models, use_container_width=True)

    # --- Tab 5: Claims Forecasting ---
    elif tab == "🔮 Claims Forecasting":
        st.title("🔮 statsmodels 90-Day Claims Forecasting")
        st.markdown("Time-series projection models tracking claim volume, payouts, and fraud counts.")
        
        if os.path.exists(FORECAST_PATH):
            fc_df = pd.read_csv(FORECAST_PATH)
            
            # Interactive Line chart showing 90-day daily payout projections
            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(
                x=fc_df["Date"], 
                y=fc_df["Forecasted_Payout"],
                name="Projected Daily Payout (INR)", 
                line=dict(color="#d95f02", width=3, dash="dash")
            ))
            fig_fc.add_trace(go.Scatter(
                x=fc_df["Date"], 
                y=fc_df["Forecasted_Payout_Upper"],
                name="90% Confidence Upper Limit", 
                line=dict(color="#ff7f0e", width=1), 
                fill=None
            ))
            fig_fc.add_trace(go.Scatter(
                x=fc_df["Date"], 
                y=fc_df["Forecasted_Payout_Lower"],
                name="90% Confidence Lower Limit", 
                line=dict(color="#ff7f0e", width=1), 
                fill='tonexty', 
                fillcolor='rgba(255, 127, 14, 0.15)'
            ))
            
            fig_fc.update_layout(
                title="90-Day Projected Payout Trend (INR)",
                xaxis_title="Forecast Date",
                yaxis_title="Payout Amount (INR)",
                template="plotly_dark",
                legend=dict(x=0.01, y=0.99)
            )
            
            st.plotly_chart(fig_fc, use_container_width=True)
            
            # Key statistics
            total_projected = fc_df["Forecasted_Payout"].sum()
            avg_projected = fc_df["Forecasted_Payout"].mean()
            st.info(f"🔮 **Total Projected Portfolio Claims Payout (Next 90 Days)**: {format_inr(total_projected)} | **Avg Daily Payout**: {format_inr(avg_projected)}")
        else:
            st.warning("Forecasting data not found. Please run the pipeline.")

    # --- Tab 6: Cohort Retention ---
    elif tab == "👥 Cohort Retention":
        st.title("👥 Actuarial Cohort Retention Analysis")
        st.markdown("Cohort retention tracking customer lifetime value (CLV) and premium durability.")
        
        if os.path.exists(COHORT_PIVOT_PATH):
            cohort_pivot = pd.read_csv(COHORT_PIVOT_PATH)
            
            # Format columns
            cohort_display = cohort_pivot.set_index("Acquisition_Month")
            
            st.markdown("### Cohort Active Retention Percentage Heatmap")
            
            # Retention plot
            fig_cohort = px.imshow(
                cohort_display,
                labels=dict(x="Months Active", y="Acquisition Cohort", color="Retention %"),
                x=cohort_display.columns,
                y=cohort_display.index,
                color_continuous_scale="Viridis",
                title="Actuarial Cohort Monthly Retention Rate"
            )
            fig_cohort.update_layout(template="plotly_dark")
            st.plotly_chart(fig_cohort, use_container_width=True)
            
            st.dataframe(cohort_display.style.format("{:.1f}%", na_rep="-"), use_container_width=True)
        else:
            st.warning("Cohort pivot table not found. Please run the pipeline.")

# --- Tab 7: Upload Center ---
if tab == "📥 Upload Center":
    st.title("📥 Upload Excel Data Center")
    st.markdown("Upload raw insurance Excel workbooks, map columns, and execute analytics pipeline.")
    
    uploaded_file = st.file_uploader("Choose an Excel File", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        
        # Read file
        df_raw = pd.read_excel(uploaded_file)
        
        st.markdown("### Raw Excel Structure Preview:")
        st.write(df_raw.head())
        
        if st.button("🚀 Process & Execute Calculations"):
            with st.spinner("Processing workbook..."):
                # Map Excel to standard pipeline format
                df_mapped = map_excel_to_pipeline_format(df_raw)
                
                # Save raw Excel to target pipeline folder
                raw_dir = os.path.join(BASE_DIR, "data", "raw")
                os.makedirs(raw_dir, exist_ok=True)
                file_path = os.path.join(raw_dir, "Master_Insurance_Data.xlsx")
                df_mapped.to_excel(file_path, index=False)
                st.info("Successfully converted alternate columns & saved raw workbook.")
                
            # Sequentially execute pipeline scripts
            pipeline_scripts = [
                "src/preprocessing/cleaner.py",
                "src/etl/star_schema_loader.py",
                "src/preprocessing/features.py",
                "src/segmentation/rfm.py",
                "src/segmentation/product_performance.py",
                "src/segmentation/cohort_analysis.py",
                "src/fraud_detection/detector.py",
                "src/forecasting/forecaster.py"
            ]
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, script in enumerate(pipeline_scripts):
                script_path = os.path.join(BASE_DIR, script)
                status_text.text(f"Running script: {script}...")
                
                args = [sys.executable, script_path]
                if script == "src/forecasting/forecaster.py":
                    args.append("--fast")
                    
                subprocess.run(args, capture_output=True, text=True, check=True)
                progress_bar.progress(int((idx + 1) / len(pipeline_scripts) * 100))
                
            st.success("🎉 Calculations completed successfully! All database stars, segments, fraud outlier models, and forecasters are updated.")
            st.balloons()
            
            # Clear st.cache_data to force reload
            st.cache_data.clear()
