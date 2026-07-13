-- SQL Analytics Script: Aggregations, Window Functions, CTEs, and Views
-- Suitable for PostgreSQL, SQLite, and SQL Server (T-SQL)

--------------------------------------------------------------------------------
-- 1. ANALYTICAL VIEWS
--------------------------------------------------------------------------------

-- View: Complete Denormalized Claims View
CREATE VIEW IF NOT EXISTS v_ClaimsSummary AS
SELECT 
    f.Claim_Key,
    f.Claim_ID,
    c.Customer_ID,
    c.Customer_Name,
    c.Customer_Age,
    c.Customer_Gender,
    c.Customer_Income,
    p.Policy_Number,
    p.Policy_Type,
    p.Policy_Premium,
    p.Policy_Start_Date,
    p.Policy_End_Date,
    l.City,
    l.State,
    l.Zipcode,
    a.Agent_ID,
    a.Agent_Name,
    t.Claim_Reason,
    t.Accident_Type,
    d.Full_Date AS Claim_Date,
    f.Claim_Amount,
    f.Claim_Status,
    f.Fraud_Flag
FROM Fact_Claims f
JOIN DimCustomer c ON f.Customer_Key = c.Customer_Key
JOIN DimPolicy p ON f.Policy_Key = p.Policy_Key
JOIN DimLocation l ON f.Location_Key = l.Location_Key
JOIN DimAgent a ON f.Agent_Key = a.Agent_Key
JOIN DimClaimType t ON f.Claim_Type_Key = t.Claim_Type_Key
JOIN DimDate d ON f.Claim_Date_Key = d.Date_Key;


-- View: High Risk Fraud Claims (Risk Score and Probability summary)
CREATE VIEW IF NOT EXISTS v_FraudRiskAssessment AS
SELECT 
    Claim_ID,
    Customer_ID,
    Customer_Name,
    Policy_Type,
    Claim_Amount,
    Policy_Premium,
    Claim_Status,
    Fraud_Flag
FROM v_ClaimsSummary
WHERE Claim_Amount > Policy_Premium * 5 
   OR Claim_Status = 'Rejected' 
   OR Fraud_Flag = 1;

--------------------------------------------------------------------------------
-- 2. PORTFOLIO AND CLAIMS KPI QUERIES
--------------------------------------------------------------------------------

