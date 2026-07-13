import os
import re
import numpy as np
import pandas as pd
from typing import Dict, Any

class DataCleaner:
    """Class to clean and preprocess raw insurance claim data."""

    def __init__(self, raw_path: str):
        self.raw_path = raw_path
        self.df = pd.read_excel(raw_path)
        print(f"Loaded raw dataset with {self.df.shape[0]} rows and {self.df.shape[1]} columns.")

    def clean_data(self) -> pd.DataFrame:
        """Runs the entire cleaning pipeline."""
        df = self.df.copy()

        # 1. Clean whitespace and text columns
        df = self._normalize_text(df)

        # 2. Convert currency and numeric columns stored as strings
        df = self._clean_numeric_columns(df)

        # 3. Standardize categorical columns
        df = self._standardize_categoricals(df)

        # 4. Handle invalid and impossible numbers
        df = self._fix_impossible_values(df)

        # 5. Convert and validate dates
        df = self._clean_dates(df)

        # 6. Remove duplicate rows and resolve duplicate Claim IDs
        df = self._remove_duplicates(df)

        # 7. Impute missing values
        df = self._impute_missing_values(df)

        # 8. Post-cleaning validation checks
        self._run_validation_checks(df)

        self.cleaned_df = df
        return df

    def _normalize_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """Trims whitespace from string columns and standardizes capitalization."""
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                # Replace 'nan' or empty values with actual NaN
                df[col] = df[col].replace({'nan': np.nan, 'None': np.nan, '': np.nan, 'Unknown': np.nan})
        return df

    def _clean_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parses currency strings into clean floats."""
        cols_to_clean = ["Policy_Premium", "Claim_Amount", "Customer_Income", "Customer_Age", "Previous_Claims"]
        for col in cols_to_clean:
            if col in df.columns:
                # Helper to convert dirty currency string to float
                def parse_val(val):
                    if pd.isnull(val):
                        return np.nan
                    val_str = str(val).replace('$', '').replace(',', '').strip()
                    try:
                        return float(val_str)
                    except ValueError:
                        return np.nan

                df[col] = df[col].apply(parse_val)
        return df

    def _standardize_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Resolves inconsistent category names for Gender, Status, and Type."""
        # Gender mapping
        gender_map = {
            'M': 'Male', 'MALE': 'Male', 'Male': 'Male',
            'F': 'Female', 'FEMALE': 'Female', 'Femal': 'Female', 'Female': 'Female'
        }
        df["Customer_Gender"] = df["Customer_Gender"].map(gender_map).fillna("Unknown")

        # Claim Status mapping
        status_map = {
            'Approved': 'Approved', 'Approvedd': 'Approved',
            'Rejected': 'Rejected', 'Rejctd': 'Rejected',
            'Pending': 'Pending', 'Pendng': 'Pending'
        }
        df["Claim_Status"] = df["Claim_Status"].map(status_map).fillna("Pending")

        # Policy Type and Accident Type defaults
        df["Policy_Type"] = df["Policy_Type"].fillna("Auto")
        df["Accident_Type"] = df["Accident_Type"].fillna("N/A")
        df["Claim_Reason"] = df["Claim_Reason"].fillna("Unknown")
        return df

    def _fix_impossible_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Resolves negative ages, incomes, claims, premiums, and extreme outliers."""
        # Age: negative to absolute, missing to median, outliers (>100 or <0) to median
        median_age = df[(df["Customer_Age"] >= 18) & (df["Customer_Age"] <= 90)]["Customer_Age"].median()
        if pd.isnull(median_age):
            median_age = 45.0
            
        df["Customer_Age"] = df["Customer_Age"].apply(
            lambda x: abs(x) if (not pd.isnull(x) and -90 <= x < 0) 
            else (median_age if (pd.isnull(x) or x < 0 or x > 100) else x)
        )

        # Income: negative to positive, missing to median
        median_income = df[df["Customer_Income"] > 0]["Customer_Income"].median()
        if pd.isnull(median_income):
            median_income = 65000.0
        df["Customer_Income"] = df["Customer_Income"].apply(
            lambda x: abs(x) if (not pd.isnull(x) and x < 0)
            else (median_income if (pd.isnull(x) or x <= 0) else x)
        )

        # Policy Premium: negative to absolute, missing to median by Policy Type
        for ptype in df["Policy_Type"].unique():
            med_prem = df[(df["Policy_Type"] == ptype) & (df["Policy_Premium"] > 0)]["Policy_Premium"].median()
            if pd.isnull(med_prem):
                med_prem = 500.0
            df.loc[(df["Policy_Type"] == ptype) & ((df["Policy_Premium"].isnull()) | (df["Policy_Premium"] <= 0)), "Policy_Premium"] = med_prem
        
        # In case some are negative (due to dirty data), take absolute
        df["Policy_Premium"] = df["Policy_Premium"].abs()

        # Claim Amount: negative to absolute, extreme outliers (> $150,000) cap at 99th percentile of normal values or median
        median_claim = df[df["Claim_Amount"] > 0]["Claim_Amount"].median()
        if pd.isnull(median_claim):
            median_claim = 5000.0
            
        df["Claim_Amount"] = df["Claim_Amount"].apply(
            lambda x: abs(x) if (not pd.isnull(x) and x < 0)
            else (median_claim if (pd.isnull(x)) else x)
        )
        
        # Cap claim amount outliers at $150,000 for standard analytics, unless justified, or keep them but flag them. 
        # Here we keep them for fraud modeling (since extreme claims can be fraud) but clean negative values.
        
        # Previous Claims
        df["Previous_Claims"] = df["Previous_Claims"].apply(lambda x: int(abs(x)) if not pd.isnull(x) else 0)
        
        return df

    def _clean_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parses and standardizes dates, resolving sequence issues."""
        # Convert to datetime (setting errors='coerce' turns invalid dates like 2024-15-40 to NaT)
        df["Policy_Start_Date"] = pd.to_datetime(df["Policy_Start_Date"], errors='coerce')
        df["Policy_End_Date"] = pd.to_datetime(df["Policy_End_Date"], errors='coerce')
        df["Claim_Date"] = pd.to_datetime(df["Claim_Date"], errors='coerce')

        # Impute missing Policy Start Dates with the median start date
        median_start = df["Policy_Start_Date"].dropna().median()
        if pd.isnull(median_start):
            median_start = pd.Timestamp("2022-01-01")
        df["Policy_Start_Date"] = df["Policy_Start_Date"].fillna(median_start)

        # Impute/Fix Policy End Date: must be after start date. Default to 1 year after start date
        for idx, row in df.iterrows():
            start_dt = row["Policy_Start_Date"]
            end_dt = row["Policy_End_Date"]
            if pd.isnull(end_dt) or end_dt <= start_dt:
                df.at[idx, "Policy_End_Date"] = start_dt + pd.Timedelta(days=365)

        # Impute missing Claim Dates: set to Policy_Start_Date + 30 days
        for idx, row in df.iterrows():
            start_dt = row["Policy_Start_Date"]
            claim_dt = row["Claim_Date"]
            if pd.isnull(claim_dt):
                df.at[idx, "Claim_Date"] = start_dt + pd.Timedelta(days=30)
            elif claim_dt < start_dt:
                # Fix Claim Date before Policy Start Date (either date error or fraud).
                # For cleaning: if claim date is before policy, and it's not a fraud flag,
                # we can adjust it or leave it if we want to flag it in fraud detection.
                # Let's keep the original claim date to allow the fraud detection module to catch it!
                # But make sure it is a valid datetime format.
                pass

        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Removes exact duplicates and handles duplicate Claim_IDs."""
        # 1. Exact duplicates
        before_exact = len(df)
        df = df.drop_duplicates(keep='first')
        after_exact = len(df)
        print(f"Removed {before_exact - after_exact} exact duplicate rows.")

        # 2. Duplicate Claim IDs with different contents
        # Sort so that records with fewer nulls come first, then drop duplicates on Claim_ID
        before_claim_id = len(df)
        df['null_count'] = df.isnull().sum(axis=1)
        df = df.sort_values(by=["Claim_ID", "null_count", "Claim_Amount"], ascending=[True, True, False])
        df = df.drop_duplicates(subset=["Claim_ID"], keep='first')
        df = df.drop(columns=['null_count'])
        after_claim_id = len(df)
        print(f"Removed {before_claim_id - after_claim_id} duplicate Claim ID records.")

        return df

    def _impute_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final sweep to ensure no missing values remain in essential columns."""
        # Zipcode: fill with mode
        zip_mode = df["Location_Zipcode"].mode()[0] if not df["Location_Zipcode"].empty else "10001"
        df["Location_Zipcode"] = df["Location_Zipcode"].fillna(zip_mode).astype(str)

        # Text columns
        df["Customer_Name"] = df["Customer_Name"].fillna("Unknown Client")
        df["Agent_ID"] = df["Agent_ID"].fillna("AGT0000")
        df["Agent_Name"] = df["Agent_Name"].fillna("Unknown Agent")
        
        return df

    def _run_validation_checks(self, df: pd.DataFrame):
        """Verifies that all columns conform to expected business rules."""
        print("--- RUNNING PREPROCESSING VALIDATION ---")
        assert df["Claim_ID"].is_unique, "Validation Failed: Claim_ID is not unique!"
        assert df.isnull().sum().sum() == 0, f"Validation Failed: Found {df.isnull().sum().sum()} remaining null values!"
        assert (df["Customer_Age"] >= 0).all(), "Validation Failed: Found negative ages!"
        assert (df["Customer_Income"] >= 0).all(), "Validation Failed: Found negative incomes!"
        assert (df["Policy_Premium"] >= 0).all(), "Validation Failed: Found negative premiums!"
        assert (df["Policy_End_Date"] > df["Policy_Start_Date"]).all(), "Validation Failed: Policy End Date is not after Start Date!"
        print("Validation Passed: Cleaned dataset meets all constraints.")

    def save_cleaned_data(self, output_path: str):
        """Saves the cleaned dataset as a CSV file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.cleaned_df.to_csv(output_path, index=False)
        print(f"Cleaned dataset saved successfully to: {output_path}")

if __name__ == "__main__":
    raw_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "Master_Insurance_Data.xlsx"))
    clean_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "processed_insurance_data.csv"))
    
    cleaner = DataCleaner(raw_file)
    cleaner.clean_data()
    cleaner.save_cleaned_data(clean_file)
