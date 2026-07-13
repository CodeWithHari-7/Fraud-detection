import os
import pandas as pd
import numpy as np

class FeatureEngineer:
    """Class to engineer analytical features and indicators for fraud and claims risk analysis."""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = pd.read_csv(data_path)
        # Parse dates
        self.df["Policy_Start_Date"] = pd.to_datetime(self.df["Policy_Start_Date"])
        self.df["Policy_End_Date"] = pd.to_datetime(self.df["Policy_End_Date"])
        self.df["Claim_Date"] = pd.to_datetime(self.df["Claim_Date"])

    def engineer_features(self) -> pd.DataFrame:
        """Run the feature engineering pipeline and return the updated dataframe."""
        df = self.df.copy()

        print("Engineering features...")

        # 1. Policy Age (Days from policy start to claim date)
        df["Policy_Age_Days"] = (df["Claim_Date"] - df["Policy_Start_Date"]).dt.days
        # If claims are before policy start, this will be negative (which we keep as a raw feature, but it's an indicator)
        df["Days_Since_Policy_Start"] = df["Policy_Age_Days"]

        # 2. Customer Lifetime in days (policy duration)
        df["Customer_Lifetime_Days"] = (df["Policy_End_Date"] - df["Policy_Start_Date"]).dt.days

        # 3. Claim to Premium Ratio
        df["Claim_to_Premium_Ratio"] = df["Claim_Amount"] / df["Policy_Premium"]

        # 4. Premium to Claim Ratio
        df["Premium_to_Claim_Ratio"] = df["Policy_Premium"] / df["Claim_Amount"].replace(0, np.nan)
        df["Premium_to_Claim_Ratio"] = df["Premium_to_Claim_Ratio"].fillna(0)

        # 5. Claim Frequency (total claims per customer ID in the dataset)
        freq_map = df["Customer_ID"].value_counts().to_dict()
        df["Claim_Frequency"] = df["Customer_ID"].map(freq_map)

        # 6. Customer Value Index (a metric combining income, premium, and claims history)
        # Higher income + premium = higher value; higher previous claims = lower value
        df["Customer_Value_Index"] = (df["Customer_Income"] * df["Policy_Premium"]) / (1 + df["Previous_Claims"])
        # Log scaling for better distribution
        df["Customer_Value_Index"] = np.log1p(df["Customer_Value_Index"])

        # 7. Fraud Indicators (Binary flags for known high-risk conditions)
        df["Indicator_Claim_Before_Policy"] = (df["Claim_Date"] < df["Policy_Start_Date"]).astype(int)
        df["Indicator_Recent_Policy_High_Claim"] = (
            (df["Policy_Age_Days"] >= 0) & (df["Policy_Age_Days"] <= 30) & (df["Claim_Amount"] > 10000)
        ).astype(int)
        df["Indicator_Claim_Exceeds_Premium"] = (df["Claim_Amount"] > df["Policy_Premium"]).astype(int)
        df["Indicator_Extreme_Claim"] = (df["Claim_Amount"] > 50000).astype(int)
        df["Indicator_Repeat_Claimant"] = (df["Previous_Claims"] >= 3).astype(int)

        # 8. Composite Risk Score (scaled 0-100)
        # Weights:
        # - Claim before policy: 35 points
        # - Recent policy + high claim: 20 points
        # - Claim exceeds premium: 15 points
        # - Repeat claimant: 10 points
        # - Claim frequency > 1: 10 points
        # - Customer Age is very young (< 25) or very old (> 75): 10 points
        
        age_risk = df["Customer_Age"].apply(lambda x: 1 if (x < 25 or x > 75) else 0)
        freq_risk = df["Claim_Frequency"].apply(lambda x: 1 if x > 1 else 0)
        
        raw_risk = (
            df["Indicator_Claim_Before_Policy"] * 35 +
            df["Indicator_Recent_Policy_High_Claim"] * 20 +
            df["Indicator_Claim_Exceeds_Premium"] * 15 +
            df["Indicator_Repeat_Claimant"] * 10 +
            freq_risk * 10 +
            age_risk * 10
        )
        # Scale to 0-100
        df["Risk_Score"] = raw_risk.clip(0, 100)

        # Re-format dates back to strings for CSV compatibility
        df["Policy_Start_Date"] = df["Policy_Start_Date"].dt.strftime("%Y-%m-%d")
        df["Policy_End_Date"] = df["Policy_End_Date"].dt.strftime("%Y-%m-%d")
        df["Claim_Date"] = df["Claim_Date"].dt.strftime("%Y-%m-%d")

        print("Feature engineering completed successfully.")
        return df

    def save_features(self, output_path: str):
        """Saves the dataframe with engineered features."""
        df_feat = self.engineer_features()
        df_feat.to_csv(output_path, index=False)
        print(f"Features saved successfully to: {output_path}")

if __name__ == "__main__":
    processed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "processed_insurance_data.csv"))
    
    fe = FeatureEngineer(processed_path)
    fe.save_features(processed_path)
