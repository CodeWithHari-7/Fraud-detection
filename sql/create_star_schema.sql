-- SQL Script to Create Star Schema Tables, Constraints, and Indexes
-- Target Databases: PostgreSQL / SQLite / SQL Server / MySQL (Standard ANSI SQL)

-- 1. Dimension Tables

CREATE TABLE DimCustomer (
    Customer_Key INTEGER PRIMARY KEY AUTOINCREMENT,
    Customer_ID VARCHAR(50) NOT NULL,
    Customer_Name VARCHAR(100) NOT NULL,
    Customer_Age INTEGER,
    Customer_Gender VARCHAR(20),
    Customer_Income DECIMAL(12, 2)
);

CREATE TABLE DimPolicy (
    Policy_Key INTEGER PRIMARY KEY AUTOINCREMENT,
    Policy_Number VARCHAR(50) NOT NULL,
    Policy_Type VARCHAR(50) NOT NULL,
    Policy_Premium DECIMAL(10, 2),
    Policy_Start_Date DATE,
    Policy_End_Date DATE
);

CREATE TABLE DimLocation (
    Location_Key INTEGER PRIMARY KEY AUTOINCREMENT,
    City VARCHAR(100),
    State VARCHAR(10),
    Zipcode VARCHAR(20)
);

CREATE TABLE DimAgent (
    Agent_Key INTEGER PRIMARY KEY AUTOINCREMENT,
    Agent_ID VARCHAR(50) NOT NULL,
    Agent_Name VARCHAR(100) NOT NULL
);

CREATE TABLE DimClaimType (
    Claim_Type_Key INTEGER PRIMARY KEY AUTOINCREMENT,
    Claim_Reason VARCHAR(255),
    Accident_Type VARCHAR(100)
);

CREATE TABLE DimDate (
    Date_Key INTEGER PRIMARY KEY, -- Formatted as YYYYMMDD
    Full_Date DATE NOT NULL,
    Year INTEGER NOT NULL,
    Quarter INTEGER NOT NULL,
    Month INTEGER NOT NULL,
    Month_Name VARCHAR(20) NOT NULL,
    Day INTEGER NOT NULL,
    Day_Of_Week INTEGER NOT NULL,
    Day_Name VARCHAR(20) NOT NULL,
    Is_Weekend INTEGER NOT NULL -- 0 or 1
);

-- 2. Fact Table

CREATE TABLE Fact_Claims (
    Claim_Key INTEGER PRIMARY KEY AUTOINCREMENT,
    Claim_ID VARCHAR(50) NOT NULL,
    Customer_Key INTEGER NOT NULL,
    Policy_Key INTEGER NOT NULL,
    Location_Key INTEGER NOT NULL,
    Agent_Key INTEGER NOT NULL,
    Claim_Type_Key INTEGER NOT NULL,
    Claim_Date_Key INTEGER NOT NULL,
    Claim_Amount DECIMAL(12, 2),
    Claim_Status VARCHAR(50),
    Fraud_Flag INTEGER DEFAULT 0,
    FOREIGN KEY (Customer_Key) REFERENCES DimCustomer(Customer_Key),
    FOREIGN KEY (Policy_Key) REFERENCES DimPolicy(Policy_Key),
    FOREIGN KEY (Location_Key) REFERENCES DimLocation(Location_Key),
    FOREIGN KEY (Agent_Key) REFERENCES DimAgent(Agent_Key),
    FOREIGN KEY (Claim_Type_Key) REFERENCES DimClaimType(Claim_Type_Key),
    FOREIGN KEY (Claim_Date_Key) REFERENCES DimDate(Date_Key)
);

-- 3. Indexes for Performance Tuning

-- Indexes on Business Keys
CREATE UNIQUE INDEX idx_dim_cust_id ON DimCustomer(Customer_ID);
CREATE INDEX idx_dim_pol_num ON DimPolicy(Policy_Number);
CREATE INDEX idx_fact_claim_id ON Fact_Claims(Claim_ID);

-- Indexes on Foreign Keys in Fact Table
CREATE INDEX idx_fact_cust_key ON Fact_Claims(Customer_Key);
CREATE INDEX idx_fact_pol_key ON Fact_Claims(Policy_Key);
CREATE INDEX idx_fact_loc_key ON Fact_Claims(Location_Key);
CREATE INDEX idx_fact_agt_key ON Fact_Claims(Agent_Key);
CREATE INDEX idx_fact_claim_type_key ON Fact_Claims(Claim_Type_Key);
CREATE INDEX idx_fact_date_key ON Fact_Claims(Claim_Date_Key);

-- Indexes for Analytical Queries
CREATE INDEX idx_fact_fraud ON Fact_Claims(Fraud_Flag);
CREATE INDEX idx_fact_status ON Fact_Claims(Claim_Status);
CREATE INDEX idx_dim_pol_type ON DimPolicy(Policy_Type);
CREATE INDEX idx_dim_loc_state ON DimLocation(State);
