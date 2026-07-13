import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_insurance_data(output_path, num_records=1000):
    np.random.seed(42)
    random.seed(42)
    
    # Helper lists
    first_names = ["John", "Jane", "Robert", "Mary", "Michael", "Linda", "David", "Elizabeth", "William", "Barbara", 
                   "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    cities_states = [
        ("New York", "NY", "10001"),
        ("Los Angeles", "CA", "90001"),
        ("Chicago", "IL", "60601"),
        ("Houston", "TX", "77001"),
        ("Miami", "FL", "33101"),
        ("San Francisco", "CA", "94101"),
        ("Austin", "TX", "78701"),
        ("Seattle", "WA", "98101"),
        ("Boston", "MA", "02101"),
        ("Atlanta", "GA", "30301")
    ]
    
    policy_types = ["Auto", "Home", "Health", "Life"]
    claim_reasons = {
        "Auto": ["Collision", "Theft", "Vandalisim", "Windshield Breakage", "Roadside Assistance"],
        "Home": ["Water Damage", "Fire", "Theft", "Wind Damage", "Hail Damage"],
        "Health": ["Medical Procedure", "Doctor Visit", "Emergency Room", "Prescription", "Dental Treatment"],
        "Life": ["Natural Death", "Accidental Death", "Critical Illness", "Terminal Illness"]
    }
    
    accident_types = ["Single Vehicle", "Multi Vehicle", "Theft", "Fire", "Natural Disaster", "Medical Treatment", "N/A"]
    agent_pool = [(f"AGT{i:04d}", f"Agent {random.choice(first_names)} {random.choice(last_names)}") for i in range(1, 31)]
    
    data = []
    
    # Base generation of 1000 records
    for i in range(num_records):
        claim_id = f"CLM{10000 + i}"
        customer_id = f"CUST{20000 + random.randint(1, 800)}" # Allows multiple claims per customer
        cust_first = random.choice(first_names)
        cust_last = random.choice(last_names)
        cust_name = f"{cust_first} {cust_last}"
        
        # Age with outliers
        age_rand = random.random()
        if age_rand < 0.02:
            age = random.choice([-5, -15, 150, 120]) # Negative or impossible values
        elif age_rand < 0.06:
            age = None # Missing value
        else:
            age = int(np.random.normal(45, 15))
            age = max(18, min(85, age)) # Keep in reasonable bounds normally
            
        # Gender with dirty labels
        gender_choice = random.choice(["Male", "Female", "M", "F", "MALE", "FEMALE", "Femal", None])
        
        # Income with missing and negative values
        inc_rand = random.random()
        if inc_rand < 0.03:
            income = -random.randint(10000, 50000)
        elif inc_rand < 0.08:
            income = None
        else:
            income = int(np.random.normal(65000, 25000))
            income = max(15000, income)
            
        city, state, zipcode = random.choice(cities_states)
        
        # Zipcode dirtying
        if random.random() < 0.05:
            zipcode = int(zipcode) # Store as numeric instead of string
            
        policy_num = f"POL{random.randint(100000, 999999)}"
        policy_type = random.choice(policy_types)
        
        # Dates (Dirtying: YYYY-MM-DD, MM/DD/YYYY, timestamp, invalid date strings)
        start_year = random.randint(2020, 2024)
        start_month = random.randint(1, 12)
        start_day = random.randint(1, 28)
        start_dt = datetime(start_year, start_month, start_day)
        
        dt_format = random.random()
        if dt_format < 0.05:
            policy_start = f"{start_month:02d}/{start_day:02d}/{start_year}"
        elif dt_format < 0.07:
            policy_start = "2024-15-40" # Invalid date
        elif dt_format < 0.09:
            policy_start = "Unknown"
        else:
            policy_start = start_dt.strftime("%Y-%m-%d")
            
        # Policy End Date: normally 1 year later
        if random.random() < 0.03:
            policy_end = (start_dt - timedelta(days=30)).strftime("%Y-%m-%d") # End before start
        else:
            policy_end = (start_dt + timedelta(days=365)).strftime("%Y-%m-%d")
            
        # Premium: string with $, negative, missing
        prem_val = float(np.random.normal(500, 150))
        prem_val = max(100.0, prem_val)
        prem_rand = random.random()
        if prem_rand < 0.02:
            premium = f"-${prem_val:.2f}"
        elif prem_rand < 0.05:
            premium = f"${prem_val:.2f}"
        elif prem_rand < 0.08:
            premium = None
        else:
            premium = round(prem_val, 2)
            
        agent_id, agent_name = random.choice(agent_pool)
        
        # Claim Date
        claim_offset = random.randint(-40, 400) # can be before policy start
        claim_dt = start_dt + timedelta(days=claim_offset)
        
        c_dt_format = random.random()
        if c_dt_format < 0.05:
            claim_date = claim_dt.strftime("%m/%d/%Y")
        elif c_dt_format < 0.08:
            claim_date = None
        else:
            claim_date = claim_dt.strftime("%Y-%m-%d")
            
        # Claim Amount: string with $, negative, missing, extreme outliers
        claim_base = float(np.random.normal(5000, 4000))
        claim_base = max(100.0, claim_base)
        claim_rand = random.random()
        if claim_rand < 0.01:
            claim_amount = -round(claim_base, 2)
        elif claim_rand < 0.03:
            claim_amount = f"${claim_base:.2f}"
        elif claim_rand < 0.05:
            claim_amount = round(claim_base * 30, 2) # Extreme outlier ($150,000+)
        elif claim_rand < 0.08:
            claim_amount = None
        else:
            claim_amount = round(claim_base, 2)
            
        # Claim Status: dirty categories
        claim_status = random.choice(["Approved", "Rejected", "Pending", "Approvedd", "Rejctd", "Pendng", None])
        
        claim_reason = random.choice(claim_reasons[policy_type])
        previous_claims = random.choice([0, 0, 0, 1, 1, 2, 3, 4, 5])
        accident_type = random.choice(accident_types)
        
        # Build logic for historical fraud flag (used to train ML/evaluate rules)
        is_fraud = 0
        
        # A claim amount is numeric and valid for logic check
        try:
            c_amt = float(str(claim_amount).replace('$', '').replace(',', '')) if claim_amount is not None else 0
        except ValueError:
            c_amt = 0
            
        try:
            prem = float(str(premium).replace('$', '').replace(',', '')) if premium is not None else 0
        except ValueError:
            prem = 0
            
        # Logic patterns for fraud
        if c_amt > 80000:
            is_fraud = 1 # Extreme claims are highly suspicious
        elif claim_offset >= 0 and claim_offset < 10 and c_amt > 15000:
            is_fraud = 1 # Claim registered right after policy start
        elif c_amt > 15000 and prem < 150:
            is_fraud = 1 # Low premium, very high claim
        elif previous_claims >= 4 and random.random() < 0.5:
            is_fraud = 1 # Repeat claimants
        elif claim_offset < 0:
            is_fraud = 1 # Claims occurred before policy started (clearly fraudulent)
            
        # Add some random fraud for noise
        if random.random() < 0.02:
            is_fraud = 1
            
        data.append({
            "Claim_ID": claim_id,
            "Customer_ID": customer_id,
            "Customer_Name": cust_name,
            "Customer_Age": age,
            "Customer_Gender": gender_choice,
            "Customer_Income": income,
            "Location_City": city,
            "Location_State": state,
            "Location_Zipcode": zipcode,
            "Policy_Number": policy_num,
            "Policy_Type": policy_type,
            "Policy_Start_Date": policy_start,
            "Policy_End_Date": policy_end,
            "Policy_Premium": premium,
            "Agent_ID": agent_id,
            "Agent_Name": agent_name,
            "Claim_Date": claim_date,
            "Claim_Amount": claim_amount,
            "Claim_Status": claim_status,
            "Claim_Reason": claim_reason,
            "Previous_Claims": previous_claims,
            "Accident_Type": accident_type,
            "Fraud_Flag": is_fraud
        })
        
    # Generate some duplicates (exact duplicates)
    for _ in range(15):
        dup_record = random.choice(data).copy()
        data.append(dup_record)
        
    # Generate duplicate IDs with different data
    for j in range(10):
        record_to_dup = random.choice(data).copy()
        record_to_dup["Customer_Name"] = "Duplicate ID Holder"
        record_to_dup["Claim_Amount"] = 99999.0
        data.append(record_to_dup)
        
    df = pd.DataFrame(data)
    
    # Write to Excel
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"Generated raw insurance dataset: {output_path} with {len(df)} records.")

if __name__ == "__main__":
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw"))
    out_file = os.path.join(out_dir, "Master_Insurance_Data.xlsx")
    generate_insurance_data(out_file)
