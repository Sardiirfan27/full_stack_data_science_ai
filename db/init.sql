-- ============================================
--  RESET ALL TABLES (IF EXISTS)
-- ============================================
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS contracts CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP VIEW IF EXISTS customers_summary;

-- ============================================
-- Clean up existing sequences and functions
-- ============================================
DROP SEQUENCE IF EXISTS contract_seq CASCADE;
DROP SEQUENCE IF EXISTS transaction_seq CASCADE;

DROP FUNCTION IF EXISTS generate_contract_id();
DROP FUNCTION IF EXISTS generate_transaction_id();

-- ============================================
--  CUSTOMERS TABLE
-- ============================================
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    gender VARCHAR(10),
    senior_citizen BOOLEAN,
    partner BOOLEAN,
    dependents BOOLEAN,
    signup_date DATE
);


-- =====================================================
-- SEQUENCE
-- These sequences provide unique incremental numbers
-- for contract and transaction ID generation.
-- =====================================================
CREATE SEQUENCE contract_seq START 1;
CREATE SEQUENCE transaction_seq START 1;

-- =====================================================
-- FUNCTION: generate_contract_id()
-- Purpose  : Automatically generate unique Contract IDs
-- Format   : CNT<year>-<6-digit-sequence>
-- Example  : CNT2025-000001
-- =====================================================
CREATE OR REPLACE FUNCTION generate_contract_id()
RETURNS TEXT AS $$
DECLARE
    seq_val TEXT;
BEGIN
    -- Get next sequence value and format it as a 6-digit string
    seq_val := LPAD(nextval('contract_seq')::TEXT, 6, '0');

    -- Concatenate prefix, current year, and formatted sequence
    RETURN 'CNT' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' || seq_val;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- FUNCTION: generate_transaction_id()
-- Purpose  : Automatically generate unique Transaction IDs
-- Format   : TRX<year>-<6-digit-sequence>
-- Example  : TRX2025-000001
-- =====================================================
CREATE OR REPLACE FUNCTION generate_transaction_id()
RETURNS TEXT AS $$
DECLARE
    seq_val TEXT;
BEGIN
    -- Get next sequence value and format it as a 6-digit string
    seq_val := LPAD(nextval('transaction_seq')::TEXT, 6, '0');

    -- Concatenate prefix, current year, and formatted sequence
    RETURN 'TRX' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' || seq_val;
END;
$$ LANGUAGE plpgsql;



-- ============================================
--  CONTRACTS TABLE
-- ============================================
CREATE TABLE contracts (
    contract_id TEXT PRIMARY KEY DEFAULT generate_contract_id(),
    customer_id VARCHAR(20) REFERENCES customers(customer_id),
    phone_service VARCHAR(10),       
    multiple_lines VARCHAR(30),      
    internet_service VARCHAR(20),
    online_security BOOLEAN,
    tech_support BOOLEAN,
    online_backup BOOLEAN,
    device_protection BOOLEAN,
    streaming_movies BOOLEAN,
    streaming_tv BOOLEAN,
    contract_type VARCHAR(20),
    payment_method VARCHAR(40),
    paperless_billing BOOLEAN,
    monthly_charges NUMERIC(8,2)
);

-- ============================================
--  TRANSACTIONS TABLE
-- ============================================
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY DEFAULT generate_transaction_id(),
    customer_id VARCHAR(20) REFERENCES customers(customer_id),
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    amount NUMERIC(8,2) NOT NULL,
    paid BOOLEAN DEFAULT FALSE,
    paid_date DATE
);

