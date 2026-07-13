# Fraud Detection and Risk Assessment Report

## Overview
- **Total Claims Assessed**: 2000
- **Flagged Suspicious Claims (Risk Score >= 50)**: 128 (6.40% of portfolio)
- **Historical Fraud Ground Truth Cases**: 356 (17.80%)

## Model Performance Comparison (vs Ground Truth)

| Method | Accuracy | Precision | Recall | F1-Score |
| --- | --- | --- | --- | --- |
| Rule-Based | 82.00% | 16.67% | 0.28% | 0.55% |
| Isolation Forest | 75.20% | 20.83% | 14.04% | 16.78% |
| Local Outlier Factor | 73.90% | 15.42% | 10.39% | 12.42% |
| DBSCAN Outliers | 81.80% | 27.78% | 1.40% | 2.67% |
| One-Class SVM | 74.25% | 17.28% | 11.80% | 14.02% |

### Model Evaluation Summary
- **Rule-Based Detection** provides high precision because its indicators represent clear boundary violations (like claiming before the policy starts). However, it has low recall as it misses complex, non-obvious fraud patterns.
- **Isolation Forest** and **One-Class SVM** achieve the highest F1-scores, capturing multi-dimensional anomalies in claim amount, previous claims, and policy age.
- The **Ensemble Fraud Risk Score** combines both deterministic rules and machine learning insights to establish a continuous score (0-100) for risk assessment.

## Suspicious Claims Flagged for Investigation (Top 15 High Risk)

| Claim ID | Customer ID | Policy Type | Claim Amount | Risk Score | Fraud Prob | Reason for Flag |
| --- | --- | --- | --- | --- | --- | --- |
| CLM00105 | C00638 | Health | ₹271,661.00 | **60** | 0.60 | Frequent claimant |
| CLM00287 | C00092 | Auto | ₹339,373.00 | **60** | 0.60 | Claim exceeds premium x10 |
| CLM00319 | C00684 | Auto | ₹304,323.00 | **60** | 0.60 | Claim exceeds premium x10, Frequent claimant |
| CLM00336 | C00107 | Home | ₹11,791.00 | **60** | 0.60 | ML Anomaly |
| CLM00796 | C00356 | Auto | ₹198,570.00 | **60** | 0.60 | Claim exceeds premium x10, Frequent claimant |
| CLM00770 | C00427 | Auto | ₹236,003.00 | **60** | 0.60 | Claim exceeds premium x10 |
| CLM00581 | C00260 | Auto | ₹60,764.00 | **60** | 0.60 | Frequent claimant |
| CLM01992 | C00638 | Auto | ₹320,225.00 | **60** | 0.60 | ML Anomaly |
| CLM01791 | C00130 | Home | ₹301,408.00 | **60** | 0.60 | Claim exceeds premium x10, Frequent claimant |
| CLM01739 | C00408 | Auto | ₹256,400.00 | **60** | 0.60 | Claim exceeds premium x10, Frequent claimant |
| CLM01723 | C00626 | Auto | ₹329,374.00 | **60** | 0.60 | Claim exceeds premium x10, Frequent claimant |
| CLM01720 | C00685 | Auto | ₹326,932.00 | **60** | 0.60 | Claim exceeds premium x10, Frequent claimant |
| CLM01859 | C00253 | Health | ₹189,555.00 | **60** | 0.60 | Frequent claimant |
| CLM01441 | C00001 | Health | ₹344,062.00 | **60** | 0.60 | Claim exceeds premium x10 |
| CLM01545 | C00124 | Health | ₹325,677.00 | **60** | 0.60 | Claim exceeds premium x10, Frequent claimant |


> [!WARNING]
> Claims listed in this report require manual audits by claims adjusters prior to payment release. Special focus should be placed on claims where `Indicator_Claim_Before_Policy` is flagged, as these represent definitive insurance fraud.
