import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class ClaimsVisualizer:
    """Class to perform Exploratory Data Analysis and generate professional charts."""

    def __init__(self, data_path: str, output_dir: str):
        self.df = pd.read_csv(data_path)
        # Parse dates
        self.df["Policy_Start_Date"] = pd.to_datetime(self.df["Policy_Start_Date"])
        self.df["Policy_End_Date"] = pd.to_datetime(self.df["Policy_End_Date"])
        self.df["Claim_Date"] = pd.to_datetime(self.df["Claim_Date"])
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set styling
        sns.set_theme(style="whitegrid")
        plt.rcParams.update({
            'font.size': 11,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'figure.titlesize': 16,
            'figure.dpi': 150
        })
        self.palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

    def run_all(self):
        """Generates all 26 required plots for the EDA."""
        print(f"Generating 26 EDA plots inside: {self.output_dir}...")
        self.plot_1_gender_distribution()
        self.plot_2_age_distribution()
        self.plot_3_age_vs_claim()
        self.plot_4_income_distribution()
        self.plot_5_income_vs_claim()
        self.plot_6_premium_distribution()
        self.plot_7_premium_vs_claim()
        self.plot_8_policy_type_popularity()
        self.plot_9_claim_status_distribution()
        self.plot_10_claim_reason_frequency()
        self.plot_11_claim_amount_distribution()
        self.plot_12_claim_amount_boxplot_by_type()
        self.plot_13_premium_boxplot_by_type()
        self.plot_14_claim_status_by_policy_type()
        self.plot_15_fraud_flag_distribution()
        self.plot_16_fraud_rate_by_policy_type()
        self.plot_17_fraud_rate_by_gender()
        self.plot_18_fraud_vs_claim_amount()
        self.plot_19_fraud_vs_customer_age()
        self.plot_20_claims_by_state()
        self.plot_21_claim_amount_by_state()
        self.plot_22_yearly_claim_trends()
        self.plot_23_monthly_claim_trends()
        self.plot_24_accident_type_frequency()
        self.plot_25_previous_claims_distribution()
        self.plot_26_correlation_heatmap()
        print("All plots generated successfully.")

    def _save_fig(self, filename: str):
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150)
        plt.close()

    def plot_1_gender_distribution(self):
        plt.figure(figsize=(7, 5))
        counts = self.df["Customer_Gender"].value_counts()
        colors = ["#2b5c8f", "#d95f02", "#7570b3"]
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90, colors=colors[:len(counts)], 
                wedgeprops={'edgecolor': 'w', 'linewidth': 1.5, 'antialiased': True})
        plt.title("Distribution of Claims by Customer Gender")
        self._save_fig("eda_1_gender_distribution.png")

    def plot_2_age_distribution(self):
        plt.figure(figsize=(8, 5))
        sns.histplot(self.df["Customer_Age"], bins=20, kde=True, color="#2b5c8f")
        plt.title("Distribution of Customer Age")
        plt.xlabel("Age")
        plt.ylabel("Count")
        self._save_fig("eda_2_age_distribution.png")

    def plot_3_age_vs_claim(self):
        plt.figure(figsize=(8, 5))
        sns.scatterplot(data=self.df, x="Customer_Age", y="Claim_Amount", alpha=0.6, color="#d95f02")
        plt.title("Customer Age vs Claim Amount")
        plt.xlabel("Age")
        plt.ylabel("Claim Amount (INR)")
        self._save_fig("eda_3_age_vs_claim.png")

    def plot_4_income_distribution(self):
        plt.figure(figsize=(8, 5))
        sns.histplot(self.df["Customer_Income"], bins=20, kde=True, color="#2ca02c")
        plt.title("Distribution of Customer Annual Income")
        plt.xlabel("Annual Income (INR)")
        plt.ylabel("Count")
        self._save_fig("eda_4_income_distribution.png")

    def plot_5_income_vs_claim(self):
        plt.figure(figsize=(8, 5))
        sns.scatterplot(data=self.df, x="Customer_Income", y="Claim_Amount", alpha=0.6, color="#2b5c8f")
        plt.title("Customer Income vs Claim Amount")
        plt.xlabel("Annual Income (INR)")
        plt.ylabel("Claim Amount (INR)")
        self._save_fig("eda_5_income_vs_claim.png")

    def plot_6_premium_distribution(self):
        plt.figure(figsize=(8, 5))
        sns.histplot(self.df["Policy_Premium"], bins=20, kde=True, color="#9467bd")
        plt.title("Distribution of Policy Premium")
        plt.xlabel("Policy Premium (INR)")
        plt.ylabel("Count")
        self._save_fig("eda_6_premium_distribution.png")

    def plot_7_premium_vs_claim(self):
        plt.figure(figsize=(8, 5))
        sns.scatterplot(data=self.df, x="Policy_Premium", y="Claim_Amount", alpha=0.6, color="#d62728")
        plt.title("Policy Premium vs Claim Amount")
        plt.xlabel("Policy Premium (INR)")
        plt.ylabel("Claim Amount (INR)")
        self._save_fig("eda_7_premium_vs_claim.png")

    def plot_8_policy_type_popularity(self):
        plt.figure(figsize=(8, 5))
        sns.countplot(data=self.df, x="Policy_Type", palette="viridis")
        plt.title("Policy Popularity (Total Claims Count by Policy Type)")
        plt.xlabel("Policy Type")
        plt.ylabel("Claims Count")
        self._save_fig("eda_8_policy_type_popularity.png")

    def plot_9_claim_status_distribution(self):
        plt.figure(figsize=(7, 5))
        counts = self.df["Claim_Status"].value_counts()
        colors = ["#2ca02c", "#d62728", "#ff7f0e"]
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90, colors=colors[:len(counts)], 
                wedgeprops={'edgecolor': 'w', 'linewidth': 1.5, 'antialiased': True})
        plt.title("Distribution of Claim Processing Status")
        self._save_fig("eda_9_claim_status_distribution.png")

    def plot_10_claim_reason_frequency(self):
        plt.figure(figsize=(10, 6))
        sns.countplot(data=self.df, y="Claim_Reason", order=self.df["Claim_Reason"].value_counts().index, palette="plasma")
        plt.title("Frequency of Claims by Underwriting Reason")
        plt.xlabel("Count")
        plt.ylabel("Claim Reason")
        self._save_fig("eda_10_claim_reason_frequency.png")

    def plot_11_claim_amount_distribution(self):
        plt.figure(figsize=(8, 5))
        # Log distribution helps view outliers and spread
        sns.histplot(self.df["Claim_Amount"], bins=30, kde=True, color="#2b5c8f")
        plt.title("Distribution of Claim Amount")
        plt.xlabel("Claim Amount (INR)")
        plt.ylabel("Count")
        self._save_fig("eda_11_claim_amount_distribution.png")

    def plot_12_claim_amount_boxplot_by_type(self):
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=self.df, x="Policy_Type", y="Claim_Amount", palette="Set2")
        plt.title("Claim Amount Distribution by Policy Type")
        plt.xlabel("Policy Type")
        plt.ylabel("Claim Amount (INR)")
        self._save_fig("eda_12_claim_amount_boxplot_by_type.png")

    def plot_13_premium_boxplot_by_type(self):
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=self.df, x="Policy_Type", y="Policy_Premium", palette="Set1")
        plt.title("Policy Premium Distribution by Policy Type")
        plt.xlabel("Policy Type")
        plt.ylabel("Policy Premium (INR)")
        self._save_fig("eda_13_premium_boxplot_by_type.png")

    def plot_14_claim_status_by_policy_type(self):
        plt.figure(figsize=(8, 5))
        cross_tab = pd.crosstab(self.df["Policy_Type"], self.df["Claim_Status"], normalize='index') * 100
        cross_tab.plot(kind="bar", stacked=True, color=["#2ca02c", "#ff7f0e", "#d62728"], ax=plt.gca())
        plt.title("Percentage Claim Status Breakdown by Policy Type")
        plt.xlabel("Policy Type")
        plt.ylabel("Percentage (%)")
        plt.legend(title="Claim Status")
        self._save_fig("eda_14_claim_status_by_policy_type.png")

    def plot_15_fraud_flag_distribution(self):
        plt.figure(figsize=(7, 5))
        counts = self.df["Fraud_Flag"].value_counts()
        labels = ["Non-Fraud (0)", "Fraud (1)"]
        colors = ["#2b5c8f", "#d62728"]
        plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, 
                wedgeprops={'edgecolor': 'w', 'linewidth': 1.5, 'antialiased': True})
        plt.title("Historical Claim Fraud Rate Distribution")
        self._save_fig("eda_15_fraud_flag_distribution.png")

    def plot_16_fraud_rate_by_policy_type(self):
        plt.figure(figsize=(8, 5))
        fraud_rates = self.df.groupby("Policy_Type")["Fraud_Flag"].mean() * 100
        sns.barplot(x=fraud_rates.index, y=fraud_rates.values, palette="rocket")
        plt.title("Historical Fraud Rate by Policy Type")
        plt.xlabel("Policy Type")
        plt.ylabel("Fraud Rate (%)")
        self._save_fig("eda_16_fraud_rate_by_policy_type.png")

    def plot_17_fraud_rate_by_gender(self):
        plt.figure(figsize=(8, 5))
        fraud_rates = self.df.groupby("Customer_Gender")["Fraud_Flag"].mean() * 100
        sns.barplot(x=fraud_rates.index, y=fraud_rates.values, palette="coolwarm")
        plt.title("Fraud Rate by Customer Gender")
        plt.xlabel("Gender")
        plt.ylabel("Fraud Rate (%)")
        self._save_fig("eda_17_fraud_rate_by_gender.png")

    def plot_18_fraud_vs_claim_amount(self):
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=self.df, x="Fraud_Flag", y="Claim_Amount", palette="Set1")
        plt.xticks([0, 1], ["Non-Fraud (0)", "Fraud (1)"])
        plt.title("Claim Amount Distribution for Fraud vs Non-Fraud Cases")
        plt.xlabel("Fraud Status")
        plt.ylabel("Claim Amount (INR)")
        self._save_fig("eda_18_fraud_vs_claim_amount.png")

    def plot_19_fraud_vs_customer_age(self):
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=self.df, x="Fraud_Flag", y="Customer_Age", palette="Set2")
        plt.xticks([0, 1], ["Non-Fraud (0)", "Fraud (1)"])
        plt.title("Customer Age Distribution for Fraud vs Non-Fraud Cases")
        plt.xlabel("Fraud Status")
        plt.ylabel("Age")
        self._save_fig("eda_19_fraud_vs_customer_age.png")

    def plot_20_claims_by_state(self):
        plt.figure(figsize=(8, 5))
        sns.countplot(data=self.df, x="Location_State", order=self.df["Location_State"].value_counts().index, palette="mako")
        plt.title("Total Claims Count by State")
        plt.xlabel("State")
        plt.ylabel("Count of Claims")
        self._save_fig("eda_20_claims_by_state.png")

    def plot_21_claim_amount_by_state(self):
        plt.figure(figsize=(8, 5))
        state_sums = self.df.groupby("Location_State")["Claim_Amount"].sum().sort_values(ascending=False)
        sns.barplot(x=state_sums.index, y=state_sums.values / 1e6, palette="mako")
        plt.title("Total Claim Amount Disbursed by State")
        plt.xlabel("State")
        plt.ylabel("Total Claims Paid (INR Millions)")
        self._save_fig("eda_21_claim_amount_by_state.png")

    def plot_22_yearly_claim_trends(self):
        plt.figure(figsize=(8, 5))
        self.df["Claim_Year"] = self.df["Claim_Date"].dt.year
        yearly = self.df.groupby("Claim_Year")["Claim_ID"].count()
        sns.lineplot(x=yearly.index, y=yearly.values, marker="o", color="#2b5c8f", linewidth=2.5)
        plt.title("Claims Frequency Trend by Year")
        plt.xlabel("Year")
        plt.ylabel("Number of Claims")
        plt.xticks(yearly.index)
        self._save_fig("eda_22_yearly_claim_trends.png")

    def plot_23_monthly_claim_trends(self):
        plt.figure(figsize=(10, 5))
        # Claims monthly volume
        self.df["Claim_Month_Year"] = self.df["Claim_Date"].dt.to_period("M")
        monthly = self.df.groupby("Claim_Month_Year")["Claim_ID"].count()
        # Plot as line
        monthly.plot(kind="line", marker="s", color="#d95f02", linewidth=2, ax=plt.gca())
        plt.title("Monthly Claims Volume Trend (Time Series)")
        plt.xlabel("Year-Month")
        plt.ylabel("Number of Claims")
        plt.xticks(rotation=45)
        self._save_fig("eda_23_monthly_claim_trends.png")

    def plot_24_accident_type_frequency(self):
        plt.figure(figsize=(9, 5))
        sns.countplot(data=self.df, x="Accident_Type", order=self.df["Accident_Type"].value_counts().index, palette="cubehelix")
        plt.title("Claim Distribution by Accident Type")
        plt.xlabel("Accident Type")
        plt.ylabel("Count")
        self._save_fig("eda_24_accident_type_frequency.png")

    def plot_25_previous_claims_distribution(self):
        plt.figure(figsize=(8, 5))
        sns.countplot(data=self.df, x="Previous_Claims", palette="viridis")
        plt.title("Distribution of Customer Previous Claims Count")
        plt.xlabel("Number of Previous Claims")
        plt.ylabel("Count of Customers")
        self._save_fig("eda_25_previous_claims_distribution.png")

    def plot_26_correlation_heatmap(self):
        plt.figure(figsize=(8, 6))
        num_cols = ["Customer_Age", "Customer_Income", "Policy_Premium", "Claim_Amount", "Previous_Claims", "Fraud_Flag"]
        corr = self.df[num_cols].corr()
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1, linewidths=0.5)
        plt.title("Correlation Matrix for Key Numerical Fields")
        self._save_fig("eda_26_correlation_heatmap.png")

if __name__ == "__main__":
    data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "processed_insurance_data.csv"))
    images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "images"))
    
    visualizer = ClaimsVisualizer(data_file, images_dir)
    visualizer.run_all()