-- ============================================
--  INSERT CUSTOMERS (20 ENTRIES)
-- ============================================
INSERT INTO customers (customer_id, gender, senior_citizen, partner, dependents, signup_date) VALUES
('1000-VHVEG', 'Male', FALSE, TRUE, FALSE, '2025-01-10'),
('1001-HYTRS', 'Female', TRUE, FALSE, FALSE, '2025-01-15'),
('1002-KLOPQ', 'Male', FALSE, TRUE, TRUE, '2025-01-25'),
('1003-GNVDE', 'Female', FALSE, TRUE, TRUE, '2025-02-05'),
('1004-PLMXS', 'Male', FALSE, FALSE, FALSE, '2025-02-15'),
('1005-BNYTR', 'Female', TRUE, FALSE, FALSE, '2025-02-25'),
('1006-MJHGF', 'Male', FALSE, TRUE, FALSE, '2025-03-01'),
('1007-QWERT', 'Female', FALSE, TRUE, TRUE, '2025-03-05'),
('1008-ASDFG', 'Male', FALSE, FALSE, FALSE, '2025-03-15'),
('1009-ZXCVB', 'Female', TRUE, TRUE, TRUE, '2025-03-20'),
('1010-HJKLM', 'Male', FALSE, TRUE, FALSE, '2025-03-25'),
('1011-NBVFR', 'Female', TRUE, FALSE, FALSE, '2025-03-30'),
('1012-QAZWS', 'Male', FALSE, TRUE, TRUE, '2025-04-05'),
('1013-EDCRF', 'Female', FALSE, TRUE, FALSE, '2025-04-10'),
('1014-TGBHU', 'Male', FALSE, FALSE, FALSE, '2025-04-15'),
('1015-YHNJM', 'Female', TRUE, FALSE, TRUE, '2025-04-20'),
('1016-UJMKI', 'Male', FALSE, TRUE, FALSE, '2025-04-25'),
('1017-OLPWA', 'Female', FALSE, TRUE, TRUE, '2025-04-28'),
('1018-RQAZE', 'Male', FALSE, FALSE, FALSE, '2025-05-01'),
('1019-TWSXC', 'Female', TRUE, FALSE, FALSE, '2025-05-05');

-- ============================================
--  INSERT CONTRACTS (20 ENTRIES)
-- ============================================
-- 50% Month-to-month (10 customers)
INSERT INTO contracts (customer_id, phone_service, multiple_lines, internet_service, online_security, tech_support, online_backup,
                       device_protection, streaming_movies, streaming_tv, contract_type,
                       payment_method, paperless_billing, monthly_charges)
VALUES
('1000-VHVEG', 'Yes', 'Yes', 'Fiber optic', FALSE, FALSE, TRUE, TRUE, TRUE, TRUE, 'Month-to-month', 'Electronic check', TRUE, 90.00),
('1003-GNVDE', 'Yes', 'No', 'Fiber optic', FALSE, TRUE, TRUE, FALSE, TRUE, TRUE, 'Month-to-month', 'Electronic check', TRUE, 85.00),
('1004-PLMXS', 'No', 'No phone service', 'No', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, 'Month-to-month', 'Electronic check', TRUE, 20.00),
('1006-MJHGF', 'Yes', 'No', 'DSL', TRUE, TRUE, FALSE, TRUE, FALSE, FALSE, 'Month-to-month', 'Mailed check', FALSE, 50.00),
('1007-QWERT', 'Yes', 'Yes', 'Fiber optic', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 'Month-to-month', 'Credit card (automatic)', FALSE, 95.00),
('1008-ASDFG', 'Yes', 'No', 'Fiber optic', FALSE, TRUE, TRUE, TRUE, FALSE, TRUE, 'Month-to-month', 'Electronic check', TRUE, 75.00),
('1010-HJKLM', 'Yes', 'Yes', 'DSL', TRUE, FALSE, TRUE, FALSE, TRUE, FALSE, 'Month-to-month', 'Electronic check', TRUE, 60.00),
('1012-QAZWS', 'No', 'No phone service', 'No', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, 'Month-to-month', 'Electronic check', TRUE, 25.00),
('1016-UJMKI', 'Yes', 'Yes', 'Fiber optic', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 'Month-to-month', 'Credit card (automatic)', TRUE, 95.00),
('1018-RQAZE', 'Yes', 'No', 'DSL', TRUE, FALSE, FALSE, FALSE, FALSE, TRUE, 'Month-to-month', 'Electronic check', TRUE, 55.00),

