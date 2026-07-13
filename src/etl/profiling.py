import os
import re
import numpy as np
import pandas as pd
from typing import Dict, Any, List

class DataProfiler:
    """Class to profile raw insurance claim datasets and identify data quality issues."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = pd.read_excel(file_path)
        self.issues: Dict[str, Any] = {}
        self.stats: Dict[str, Any] = {}

    def profile_data(self) -> Dict[str, Any]:
        """Runs the entire profiling suite on the dataset."""
        self._check_missing_values()
        self._check_duplicate_rows()
        self._check_duplicate_ids()
        self._check_invalid_dates()
        self._check_incorrect_datatypes()
        self._check_negative_values()
        self._check_invalid_categoricals()
        self._check_outliers()
        self._check_high_cardinality()
        self._calculate_statistics()
        return {
            "issues": self.issues,
            "stats": self.stats,
            "shape": self.df.shape
        }

    def _check_missing_values(self):
        null_counts = self.df.isnull().sum()
        null_pct = (null_counts / len(self.df)) * 100
        self.issues["missing_values"] = {
            col: {"count": int(count), "percentage": float(pct)}
            for col, count, pct in zip(self.df.columns, null_counts, null_pct) if count > 0
        }

    def _check_duplicate_rows(self):
        dups = self.df.duplicated().sum()
        self.issues["duplicate_rows"] = int(dups)

    def _check_duplicate_ids(self):
        claim_id_dups = self.df["Claim_ID"].duplicated().sum()
        customer_id_dups = self.df["Customer_ID"].duplicated().sum()
        self.issues["duplicate_ids"] = {
            "Claim_ID_duplicates": int(claim_id_dups),
            "Customer_ID_duplicates": int(customer_id_dups)
        }

    def _check_invalid_dates(self):
        invalid_start_dates = []
        invalid_end_dates = []
        invalid_claim_dates = []
        date_sequence_errors = 0
        claim_before_policy_errors = 0
        future_dates = 0
        
        current_time = pd.Timestamp.now()

        for idx, row in self.df.iterrows():
            # Validate Policy Start Date
            start_val = row["Policy_Start_Date"]
            start_parsed = None
            try:
                if pd.isnull(start_val) or start_val == "Unknown":
                    invalid_start_dates.append((idx, start_val, "Missing/Unknown"))
                else:
                    start_parsed = pd.to_datetime(start_val)
                    if start_parsed > current_time:
                        future_dates += 1
            except Exception as e:
                invalid_start_dates.append((idx, start_val, str(e)))

            # Validate Policy End Date
            end_val = row["Policy_End_Date"]
            end_parsed = None
            try:
                if pd.isnull(end_val):
                    invalid_end_dates.append((idx, end_val, "Missing"))
                else:
                    end_parsed = pd.to_datetime(end_val)
            except Exception as e:
                invalid_end_dates.append((idx, end_val, str(e)))

            # Validate Claim Date
            claim_val = row["Claim_Date"]
            claim_parsed = None
            try:
                if pd.isnull(claim_val):
                    invalid_claim_dates.append((idx, claim_val, "Missing"))
                else:
                    claim_parsed = pd.to_datetime(claim_val)
            except Exception as e:
                invalid_claim_dates.append((idx, claim_val, str(e)))

            # Logic validations if parsed successfully
            if start_parsed and end_parsed:
                if start_parsed > end_parsed:
                    date_sequence_errors += 1
            
            if start_parsed and claim_parsed:
                if claim_parsed < start_parsed:
                    claim_before_policy_errors += 1

        self.issues["invalid_dates"] = {
            "invalid_policy_start_count": len(invalid_start_dates),
            "invalid_policy_end_count": len(invalid_end_dates),
            "invalid_claim_date_count": len(invalid_claim_dates),
            "policy_end_before_start_count": date_sequence_errors,
            "claim_before_policy_start_count": claim_before_policy_errors,
            "future_dates_count": future_dates
        }

    def _check_incorrect_datatypes(self):
        incorrect_types = {}
        for col in ["Policy_Premium", "Claim_Amount"]:
            string_patterns = self.df[col].astype(str).str.contains(r'\$|,', regex=True).sum()
            incorrect_types[col] = {
                "inferred_type": str(self.df[col].dtype),
                "records_with_currency_symbols": int(string_patterns)
            }
        
        # Check Zipcode datatype mismatch (should be clean string, but often mixed)
        zip_types = self.df["Location_Zipcode"].apply(lambda x: type(x).__name__).value_counts().to_dict()
        incorrect_types["Location_Zipcode"] = {
            "type_distribution": {str(k): int(v) for k, v in zip_types.items()}
        }
        
        self.issues["incorrect_datatypes"] = incorrect_types

    def _check_negative_values(self):
        negatives = {}
        numeric_cols = ["Customer_Age", "Customer_Income", "Policy_Premium", "Claim_Amount", "Previous_Claims"]
        for col in numeric_cols:
            neg_count = 0
            for val in self.df[col].dropna():
                try:
                    # Strip symbols if string
                    val_clean = float(str(val).replace('$', '').replace(',', ''))
                    if val_clean < 0:
                        neg_count += 1
                except ValueError:
                    pass
            negatives[col] = neg_count
        self.issues["negative_values"] = negatives

    def _check_invalid_categoricals(self):
        categoricals = {
            "Customer_Gender": ["Male", "Female"],
            "Claim_Status": ["Approved", "Rejected", "Pending"],
            "Policy_Type": ["Auto", "Home", "Health", "Life"]
        }
        invalid_cats = {}
        for col, valid_vals in categoricals.items():
            unique_vals = self.df[col].dropna().unique()
            invalids = [str(val) for val in unique_vals if str(val) not in valid_vals]
            invalid_cats[col] = {
                "unique_values_found": [str(x) for x in unique_vals],
                "invalid_values": invalids,
                "invalid_count": int(self.df[col].astype(str).apply(lambda x: x not in valid_vals and x != 'nan').sum())
            }
        self.issues["invalid_categoricals"] = invalid_cats

    def _check_outliers(self):
        outliers = {}
        # We check age, income, and clean claim/premium values using IQR method
        for col in ["Customer_Age", "Customer_Income"]:
            series = pd.to_numeric(self.df[col], errors='coerce').dropna()
            if len(series) > 0:
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                outlier_count = ((series < lower) | (series > upper)).sum()
                outliers[col] = {
                    "outlier_count": int(outlier_count),
                    "lower_bound": float(lower),
                    "upper_bound": float(upper)
                }
        self.issues["outliers"] = outliers

    def _check_high_cardinality(self):
        cardinality = {}
        for col in self.df.columns:
            unique_count = self.df[col].nunique()
            cardinality[col] = {
                "unique_count": int(unique_count),
                "is_high_cardinality": bool(unique_count > 100 and unique_count != len(self.df))
            }
        self.issues["high_cardinality"] = cardinality

    def _calculate_statistics(self):
        for col in self.df.columns:
            # Try to convert to numeric to get descriptive stats
            series = pd.to_numeric(
                self.df[col].astype(str).str.replace('$', '').str.replace(',', '').str.replace('-', ''),
                errors='coerce'
            ).dropna()
            
            if len(series) > 0 and self.df[col].nunique() > 10: # Only for numerical columns
                self.stats[col] = {
                    "count": int(series.count()),
                    "mean": float(series.mean()),
                    "std": float(series.std()),
                    "min": float(series.min()),
                    "25%": float(series.quantile(0.25)),
                    "50%": float(series.median()),
                    "75%": float(series.quantile(0.75)),
                    "max": float(series.max()),
                    "skewness": float(series.skew()) if not pd.isnull(series.skew()) else 0.0,
                    "kurtosis": float(series.kurtosis()) if not pd.isnull(series.kurtosis()) else 0.0
                }

    def generate_markdown_report(self, report_path: str):
        """Generates a beautiful data profiling report in markdown format."""
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Data Profiling Report: Master Insurance Claims Dataset\n\n")
            f.write("## Overview\n")
            f.write(f"- **Total Records**: {self.df.shape[0]}\n")
            f.write(f"- **Total Columns**: {self.df.shape[1]}\n")
            f.write(f"- **Duplicate Rows**: {self.issues['duplicate_rows']}\n\n")
            
            f.write("## Key Data Quality Issues Identified\n\n")
            
            # Missing values
            f.write("### 1. Missing Values\n")
            f.write("| Column Name | Missing Count | Percentage |\n")
            f.write("| --- | --- | --- |\n")
            for col, item in self.issues["missing_values"].items():
                f.write(f"| `{col}` | {item['count']} | {item['percentage']:.2f}% |\n")
            f.write("\n")
            
            # Duplicate IDs
            f.write("### 2. Duplicate Identifiers\n")
            f.write(f"- **Duplicate Claim IDs**: {self.issues['duplicate_ids']['Claim_ID_duplicates']}\n")
            f.write(f"- **Duplicate Customer IDs**: {self.issues['duplicate_ids']['Customer_ID_duplicates']}\n\n")
            
            # Invalid Dates
            f.write("### 3. Date Anomalies\n")
            dates = self.issues["invalid_dates"]
            f.write(f"- **Unparseable Policy Start Dates**: {dates['invalid_policy_start_count']}\n")
            f.write(f"- **Unparseable Policy End Dates**: {dates['invalid_policy_end_count']}\n")
            f.write(f"- **Unparseable Claim Dates**: {dates['invalid_claim_date_count']}\n")
            f.write(f"- **Policy End Date before Policy Start Date**: {dates['policy_end_before_start_count']}\n")
            f.write(f"- **Claim Date before Policy Start Date**: {dates['claim_before_policy_start_count']}\n")
            f.write(f"- **Future Dates**: {dates['future_dates_count']}\n\n")
            
            # Incorrect datatypes
            f.write("### 4. Datatype Inconsistencies\n")
            for col, item in self.issues["incorrect_datatypes"].items():
                if "records_with_currency_symbols" in item:
                    f.write(f"- **Column `{col}`** contains `{item['records_with_currency_symbols']}` records with currency symbols or commas. Inferred Pandas dtype: `{item['inferred_type']}`\n")
                elif "type_distribution" in item:
                    f.write(f"- **Column `{col}`** contains mixed python types: `{item['type_distribution']}`\n")
            f.write("\n")
            
            # Negative Values
            f.write("### 5. Negative Values (Impossible values)\n")
            f.write("| Column Name | Negative Value Count |\n")
            f.write("| --- | --- |\n")
            for col, count in self.issues["negative_values"].items():
                if count > 0:
                    f.write(f"| `{col}` | {count} |\n")
            f.write("\n")

            # Invalid Categorical Labels
            f.write("### 6. Inconsistent Categorical Labels\n")
            for col, item in self.issues["invalid_categoricals"].items():
                if len(item["invalid_values"]) > 0:
                    f.write(f"- **Column `{col}`** contains non-standard labels: `{item['invalid_values']}` (Total inconsistent: {item['invalid_count']})\n")
            f.write("\n")

            # Outliers
            f.write("### 7. Statistical Outliers (IQR Method)\n")
            f.write("| Column Name | Outlier Count | IQR Upper Bound | IQR Lower Bound |\n")
            f.write("| --- | --- | --- | --- |\n")
            for col, item in self.issues["outliers"].items():
                f.write(f"| `{col}` | {item['outlier_count']} | {item['upper_bound']:.2f} | {item['lower_bound']:.2f} |\n")
            f.write("\n")
            
            # High Cardinality
            f.write("### 8. High Cardinality Columns\n")
            f.write("| Column Name | Unique Value Count | Is High Cardinality? |\n")
            f.write("| --- | --- | --- |\n")
            for col, item in self.issues["high_cardinality"].items():
                if item["is_high_cardinality"]:
                    f.write(f"| `{col}` | {item['unique_count']} | Yes |\n")
            f.write("\n")

            # Numerical Column Statistics
            f.write("## Descriptive Column Statistics\n\n")
            f.write("| Column | Count | Mean | Median | Std Dev | Min | Max | Skewness | Kurtosis |\n")
            f.write("| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
            for col, item in self.stats.items():
                f.write(f"| `{col}` | {item['count']} | {item['mean']:.2f} | {item['50%']:.2f} | {item['std']:.2f} | {item['min']:.2f} | {item['max']:.2f} | {item['skewness']:.2f} | {item['kurtosis']:.2f} |\n")
            f.write("\n")

        print(f"Data Profiling Report generated successfully at: {report_path}")

if __name__ == "__main__":
    raw_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "Master_Insurance_Data.xlsx"))
    report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "reports", "data_profiling_report.md"))
    
    profiler = DataProfiler(raw_path)
    profiler.profile_data()
    profiler.generate_markdown_report(report_path)