-- Query: Key Metrics Aggregate Summary
SELECT 
    COUNT(DISTINCT Customer_ID) AS Total_Customers,
    COUNT(DISTINCT Policy_Number) AS Total_Policies,
    SUM(DISTINCT Policy_Premium) AS Total_Premium_Collected,
    COUNT(Claim_ID) AS Total_Claims_Filed,
    AVG(Claim_Amount) AS Average_Claim_Amount,
    SUM(CASE WHEN Claim_Status = 'Approved' THEN Claim_Amount ELSE 0 END) AS Total_Claims_Paid,
    SUM(CASE WHEN Fraud_Flag = 1 THEN 1 ELSE 0 END) AS Fraud_Cases,
    ROUND(CAST(SUM(CASE WHEN Fraud_Flag = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(Claim_ID) * 100, 2) AS Fraud_Rate_Percentage,
    ROUND(SUM(CASE WHEN Claim_Status = 'Approved' THEN Claim_Amount ELSE 0 END) / SUM(DISTINCT Policy_Premium) * 100, 2) AS Portfolio_Loss_Ratio_Percentage
FROM v_ClaimsSummary;

--------------------------------------------------------------------------------
-- 3. WINDOW FUNCTIONS AND AGGREGATIONS
--------------------------------------------------------------------------------

-- Query: Rank Agents by Underwriting Net Profit (Premium collected minus Claims paid)
-- Uses DENSE_RANK() window function to rank agent profitability
WITH AgentProfitability AS (
    SELECT 
        Agent_ID,
        Agent_Name,
        SUM(DISTINCT Policy_Premium) AS Total_Premium,
        SUM(CASE WHEN Claim_Status = 'Approved' THEN Claim_Amount ELSE 0 END) AS Total_Payout
    FROM v_ClaimsSummary
    GROUP BY Agent_ID, Agent_Name
)
SELECT 
    Agent_ID,
    Agent_Name,
    Total_Premium,
    Total_Payout,
    (Total_Premium - Total_Payout) AS Underwriting_Net_Profit,
    DENSE_RANK() OVER (ORDER BY (Total_Premium - Total_Payout) DESC) as Profitability_Rank
FROM AgentProfitability;


-- Query: Cumulative Claims Over Time per Customer
-- Uses SUM() OVER (PARTITION BY ... ORDER BY ...) for running total calculations
SELECT 
    Customer_ID,
    Customer_Name,
    Claim_Date,
    Claim_Amount,
    SUM(Claim_Amount) OVER (PARTITION BY Customer_ID ORDER BY Claim_Date ROWS UNBOUNDED PRECEDING) AS Cumulative_Claim_Amount_Spent,
    ROW_NUMBER() OVER (PARTITION BY Customer_ID ORDER BY Claim_Date) AS Claim_Sequence_Number
FROM v_ClaimsSummary
ORDER BY Customer_ID, Claim_Date;

--------------------------------------------------------------------------------
-- 4. CTE (COMMON TABLE EXPRESSIONS) FOR SEGMENTATION AND COHORT
--------------------------------------------------------------------------------

-- Query: Customer Segment Analytics (Average Metrics per Segment)
-- Demonstrates CTE chaining and complex filters
WITH CustomerAggregates AS (
    SELECT 
        Customer_ID,
        COUNT(Claim_ID) as Claims_Count,
        SUM(Claim_Amount) as Total_Monetary,
        AVG(Customer_Income) as Avg_Income
    FROM v_ClaimsSummary
    GROUP BY Customer_ID
),
SegmentStats AS (
    SELECT 
        CASE 
            WHEN Claims_Count >= 3 AND Total_Monetary > 20000 THEN 'VIP / High Value'
            WHEN Claims_Count >= 2 THEN 'Regular Claimant'
            ELSE 'Single Event Claimant'
        END AS RFM_Claim_Segment,
        Customer_ID,
        Total_Monetary,
        Avg_Income
    FROM CustomerAggregates
)
SELECT 
    RFM_Claim_Segment,
    COUNT(Customer_ID) AS Customers_Count,
    ROUND(AVG(Total_Monetary), 2) AS Average_Claims_Total,
    ROUND(AVG(Avg_Income), 2) AS Average_Customer_Income
FROM SegmentStats
GROUP BY RFM_Claim_Segment;

--------------------------------------------------------------------------------
-- 5. FRAUD DETECTION TARGETED QUERIES
--------------------------------------------------------------------------------

-- Query: Duplicate Customer Claims Filed on Same Date
-- Fraud indicator: Identifying claims registered by the same customer on the exact same date
SELECT 
    Customer_ID,
    Customer_Name,
    Claim_Date,
    COUNT(Claim_ID) AS Claims_Filed_On_Day,
    GROUP_CONCAT(Claim_ID) AS Claim_IDs,
    SUM(Claim_Amount) AS Total_Claimed_On_Day
FROM v_ClaimsSummary
GROUP BY Customer_ID, Customer_Name, Claim_Date
HAVING COUNT(Claim_ID) > 1;


-- Query: Claims Occurred Before Policy Start Date (Definitive Fraud)
SELECT 
    Claim_ID,
    Customer_ID,
    Customer_Name,
    Policy_Number,
    Policy_Start_Date,
    Claim_Date,
    Claim_Amount,
    (JULIANDAY(Claim_Date) - JULIANDAY(Policy_Start_Date)) AS Days_Difference
FROM v_ClaimsSummary
WHERE Claim_Date < Policy_Start_Date;

--------------------------------------------------------------------------------
-- 6. STORED PROCEDURES / PSEUDO PROCEDURES FOR TRANSACTIONAL OPERATIONS
--------------------------------------------------------------------------------

-- Procedure (T-SQL/PostgreSQL syntax example): Register New Claim and Update Status
-- In production, this runs on the transactional database to preserve ACID properties
/*
CREATE OR REPLACE PROCEDURE pr_RegisterAndValidateClaim(
    p_ClaimID VARCHAR(50),
    p_CustomerID VARCHAR(50),
    p_PolicyNumber VARCHAR(50),
    p_ClaimAmount DECIMAL(12, 2),
    p_ClaimReason VARCHAR(255),
    p_ClaimDate DATE
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_CustKey INT;
    v_PolKey INT;
    v_LocKey INT;
    v_AgtKey INT;
    v_TypeKey INT;
    v_DateKey INT;
    v_FraudFlag INT := 0;
    v_PolicyStart DATE;
BEGIN
    -- 1. Check if dates exist, fetch keys
    SELECT Customer_Key INTO v_CustKey FROM DimCustomer WHERE Customer_ID = p_CustomerID;
    SELECT Policy_Key, Policy_Start_Date INTO v_PolKey, v_PolicyStart FROM DimPolicy WHERE Policy_Number = p_PolicyNumber;
    
    -- Fetch fallback keys for simplicity
    SELECT COALESCE(MAX(Location_Key), 1) INTO v_LocKey FROM DimLocation;
    SELECT COALESCE(MAX(Agent_Key), 1) INTO v_AgtKey FROM DimAgent;
    
    -- Resolve type key (insert if not present)
    SELECT Claim_Type_Key INTO v_TypeKey FROM DimClaimType WHERE Claim_Reason = p_ClaimReason LIMIT 1;
    IF v_TypeKey IS NULL THEN
        INSERT INTO DimClaimType (Claim_Reason, Accident_Type) VALUES (p_ClaimReason, 'Unspecified') RETURNING Claim_Type_Key INTO v_TypeKey;
    END IF;
    
    -- Format date key YYYYMMDD
    v_DateKey := CAST(TO_CHAR(p_ClaimDate, 'YYYYMMDD') AS INT);
    
    -- 2. Evaluate Rule-Based Fraud Risk during ingestion
    IF p_ClaimDate < v_PolicyStart THEN
        v_FraudFlag := 1; -- Fraud: Event occurred before policy started
    END IF;
    
    -- 3. Insert new transactional claim record into Fact Table
    INSERT INTO Fact_Claims (
        Claim_ID, Customer_Key, Policy_Key, Location_Key, Agent_Key, Claim_Type_Key, Claim_Date_Key, Claim_Amount, Claim_Status, Fraud_Flag
    ) VALUES (
        p_ClaimID, v_CustKey, v_PolKey, v_LocKey, v_AgtKey, v_TypeKey, v_DateKey, p_ClaimAmount, 'Pending', v_FraudFlag
    );
    
    COMMIT;
END;
$$;
*/