-- 30% One year (6 customers)
('1001-HYTRS', 'Yes', 'No', 'DSL', TRUE, TRUE, FALSE, FALSE, TRUE, FALSE, 'One year', 'Bank transfer (automatic)', FALSE, 60.00),
('1005-BNYTR', 'Yes', 'Yes', 'Fiber optic', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 'One year', 'Credit card (automatic)', FALSE, 80.00),
('1009-ZXCVB', 'Yes', 'Yes', 'Fiber optic', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 'One year', 'Bank transfer (automatic)', FALSE, 80.00),
('1011-NBVFR', 'Yes', 'No', 'DSL', TRUE, FALSE, FALSE, FALSE, FALSE, TRUE, 'One year', 'Bank transfer (automatic)', FALSE, 50.00),
('1013-EDCRF', 'Yes', 'No', 'DSL', TRUE, TRUE, TRUE, FALSE, TRUE, FALSE, 'One year', 'Credit card (automatic)', FALSE, 60.00),
('1017-OLPWA', 'Yes', 'Yes', 'Fiber optic', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 'One year', 'Credit card (automatic)', FALSE, 80.00),

-- 20% Two year (4 customers)
('1002-KLOPQ', 'Yes', 'Yes', 'Fiber optic', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 'Two year', 'Bank transfer (automatic)', FALSE, 75.00),
('1014-TGBHU', 'Yes', 'No', 'Fiber optic', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 'Two year', 'Bank transfer (automatic)', FALSE, 75.00),
('1015-YHNJM', 'Yes', 'Yes', 'DSL', TRUE, TRUE, TRUE, TRUE, FALSE, TRUE, 'Two year', 'Bank transfer (automatic)', FALSE, 85.00),
('1019-TWSXC', 'Yes', 'Yes', 'Fiber optic', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 'Two year', 'Bank transfer (automatic)', FALSE, 75.00);

-- ============================================
--  TRANSACTIONS EXAMPLES (AUTO-GENERATED IDs)
-- ============================================
-- Month-to-month customers: Multiple monthly payments
INSERT INTO transactions (customer_id, invoice_date, due_date, amount, paid, paid_date) VALUES
('1000-VHVEG', '2025-01-10', '2025-01-11', 90.00, TRUE, '2025-01-11'),
('1000-VHVEG', '2025-02-01', '2025-02-10', 90.00, TRUE, '2025-02-09'),
('1000-VHVEG', '2025-03-01', '2025-03-10', 90.00, TRUE, '2025-03-09'),
('1000-VHVEG', '2025-04-01', '2025-04-10', 90.00, TRUE, '2025-04-08'),
('1000-VHVEG', '2025-05-01', '2025-05-10', 90.00, FALSE, NULL),

('1003-GNVDE', '2025-02-05', '2025-02-06', 85.00, TRUE, '2025-02-05'),
('1003-GNVDE', '2025-02-28', '2025-03-05', 85.00, TRUE, '2025-03-05'),
('1003-GNVDE', '2025-03-30', '2025-04-05', 85.00, TRUE, '2025-04-05'),
('1003-GNVDE', '2025-04-30', '2025-05-05', 85.00, TRUE, '2025-05-05'),
('1003-GNVDE', '2025-05-30', '2025-06-05', 85.00, FALSE, NULL),

('1004-PLMXS', '2025-02-15', '2025-02-16', 20.00, TRUE, '2025-02-16'),
('1004-PLMXS', '2025-03-10', '2025-03-15', 20.00, FALSE, NULL),

('1006-MJHGF', '2025-03-01', '2025-03-02', 50.00, TRUE, '2025-03-02'),
('1006-MJHGF', '2025-03-25', '2025-04-01', 50.00, FALSE, NULL),

('1007-QWERT', '2025-03-05', '2025-03-06', 95.00, TRUE, '2025-03-06'),
('1007-QWERT', '2025-03-28', '2025-04-05', 95.00, FALSE, NULL),

('1008-ASDFG', '2025-03-15', '2025-03-16', 75.00, TRUE, '2025-03-16'),
('1008-ASDFG', '2025-04-10', '2025-04-15', 75.00, FALSE, NULL),

('1010-HJKLM', '2025-02-25', '2025-02-26', 60.00, TRUE, '2025-02-25'),
('1010-HJKLM', '2025-03-20', '2025-03-25', 60.00, TRUE, '2025-03-25'),
('1010-HJKLM', '2025-04-20', '2025-04-25', 60.00, TRUE, '2025-04-25'),
('1010-HJKLM', '2025-05-20', '2025-05-25', 60.00, FALSE, NULL),

('1012-QAZWS', '2025-04-05', '2025-04-06', 25.00, TRUE, '2025-04-06'),
('1012-QAZWS', '2025-04-28', '2025-05-05', 25.00, FALSE, NULL),

