import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class RFMAnalyzer:
    """Class to perform RFM (Recency, Frequency, Monetary) analysis and customer segmentation."""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = pd.read_csv(data_path)
        self.df["Claim_Date"] = pd.to_datetime(self.df["Claim_Date"])
        self.df["Policy_Start_Date"] = pd.to_datetime(self.df["Policy_Start_Date"])
        self.df["Policy_End_Date"] = pd.to_datetime(self.df["Policy_End_Date"])

    def analyze(self) -> pd.DataFrame:
        """Runs RFM segmentation, updates the processed CSV, and generates visualizations."""
        print("Starting RFM Customer Segmentation...")
        
        # Reference date is the max Claim Date in the dataset plus 1 day
        ref_date = self.df["Claim_Date"].max() + pd.Timedelta(days=1)
        
        # Aggregate to Customer Level
        customer_df = self.df.groupby("Customer_ID").agg(
            Latest_Claim_Date=("Claim_Date", "max"),
            Frequency=("Claim_ID", "count"),
            Monetary=("Claim_Amount", "sum"),
            Avg_Risk_Score=("Risk_Score", "mean"),
            Any_Fraud=("Fraud_Flag", "max"),
            Customer_Name=("Customer_Name", "first"),
            Customer_Age=("Customer_Age", "first"),
            Customer_Gender=("Customer_Gender", "first"),
            Customer_Income=("Customer_Income", "first")
        ).reset_index()

        # Recency: days since latest claim
        customer_df["Recency"] = (ref_date - customer_df["Latest_Claim_Date"]).dt.days

        # Scoring
        # Recency Score: lower days is better (more active/recent) -> Score 5 to 1
        customer_df["R_Score"] = pd.qcut(customer_df["Recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        
        # Frequency Score: higher is better -> Score 1 to 5. 
        # Since Frequency has a lot of 1s, we will use a custom mapping
        def score_freq(x):
            if x == 1:
                return 1
            elif x == 2:
                return 3
            else:
                return 5
        customer_df["F_Score"] = customer_df["Frequency"].apply(score_freq)

        # Monetary Score: higher total claim amount is scored 1 to 5 (from business view, high payout is high risk/value)
        customer_df["M_Score"] = pd.qcut(customer_df["Monetary"], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

        # Convert categories to integers
        customer_df["R_Score"] = customer_df["R_Score"].astype(int)
        customer_df["F_Score"] = customer_df["F_Score"].astype(int)
        customer_df["M_Score"] = customer_df["M_Score"].astype(int)

        # RFM Score
        customer_df["RFM_Score"] = customer_df["R_Score"] + customer_df["F_Score"] + customer_df["M_Score"]

        # Segmentation Logic
        def assign_segment(row):
            if row["Any_Fraud"] == 1 or row["Avg_Risk_Score"] >= 65:
                return "High Fraud Risk"
            elif row["RFM_Score"] >= 12 and row["M_Score"] >= 4:
                return "VIP"
            elif row["RFM_Score"] >= 9 and row["M_Score"] >= 3:
                return "High Value"
            elif row["R_Score"] <= 2 and row["F_Score"] >= 3:
                return "At Risk"
            elif row["R_Score"] <= 2 and row["F_Score"] == 1:
                return "Dormant"
            else:
                return "Regular"

        customer_df["Customer_Segment"] = customer_df.apply(assign_segment, axis=1)

        # Save customer-level segments
        segments_path = os.path.join(os.path.dirname(self.data_path), "customer_segments.csv")
        customer_df.to_csv(segments_path, index=False)
        print(f"Customer level RFM segments saved to: {segments_path}")

        # Map back to main processed claim dataset
        segment_map = customer_df.set_index("Customer_ID")["Customer_Segment"].to_dict()
        self.df["Customer_Segment"] = self.df["Customer_ID"].map(segment_map)
        
        # Save updated main dataset (maintaining datetime columns formatted as string)
        self.df["Policy_Start_Date"] = self.df["Policy_Start_Date"].dt.strftime("%Y-%m-%d")
        self.df["Policy_End_Date"] = self.df["Policy_End_Date"].dt.strftime("%Y-%m-%d")
        self.df["Claim_Date"] = self.df["Claim_Date"].dt.strftime("%Y-%m-%d")
        
        self.df.to_csv(self.data_path, index=False)
        print(f"Updated main dataset with customer segments: {self.data_path}")

        # Generate segment visualization
        self.plot_segments(customer_df)
        
        return customer_df

    def plot_segments(self, customer_df: pd.DataFrame):
        """Generates a bar chart showing the count of customers in each segment and saves it."""
        plt.figure(figsize=(10, 6))
        
        segment_counts = customer_df["Customer_Segment"].value_counts().sort_values(ascending=False)
        colors = ["#2b5c8f", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
        
        sns.barplot(x=segment_counts.index, y=segment_counts.values, palette="Set2")
        
        plt.title("Distribution of Customer Segments (RFM Analysis)")
        plt.xlabel("Customer Segment")
        plt.ylabel("Number of Customers")
        
        # Annotate bars
        for idx, val in enumerate(segment_counts.values):
            plt.text(idx, val + 2, str(val), ha="center", fontsize=11, fontweight="bold")
            
        images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "images"))
        os.makedirs(images_dir, exist_ok=True)
        out_fig = os.path.join(images_dir, "customer_segments.png")
        plt.tight_layout()
        plt.savefig(out_fig, dpi=150)
        plt.close()
        print(f"Saved segment distribution chart to: {out_fig}")

if __name__ == "__main__":
    processed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "processed_insurance_data.csv"))
    
    analyzer = RFMAnalyzer(processed_path)
    analyzer.analyze()
