# Data Profiling Report: Master Insurance Claims Dataset

## Overview
- **Total Records**: 1025
- **Total Columns**: 23
- **Duplicate Rows**: 15

## Key Data Quality Issues Identified

### 1. Missing Values
| Column Name | Missing Count | Percentage |
| --- | --- | --- |
| `Customer_Age` | 41 | 4.00% |
| `Customer_Gender` | 138 | 13.46% |
| `Customer_Income` | 53 | 5.17% |
| `Policy_Premium` | 30 | 2.93% |
| `Claim_Date` | 32 | 3.12% |
| `Claim_Amount` | 27 | 2.63% |
| `Claim_Status` | 150 | 14.63% |
| `Accident_Type` | 144 | 14.05% |

### 2. Duplicate Identifiers
- **Duplicate Claim IDs**: 25
- **Duplicate Customer IDs**: 456

### 3. Date Anomalies
- **Unparseable Policy Start Dates**: 33
- **Unparseable Policy End Dates**: 0
- **Unparseable Claim Dates**: 32
- **Policy End Date before Policy Start Date**: 22
- **Claim Date before Policy Start Date**: 89
- **Future Dates**: 0

### 4. Datatype Inconsistencies
- **Column `Policy_Premium`** contains `58` records with currency symbols or commas. Inferred Pandas dtype: `object`
- **Column `Claim_Amount`** contains `19` records with currency symbols or commas. Inferred Pandas dtype: `object`
- **Column `Location_Zipcode`** contains mixed python types: `{'int': 1025}`

### 5. Negative Values (Impossible values)
| Column Name | Negative Value Count |
| --- | --- |
| `Customer_Age` | 16 |
| `Customer_Income` | 33 |
| `Policy_Premium` | 26 |
| `Claim_Amount` | 12 |

### 6. Inconsistent Categorical Labels
- **Column `Customer_Gender`** contains non-standard labels: `['FEMALE', 'Femal', 'F', 'MALE', 'M']` (Total inconsistent: 644)
- **Column `Claim_Status`** contains non-standard labels: `['Approvedd', 'Pendng', 'Rejctd']` (Total inconsistent: 445)

### 7. Statistical Outliers (IQR Method)
| Column Name | Outlier Count | IQR Upper Bound | IQR Lower Bound |
| --- | --- | --- | --- |
| `Customer_Age` | 26 | 89.00 | 1.00 |
| `Customer_Income` | 34 | 136190.75 | -8051.25 |

### 8. High Cardinality Columns
| Column Name | Unique Value Count | Is High Cardinality? |
| --- | --- | --- |
| `Claim_ID` | 1000 | Yes |
| `Customer_ID` | 569 | Yes |
| `Customer_Name` | 363 | Yes |
| `Customer_Income` | 926 | Yes |
| `Policy_Number` | 1000 | Yes |
| `Policy_Start_Date` | 768 | Yes |
| `Policy_End_Date` | 755 | Yes |
| `Policy_Premium` | 962 | Yes |
| `Claim_Date` | 777 | Yes |
| `Claim_Amount` | 869 | Yes |

## Descriptive Column Statistics

| Column | Count | Mean | Median | Std Dev | Min | Max | Skewness | Kurtosis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Customer_Age` | 984 | 46.04 | 45.00 | 18.13 | 5.00 | 150.00 | 1.36 | 6.23 |
| `Customer_Income` | 972 | 64349.74 | 64430.00 | 24677.41 | 10519.00 | 141972.00 | 0.07 | -0.42 |
| `Policy_Start_Date` | 945 | 20220644.44 | 20220704.00 | 14471.36 | 20200101.00 | 20241540.00 | -0.01 | -1.34 |
| `Policy_End_Date` | 1025 | 20230217.87 | 20230616.00 | 14378.10 | 20200225.00 | 20251226.00 | -0.02 | -1.29 |
| `Policy_Premium` | 995 | 501.59 | 498.34 | 143.26 | 100.00 | 886.96 | 0.03 | -0.21 |
| `Claim_Date` | 942 | 20225013.39 | 20221210.50 | 15153.38 | 20191219.00 | 20260113.00 | 0.04 | -1.02 |
| `Claim_Amount` | 998 | 9323.61 | 5230.07 | 27400.90 | 100.00 | 314235.79 | 7.61 | 64.64 |

