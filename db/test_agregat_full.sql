SELECT
    c.customer_id AS "customerID",
    c.gender AS "gender",
    c.senior_citizen AS "SeniorCitizen",
    c.partner AS "Partner",
    c.dependents AS "Dependents",
        --  Calculate tenure in months
    CASE
        WHEN con.contract_type = 'Month-to-month' THEN 
            COUNT(CASE WHEN t.paid = TRUE THEN 1 END)
        WHEN con.contract_type = 'One year' THEN 
            12
        WHEN con.contract_type = 'Two year' THEN 
            24
        ELSE 0
    END::INT AS "tenure",

    con.phone_service AS "PhoneService",
    con.multiple_lines AS "MultipleLines",
    con.internet_service AS "InternetService",
    con.online_security AS "OnlineSecurity",
    con.online_backup AS "OnlineBackup",
    con.device_protection AS "DeviceProtection",
    con.tech_support AS "TechSupport",
    con.streaming_tv AS "StreamingTV",
    con.streaming_movies AS "StreamingMovies",
    con.contract_type AS "Contract",
    con.paperless_billing AS "PaperlessBilling",
    con.payment_method AS "PaymentMethod",
    con.monthly_charges AS "MonthlyCharges",
    
    -- Sum only the amounts of transactions that are paid
    SUM(CASE WHEN t.paid = TRUE THEN t.amount ELSE 0 END)::NUMERIC AS "TotalCharges",

    -- COALESCE handles customers without transactions/status
    COALESCE(cs.churn, 'No') AS "Churn"

FROM customers c
-- Join churn label from the view (customers_status)
JOIN contracts con 
    ON c.customer_id = con.customer_id
LEFT JOIN transactions t 
    ON c.customer_id = t.customer_id
LEFT JOIN customers_status cs
    ON c.customer_id = cs.customer_id

GROUP BY 
    c.customer_id, c.gender, c.senior_citizen, c.partner, c.dependents,
    con.phone_service, con.multiple_lines,  
    con.internet_service, con.online_security, con.tech_support, con.online_backup,
    con.device_protection, con.streaming_movies, con.streaming_tv,
    con.contract_type, con.payment_method, con.paperless_billing, con.monthly_charges,
    cs.churn

ORDER BY c.customer_id;