import os
import pandas as pd
import numpy as np

class ProductPerformanceAnalyzer:
    """Class to analyze insurance policy product performance, profitability, and risk."""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = pd.read_csv(data_path)

    def analyze(self) -> pd.DataFrame:
        """Run the product performance analysis and save reports."""
        print("Starting Product Performance Analysis...")
        
        # Deduplicate policies to get actual unique policy premiums collected
        unique_policies = self.df.drop_duplicates(subset=["Policy_Number"])
        premium_collected = unique_policies.groupby("Policy_Type")["Policy_Premium"].sum()
        policy_count = unique_policies.groupby("Policy_Type")["Policy_Number"].count()
        
        # Claims Paid (only for Approved claims, or total claim claims? Let's use Approved claims for Claims Paid, 
        # and also calculate total claim amounts filed)
        approved_claims = self.df[self.df["Claim_Status"] == "Approved"]
        claims_paid = approved_claims.groupby("Policy_Type")["Claim_Amount"].sum()
        approved_count = approved_claims.groupby("Policy_Type")["Claim_ID"].count()
        
        # Total Claims filed
        total_claims_filed = self.df.groupby("Policy_Type")["Claim_ID"].count()
        total_claims_amount_filed = self.df.groupby("Policy_Type")["Claim_Amount"].sum()
        
        # Fraud claims
        fraud_claims = self.df[self.df["Fraud_Flag"] == 1]
        fraud_count = fraud_claims.groupby("Policy_Type")["Claim_ID"].count()
        
        # Combine metrics into a single DataFrame
        product_df = pd.DataFrame({
            "Unique_Policies": policy_count,
            "Total_Premium_Collected": premium_collected,
            "Total_Claims_Filed": total_claims_filed,
            "Total_Claims_Amount_Filed": total_claims_amount_filed,
            "Approved_Claims_Count": approved_count,
            "Total_Claims_Paid": claims_paid,
            "Fraud_Claims_Count": fraud_count
        }).fillna(0)
        
        # Calculate derived KPIs
        product_df["Loss_Ratio"] = product_df["Total_Claims_Paid"] / product_df["Total_Premium_Collected"]
        product_df["Net_Profit"] = product_df["Total_Premium_Collected"] - product_df["Total_Claims_Paid"]
        product_df["Average_Claim_Amount_Paid"] = product_df["Total_Claims_Paid"] / product_df["Approved_Claims_Count"].replace(0, 1)
        product_df["Claim_Approval_Rate"] = (product_df["Approved_Claims_Count"] / product_df["Total_Claims_Filed"]) * 100
        product_df["Fraud_Rate"] = (product_df["Fraud_Claims_Count"] / product_df["Total_Claims_Filed"]) * 100
        
        # Formatting and rounding
        product_df = product_df.round({
            "Total_Premium_Collected": 2,
            "Total_Claims_Amount_Filed": 2,
            "Total_Claims_Paid": 2,
            "Loss_Ratio": 4,
            "Net_Profit": 2,
            "Average_Claim_Amount_Paid": 2,
            "Claim_Approval_Rate": 2,
            "Fraud_Rate": 2
        })
        
        # Reset index to make Policy_Type a column
        product_df = product_df.reset_index()

        # Save to CSV
        output_csv = os.path.join(os.path.dirname(self.data_path), "product_performance.csv")
        product_df.to_csv(output_csv, index=False)
        print(f"Product performance statistics saved to: {output_csv}")

        # Generate markdown report
        self.generate_markdown_report(product_df)

        return product_df

    def generate_markdown_report(self, df: pd.DataFrame):
        """Generates a professional markdown report detailing product performance."""
        report_path = os.path.abspath(os.path.join(os.path.dirname(self.data_path), "..", "..", "reports", "product_performance_report.md"))
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        # Calculate total corporate KPIs
        total_premium = df["Total_Premium_Collected"].sum()
        total_claims_paid = df["Total_Claims_Paid"].sum()
        corporate_loss_ratio = total_claims_paid / total_premium
        corporate_profit = total_premium - total_claims_paid
        total_claims_filed = df["Total_Claims_Filed"].sum()
        total_fraud = df["Fraud_Claims_Count"].sum()
        corporate_fraud_rate = (total_fraud / total_claims_filed) * 100

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Product Performance & Profitability Report\n\n")
            f.write("## Corporate Claims KPIs\n")
            f.write(f"- **Total Portfolio Premium Collected**: ₹{total_premium:,.2f}\n")
            f.write(f"- **Total Claims Payout (Claims Paid)**: ₹{total_claims_paid:,.2f}\n")
            f.write(f"- **Corporate Loss Ratio**: {corporate_loss_ratio * 100:.2f}%\n")
            f.write(f"- **Net Operating Underwriting Profit**: ₹{corporate_profit:,.2f}\n")
            f.write(f"- **Total Claims Processed**: {total_claims_filed}\n")
            f.write(f"- **Total Flagged Fraud Cases**: {total_fraud} ({corporate_fraud_rate:.2f}% of claims)\n\n")

            f.write("## Policy Product Comparison\n\n")
            f.write("| Policy Type | Policies | Premium Collected | Claims Paid | Loss Ratio | Net Profit | Avg Claim Paid | Approval Rate | Fraud Rate |\n")
            f.write("| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
            for _, row in df.iterrows():
                f.write(f"| **{row['Policy_Type']}** | {int(row['Unique_Policies'])} | ₹{row['Total_Premium_Collected']:,.2f} | ₹{row['Total_Claims_Paid']:,.2f} | {row['Loss_Ratio']*100:.2f}% | ₹{row['Net_Profit']:,.2f} | ₹{row['Average_Claim_Amount_Paid']:,.2f} | {row['Claim_Approval_Rate']:.2f}% | {row['Fraud_Rate']:.2f}% |\n")
            f.write("\n")

            f.write("## Business Insights\n\n")
            
            # Identify highest and lowest loss ratios
            highest_loss_row = df.loc[df["Loss_Ratio"].idxmax()]
            lowest_loss_row = df.loc[df["Loss_Ratio"].idxmin()]
            
            f.write(f"### 1. Loss Ratio and Risk Analysis\n")
            f.write(f"- The **{highest_loss_row['Policy_Type']}** product represents the highest loss ratio at **{highest_loss_row['Loss_Ratio']*100:.2f}%**, indicating that it returns the largest share of premiums back as claim payments. This product requires premium rate reviews.\n")
            f.write(f"- The **{lowest_loss_row['Policy_Type']}** product has the lowest loss ratio at **{lowest_loss_row['Loss_Ratio']*100:.2f}%**, making it the most profitable product line in the portfolio.\n\n")
            
            # Profitability
            f.write(f"### 2. Profitability and Growth\n")
            f.write(f"- **Net Profits** are led by the **{df.loc[df['Net_Profit'].idxmax()]['Policy_Type']}** segment with a net of **₹{df.loc[df['Net_Profit'].idxmax()]['Net_Profit']:,.2f}**.\n")
            f.write(f"- Dynamic adjustments to underwriting limits, particularly in segments with high outliers, will shield net reserves.\n\n")

            # Fraud rates
            highest_fraud_row = df.loc[df["Fraud_Rate"].idxmax()]
            f.write(f"### 3. Claims Fraud Susceptibility\n")
            f.write(f"- **{highest_fraud_row['Policy_Type']}** policies suffer from the highest rate of fraud at **{highest_fraud_row['Fraud_Rate']:.2f}%** of all claims.\n")
            f.write(f"- Claims audit triggers should prioritize **{highest_fraud_row['Policy_Type']}** claims, particularly those filed within short intervals after policy activation.\n")

        print(f"Product Performance Report generated successfully at: {report_path}")

if __name__ == "__main__":
    processed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "processed_insurance_data.csv"))
    
    analyzer = ProductPerformanceAnalyzer(processed_path)
    analyzer.analyze()
