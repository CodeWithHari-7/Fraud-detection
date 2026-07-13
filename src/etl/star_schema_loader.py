import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime

def load_star_schema(processed_csv_path, db_path):
    print(f"Loading cleaned dataset from: {processed_csv_path}")
    df = pd.read_csv(processed_csv_path)
    
    # Pre-parse dates
    df["Policy_Start_Date"] = pd.to_datetime(df["Policy_Start_Date"])
    df["Policy_End_Date"] = pd.to_datetime(df["Policy_End_Date"])
    df["Claim_Date"] = pd.to_datetime(df["Claim_Date"])

    # 1. Create DimCustomer
    print("Building DimCustomer...")
    dim_customer = df[["Customer_ID", "Customer_Name", "Customer_Age", "Customer_Gender", "Customer_Income"]].copy()
    # Deduplicate based on Customer_ID (keep last info, which is likely latest)
    dim_customer = dim_customer.drop_duplicates(subset=["Customer_ID"], keep="last").reset_index(drop=True)
    dim_customer.index = dim_customer.index + 1
    dim_customer.reset_index(inplace=True)
    dim_customer.rename(columns={"index": "Customer_Key"}, inplace=True)

    # 2. Create DimPolicy
    print("Building DimPolicy...")
    dim_policy = df[["Policy_Number", "Policy_Type", "Policy_Premium", "Policy_Start_Date", "Policy_End_Date"]].copy()
    dim_policy = dim_policy.drop_duplicates(subset=["Policy_Number"], keep="last").reset_index(drop=True)
    dim_policy.index = dim_policy.index + 1
    dim_policy.reset_index(inplace=True)
    dim_policy.rename(columns={"index": "Policy_Key"}, inplace=True)
    # Convert dates to string for SQLite storage
    dim_policy["Policy_Start_Date"] = dim_policy["Policy_Start_Date"].dt.strftime("%Y-%m-%d")
    dim_policy["Policy_End_Date"] = dim_policy["Policy_End_Date"].dt.strftime("%Y-%m-%d")

    # 3. Create DimLocation
    print("Building DimLocation...")
    dim_location = df[["Location_City", "Location_State", "Location_Zipcode"]].copy()
    dim_location.rename(columns={
        "Location_City": "City",
        "Location_State": "State",
        "Location_Zipcode": "Zipcode"
    }, inplace=True)
    dim_location = dim_location.drop_duplicates().reset_index(drop=True)
    dim_location.index = dim_location.index + 1
    dim_location.reset_index(inplace=True)
    dim_location.rename(columns={"index": "Location_Key"}, inplace=True)

    # 4. Create DimAgent
    print("Building DimAgent...")
    dim_agent = df[["Agent_ID", "Agent_Name"]].copy()
    dim_agent = dim_agent.drop_duplicates(subset=["Agent_ID"], keep="last").reset_index(drop=True)
    dim_agent.index = dim_agent.index + 1
    dim_agent.reset_index(inplace=True)
    dim_agent.rename(columns={"index": "Agent_Key"}, inplace=True)

    # 5. Create DimClaimType
    print("Building DimClaimType...")
    dim_claim_type = df[["Claim_Reason", "Accident_Type"]].copy()
    dim_claim_type = dim_claim_type.drop_duplicates().reset_index(drop=True)
    dim_claim_type.index = dim_claim_type.index + 1
    dim_claim_type.reset_index(inplace=True)
    dim_claim_type.rename(columns={"index": "Claim_Type_Key"}, inplace=True)

    # 6. Create DimDate
    print("Building DimDate...")
    # Gather all dates from Policy Start Date and Claim Date
    all_dates = pd.concat([df["Policy_Start_Date"], df["Claim_Date"]]).dropna().unique()
    all_dates = pd.to_datetime(all_dates)
    min_date = all_dates.min()
    max_date = all_dates.max()
    
    # Generate full sequence of dates
    date_range = pd.date_range(start=min_date, end=max_date, freq='D')
    dim_date = pd.DataFrame({"Full_Date": date_range})
    dim_date["Date_Key"] = dim_date["Full_Date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["Year"] = dim_date["Full_Date"].dt.year
    dim_date["Quarter"] = dim_date["Full_Date"].dt.quarter
    dim_date["Month"] = dim_date["Full_Date"].dt.month
    dim_date["Month_Name"] = dim_date["Full_Date"].dt.strftime("%B")
    dim_date["Day"] = dim_date["Full_Date"].dt.day
    dim_date["Day_Of_Week"] = dim_date["Full_Date"].dt.dayofweek + 1 # 1-7 (Mon-Sun)
    dim_date["Day_Name"] = dim_date["Full_Date"].dt.strftime("%A")
    dim_date["Is_Weekend"] = dim_date["Day_Of_Week"].apply(lambda x: 1 if x in [6, 7] else 0)
    dim_date["Full_Date"] = dim_date["Full_Date"].dt.strftime("%Y-%m-%d")

    # 7. Create Fact_Claims
    print("Building Fact_Claims...")
    # Merge dimensions to resolve surrogate keys
    fact = df.copy()
    
    fact = fact.merge(dim_customer[["Customer_Key", "Customer_ID"]], on="Customer_ID", how="left")
    fact = fact.merge(dim_policy[["Policy_Key", "Policy_Number"]], on="Policy_Number", how="left")
    
    # Merge Location
    fact.rename(columns={
        "Location_City": "City",
        "Location_State": "State",
        "Location_Zipcode": "Zipcode"
    }, inplace=True)
    # Ensure ZIP code is string for merging
    fact["Zipcode"] = fact["Zipcode"].astype(str)
    dim_location["Zipcode"] = dim_location["Zipcode"].astype(str)
    fact = fact.merge(dim_location, on=["City", "State", "Zipcode"], how="left")
    
    fact = fact.merge(dim_agent[["Agent_Key", "Agent_ID"]], on="Agent_ID", how="left")
    fact = fact.merge(dim_claim_type, on=["Claim_Reason", "Accident_Type"], how="left")
    
    # Date key mapping
    fact["Claim_Date_Key"] = fact["Claim_Date"].dt.strftime("%Y%m%d").astype(int)
    
    # Final fact columns selection
    fact_claims = fact[[
        "Claim_ID", "Customer_Key", "Policy_Key", "Location_Key", 
        "Agent_Key", "Claim_Type_Key", "Claim_Date_Key", 
        "Claim_Amount", "Claim_Status", "Fraud_Flag"
    ]].copy()
    fact_claims.index = fact_claims.index + 1
    fact_claims.reset_index(inplace=True)
    fact_claims.rename(columns={"index": "Claim_Key"}, inplace=True)

    # 8. Load into SQLite database
    print(f"Loading data into SQLite database at: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # If file exists, remove it to reload fresh
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    
    # Write tables
    dim_customer.to_sql("DimCustomer", conn, if_exists="replace", index=False)
    dim_policy.to_sql("DimPolicy", conn, if_exists="replace", index=False)
    dim_location.to_sql("DimLocation", conn, if_exists="replace", index=False)
    dim_agent.to_sql("DimAgent", conn, if_exists="replace", index=False)
    dim_claim_type.to_sql("DimClaimType", conn, if_exists="replace", index=False)
    dim_date.to_sql("DimDate", conn, if_exists="replace", index=False)
    fact_claims.to_sql("Fact_Claims", conn, if_exists="replace", index=False)
    
    # Add indexes manually (SQLite requires standard SQL command for index creation)
    cursor = conn.cursor()
    cursor.execute("CREATE UNIQUE INDEX idx_dim_cust_id ON DimCustomer(Customer_ID);")
    cursor.execute("CREATE INDEX idx_dim_pol_num ON DimPolicy(Policy_Number);")
    cursor.execute("CREATE INDEX idx_fact_claim_id ON Fact_Claims(Claim_ID);")
    cursor.execute("CREATE INDEX idx_fact_cust_key ON Fact_Claims(Customer_Key);")
    cursor.execute("CREATE INDEX idx_fact_pol_key ON Fact_Claims(Policy_Key);")
    cursor.execute("CREATE INDEX idx_fact_loc_key ON Fact_Claims(Location_Key);")
    cursor.execute("CREATE INDEX idx_fact_agt_key ON Fact_Claims(Agent_Key);")
    cursor.execute("CREATE INDEX idx_fact_claim_type_key ON Fact_Claims(Claim_Type_Key);")
    cursor.execute("CREATE INDEX idx_fact_date_key ON Fact_Claims(Claim_Date_Key);")
    cursor.execute("CREATE INDEX idx_fact_fraud ON Fact_Claims(Fraud_Flag);")
    cursor.execute("CREATE INDEX idx_fact_status ON Fact_Claims(Claim_Status);")
    cursor.execute("CREATE INDEX idx_dim_pol_type ON DimPolicy(Policy_Type);")
    cursor.execute("CREATE INDEX idx_dim_loc_state ON DimLocation(State);")
    
    conn.commit()
    conn.close()
    
    print("Successfully built SQLite Database and loaded Star Schema!")

if __name__ == "__main__":
    processed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "processed_insurance_data.csv"))
    db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "claims_analytics.db"))
    load_star_schema(processed_path, db_file)