('1016-UJMKI', '2025-04-25', '2025-04-26', 95.00, TRUE, '2025-04-25'),
('1016-UJMKI', '2025-05-20', '2025-06-25', 95.00, FALSE, NULL),

('1018-RQAZE', '2025-05-01', '2025-05-02', 55.00, TRUE, '2025-05-02'),
('1018-RQAZE', '2025-05-27', '2025-06-01', 55.00, FALSE, NULL);


--  One-year contract customers: Annual billing
INSERT INTO transactions (customer_id, invoice_date, due_date, amount, paid, paid_date) VALUES
('1001-HYTRS', '2025-01-15', '2025-01-16', 60.00 * 12, TRUE, '2025-01-15'),
('1005-BNYTR', '2025-02-25', '2025-02-26', 80.00 * 12, TRUE, '2025-02-25'),
('1009-ZXCVB', '2025-03-20', '2025-03-21', 80.00 * 12, TRUE, '2025-03-21'),
('1011-NBVFR', '2025-03-30', '2025-04-01', 50.00 * 12, TRUE, '2025-03-31'),
('1013-EDCRF', '2025-04-10', '2025-04-11', 60.00 * 12, TRUE, '2025-04-10'),
('1017-OLPWA', '2025-04-28', '2025-04-29', 80.00 * 12, TRUE, '2025-04-29');

--  Two-year contract customers: Biennial billing
INSERT INTO transactions (customer_id, invoice_date, due_date, amount, paid, paid_date) VALUES
('1002-KLOPQ', '2025-01-25', '2025-01-26', 75.00 * 24, TRUE, '2025-01-25'),
('1014-TGBHU', '2025-04-15', '2025-04-16', 75.00 * 24, TRUE, '2025-04-15'),
('1015-YHNJM', '2025-04-20', '2025-04-21', 85.00 * 24, TRUE, '2025-04-20'),
('1019-TWSXC', '2025-05-05', '2025-05-06', 75.00 * 24, TRUE, '2025-05-05');


-- =====================================================
-- Add the last_updated column to the customers table
-- =====================================================
ALTER TABLE customers
ADD COLUMN last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW();

-- Create the TRIGGER function to automatically update the last_updated column
CREATE OR REPLACE FUNCTION update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
   -- Set the last_updated column for the new row to the current timestamp
   NEW.last_updated = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';


-- Apply the TRIGGER to the customers table (for both INSERT and UPDATE)
CREATE TRIGGER last_updated_trigger
BEFORE UPDATE OR INSERT ON customers
FOR EACH ROW
EXECUTE PROCEDURE update_last_updated_column();


-- =====================================================
-- Add the last_updated column to the contracts table
-- =====================================================
ALTER TABLE contracts
ADD COLUMN last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW();

-- Apply the same TRIGGER function to the contracts table
CREATE TRIGGER contracts_last_updated_trigger
BEFORE UPDATE OR INSERT ON contracts
FOR EACH ROW
EXECUTE PROCEDURE update_last_updated_column();



-- ====================================================
-- Create the customers_status view
-- ====================================================

CREATE OR REPLACE VIEW customers_status AS
WITH latest_transaction AS (
    -- Identify the absolute latest transaction for each customer
    SELECT
        customer_id,
        due_date AS latest_due_date,
        paid AS latest_paid_status,
        paid_date AS latest_paid_date,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY due_date DESC, invoice_date DESC
        ) AS rn
    FROM transactions
)
SELECT
    c.customer_id,
    con.contract_type,
    lt.latest_due_date AS last_due_date,
    lt.latest_paid_date AS last_paid_date,
    
    -- Churn Logic: True if the latest transaction (for any contract type) is FALSE and overdue by > 60 days
    CASE
        WHEN lt.latest_paid_status = FALSE
             AND lt.latest_due_date IS NOT NULL 
             AND (CURRENT_DATE - lt.latest_due_date) > 60 THEN 'Yes'
             
        ELSE 'No'
    END AS churn
        
FROM customers c
JOIN contracts con ON c.customer_id = con.customer_id
-- Only join the latest transaction (rn = 1)
LEFT JOIN latest_transaction lt ON c.customer_id = lt.customer_id AND lt.rn = 1
ORDER BY c.customer_id;



