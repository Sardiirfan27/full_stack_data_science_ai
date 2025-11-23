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



